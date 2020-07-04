import pandas
from http import HTTPStatus
from urllib.request import urlopen
from termcolor import colored
from io import BytesIO
import numpy as np
from scipy.interpolate import interp1d
import pickle
from datetime import datetime, date

class CoronavirusInfo:

    def __init__(self, df):
        self.df = df
        self.matrix = np.asarray(df.iloc[:, :], np.int)

        self.x = self.matrix[:, 0]
        self.x_dt = [np.datetime64(datetime.utcfromtimestamp(tp)) for tp in self.x]

        for i in range(1, self.matrix.shape[1]):
            col = self._preprocess_column(self.matrix[:, i])
            self.matrix[:, i] = col

        self._create_functions()

    # we assume that coronavirus cases is always increasing/decreasing
    # therefore, for better visualization, we interpolate consecutive days with same data
    def _preprocess_column(self, col):

        new_col = col.copy().astype(np.float)

        pos = 0

        while pos < col.size:
            pos_val = col[pos]
            next_pos = pos + 1

            while next_pos < col.size:
                if abs(col[next_pos] - pos_val) > 1.0e-3:
                    break
                next_pos += 1

            if next_pos == pos + 1:
                pos += 1
            else:
                left = max(0, pos - 1)
                right = min(col.size - 1, next_pos + 1)
                if left == 0 and right == col.size - 1:
                    print(colored('problematic interpolation', 'red'))
                tr_x = (self.x[left], self.x[right])
                tr_y = (col[left], col[right])
                func = interp1d(tr_x, tr_y)
                new_value = func(self.x[pos : next_pos])
                new_col[pos : next_pos] = new_value
                pos = next_pos + 1

        return new_col

    def _create_functions(self, **kwargs):
        self.interp_funcs = []
        for col_id in range(1, self.matrix.shape[1]):
            self.interp_funcs.append(interp1d(self.x, self.matrix[:, col_id], fill_value='extrapolate', **kwargs))

    def get_earliest(self):
        return self.x_dt[0]

    def get_latest(self):
        return self.x_dt[-1]

    def _get_interpolated(self, tp, func_id):
        if isinstance(tp, np.datetime64):
            tp = tp.astype(datetime).timestamp()
        elif isinstance(tp, datetime):
            tp = tp.timestamp()

        '''
        search_slot = np.searchsorted(self.x, tp, 'right') - 1
        if search_slot < 0:
            search_slot = 0
        elif search_slot >= self.matrix.shape[0]:
            search_slot = self.matrix.shape[0] - 1

        return self.matrix[search_slot, func_id]
        '''

        #previous method, deprecated
        return self.interp_funcs[func_id](tp)

    def get_num_tested(self, tp):
        return self._get_interpolated(tp, 0)

    def get_num_positive(self, tp):
        return self._get_interpolated(tp ,1)

    def get_num_death(self, tp):
        return self._get_interpolated(tp, 2)

def get_state_data_coronavirus_api(item):
    api_url = 'http://coronavirusapi.com/getTimeSeries/{}'.format(item['state_code'])
    response = urlopen(api_url)

    if response.status != HTTPStatus.OK:
        description = HTTPStatus(response.status).description
        raise RuntimeError('unable to fetch data form coronavirus api (HTTP error code {})\n'
                           'Detail: {}'.format(response.status, description))

    csv_data = response.read()
    csv_io = BytesIO()
    csv_io.write(csv_data)
    csv_io.seek(0)

    df = pandas.read_csv(csv_io)
    return CoronavirusInfo(df)


def gather_all_states_data(api_call=get_state_data_coronavirus_api):
    states_df = pandas.read_csv('us-states.csv')

    ret = []

    print(colored('gathering information for all US states...', 'green'))

    for ind in range(states_df.shape[0]):
        state, state_code, region, division = states_df.iloc[ind, :]

        item = {
            'state' : state,
            'state_code' : state_code,
            'region' : region,
            'division' : division
        }
        corona_info = None

        try:
            corona_info = api_call(item)
        except Exception as e:
            print(colored(e, 'red'))
            print(colored('unable to gather data from all states','red'))
            raise e

        print(colored('{}({})'.format(state_code, corona_info.x.shape[0]), 'cyan'), end=' ')
        if (ind + 1) % 5 == 0:
            print('')

        item['corona_info'] = corona_info
        ret.append(item)

    return ret


if __name__ == '__main__':
    states_data = gather_all_states_data()
    with open('states_data.bin', 'wb') as outfile:
        pickle.dump(states_data, outfile)