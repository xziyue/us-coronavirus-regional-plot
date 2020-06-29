from scrape_n_parse import CoronavirusInfo, gather_all_states_data
import pickle
from termcolor import colored, cprint
import numpy as np
from datetime import datetime, timedelta, time
import pandas
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator
from matplotlib.dates import DateFormatter
import os

states_df = pandas.read_csv('us-states.csv')

data = None

def get_offline_data(ignored_state_codes = tuple()):
    global data
    stat = os.stat('states_data.bin')
    mtime = datetime.fromtimestamp(stat.st_mtime)
    print(colored('using local data (last modified: {})'.format(mtime.isoformat()), 'green'))

    with open('states_data.bin', 'rb') as infile:
        data = pickle.load(infile)

    ret = []
    for item in data:
        if item['state_code'] not in ignored_state_codes:
            ret.append(item)

    data = ret

def get_online_data(ignored_state_codes = tuple()):
    global data
    now_time = datetime.now()
    print(colored('fetching latest data (now time: {})'.format(now_time.isoformat()), 'green'))
    data = gather_all_states_data()

    ret = []
    for item in data:
        if item['state_code'] not in ignored_state_codes:
            ret.append(item)

    data = ret


def change_data_interpolation_type(new_type):
    for item in data:
        item['corona_info']._create_functions(kind=new_type)

def inspect_state_dates():
    for ind, item in enumerate(data):
        state = item['state']
        corona_info = item['corona_info']
        print(ind + 1, state, corona_info.get_earliest(), corona_info.get_latest(), sep='\t')

# get standardized date
def get_standardize_dates(**kwargs):

    step_size = kwargs.get('step_size', 1)
    use_last_end_date = kwargs.get('use_last_end_date', False)

    start_date = data[0]['corona_info'].get_earliest()
    start_state = data[0]['state']

    end_date = data[0]['corona_info'].get_latest()
    end_state = data[0]['state']


    for item in data:

        corona_info = item['corona_info']
        if corona_info.get_earliest() > start_date:
            start_date = corona_info.get_earliest()
            start_state = item['state']

        if use_last_end_date:
            if corona_info.get_latest() > end_date:
                end_date = corona_info.get_latest()
                end_state = item['state']
        else:
            if corona_info.get_latest() < end_date:
                end_date = corona_info.get_latest()
                end_state = item['state']

    print(colored('the last state to start reporting result is {} ({})'.format(start_state, start_date), 'cyan'))

    if use_last_end_date:
        print(colored('the lastest state to update result is {} ({})'.format(end_state, end_date), 'cyan'))
    else:
        print(colored('the earliest state to update result is {} ({})'.format(end_state, end_date), 'cyan'))

    day_step = timedelta(days=step_size)

    start_day = datetime.combine(start_date.astype(datetime).date(), time())
    end_day = datetime.combine(end_date.astype(datetime).date(), time())


    now_day = start_day
    ret = []
    while now_day <= end_day:
        ret.append(np.datetime64(now_day))
        now_day += day_step

    print(colored('standardized start date: {}'.format(ret[0]), 'green'))
    print(colored('standardized end date: {}'.format(ret[-1]), 'green'))

    return np.asarray(ret)


def get_daily_case_increment(std_dates):
    ret = dict()
    for item in data:
        corona_info = item['corona_info']
        daily_cases = [corona_info.get_num_positive(tp) for tp in std_dates]
        ret[item['state_code']] = np.diff(daily_cases)

    return ret


def group_by_region(inter_data):
    code_to_region = dict()
    for ind in range(states_df.shape[0]):
        # build state to region dict
        code_to_region[states_df.iloc[ind, 1]] = states_df.iloc[ind, 2]

    all_regions = set(states_df.iloc[:, 2])

    ret = dict()
    for region in all_regions:
        ret[region] = []

    for key, val in inter_data.items():
        ret[code_to_region[key]].append(val)

    return ret


def sum_keys(inter_data, axis=0):
    ret = dict()
    for key, val in inter_data.items():
        ret[key] = np.sum(val, axis=axis)

    return ret


def graph_daily_increment(ax, std_dates, key_sum):

    kv = []

    for key, val in key_sum.items():
        assert val.shape[0] == len(std_dates) - 1
        kv.append((key, val))

    kv.sort(key=lambda x : x[0])
    ks, vs = zip(*kv)

    valid_dates = std_dates[1:]
    ax.set_xlim((valid_dates[0], valid_dates[-1]))
    ax.get_xaxis().set_major_locator(LinearLocator(numticks=12))
    ax.get_xaxis().set_major_formatter(DateFormatter('%Y-%m-%d'))

    ax.stackplot(valid_dates, vs, labels=ks)
    ax.xaxis.set_tick_params(rotation=90)


if __name__ == '__main__':
    #inspect_state_dates()
    pass
