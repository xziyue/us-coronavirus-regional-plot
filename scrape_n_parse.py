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

        self.x_shift = self.x[0]

        self._create_functions()

    def _create_functions(self, **kwargs):
        x_shifted = self.x - self.x_shift
        self.interp_funcs = []
        for col_id in range(1, self.matrix.shape[1]):
            self.interp_funcs.append(interp1d(x_shifted, self.matrix[:, col_id], fill_value='extrapolate', **kwargs))

    def get_earliest(self):
        return self.x_dt[0]

    def get_latest(self):
        return self.x_dt[-1]

    def _get_interpolated(self, tp, func_id):
        if isinstance(tp, np.datetime64):
            tp = tp.astype(datetime).timestamp()
        elif isinstance(tp, datetime):
            tp = tp.timestamp()
        return self.interp_funcs[func_id](tp - self.x_shift)

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