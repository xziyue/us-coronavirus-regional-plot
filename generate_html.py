import subprocess
from io import StringIO
import sys
from graph_data import *
from ansi2html import Ansi2HTMLConverter
import re

old_stdout = sys.stdout
stdout_io = StringIO()
sys.stdout = stdout_io

get_offline_data()  # debug only
#get_online_data()
std_dates = get_standardize_dates()
change_data_interpolation_type('slinear')

filename_dict = dict()

def generate_and_save_daily_increment_graph():
    daily_case_increment = get_daily_case_increment(std_dates)
    daily_case_increment_region_grouped = group_by_region(daily_case_increment)
    daily_case_increment_region_sum = sum_keys(daily_case_increment_region_grouped)

    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    graph_daily_increment(ax, std_dates, daily_case_increment_region_sum)
    #ax.set_title('Number of Positive Per Day by Region')
    fig.tight_layout()
    plt.legend(loc='upper center')

    filename_dict['daily_positive'] = 'num_positive_per_day.svg'
    fig.savefig('./us-coronavirus-regional-plot/num_positive_per_day.svg', bbox_inches='tight')
    plt.close()

    print(colored('finished generating num positive per day graph', 'green'))


def generate_and_save_total_tests_graph():
    targets = get_state_data_by_method_name(std_dates, 'get_num_tested')
    targets_grouped = group_by_region(targets)
    targets_sum = sum_keys(targets_grouped)

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates, targets_sum)
    #fig.suptitle('Number of Tests by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/num_test.svg')
    plt.close()

    filename_dict['test'] = 'num_test.svg'
    print(colored('finished generating num test graph', 'green'))

def generate_and_save_daily_tests_graph():
    targets = get_daily_diff(std_dates, 'get_num_tested')
    targets_grouped = group_by_region(targets)
    targets_sum = sum_keys(targets_grouped)

    valid_dates = std_dates[1:]

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, valid_dates, targets_sum)
    #fig.suptitle('Number of Tests Per Day by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/num_test_per_day.svg')
    plt.close()

    filename_dict['daily_test'] = 'num_test_per_day.svg'
    print(colored('finished generating num test per day graph', 'green'))

def generate_and_save_positive_graph():
    targets = get_state_data_by_method_name(std_dates, 'get_num_positive')
    targets_grouped = group_by_region(targets)
    targets_sum = sum_keys(targets_grouped)

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates, targets_sum)
    #fig.suptitle('Number of Positives by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/num_positive.svg')
    plt.close()

    filename_dict['positive'] = 'num_positive.svg'
    print(colored('finished generating num of positive graph', 'green'))

def generate_and_save_death_graph():
    targets = get_state_data_by_method_name(std_dates, 'get_num_death')
    targets_grouped = group_by_region(targets)
    targets_sum = sum_keys(targets_grouped)

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates, targets_sum)
    #fig.suptitle('Number of Deaths by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/num_death.svg')
    plt.close()

    filename_dict['death'] = 'num_death.svg'
    print(colored('finished generating num of death graph', 'green'))

def generate_and_save_daily_death_graph():
    targets = get_daily_diff(std_dates, 'get_num_death')
    targets_grouped = group_by_region(targets)
    targets_sum = sum_keys(targets_grouped)

    valid_dates = std_dates[1:]

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, valid_dates, targets_sum)
    #fig.suptitle('Number of Deaths Per Day by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/num_death_per_day.svg')
    plt.close()

    filename_dict['daily_death'] = 'num_death_per_day.svg'
    print(colored('finished generating num death per day graph', 'green'))

def generate_and_save_death_rate_graph():
    seq1 = get_state_data_by_method_name(std_dates, 'get_num_death')
    seq1_grouped = group_by_region(seq1)
    seq1_sum = sum_keys(seq1_grouped)

    seq2 = get_state_data_by_method_name(std_dates, 'get_num_positive')
    seq2_goruped = group_by_region(seq2)
    seq2_sum = sum_keys(seq2_goruped)

    new_data = dict()
    for key in seq1_sum.keys():
        data1 = seq1_sum[key]
        data2 = seq2_sum[key]
        data3 = data1.astype(np.float) / data2.astype(np.float)
        new_data[key] = data3

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates, new_data)
    #fig.suptitle('Cumulative Death Rate by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/death_rate.svg')
    plt.close()

    filename_dict['death_rate'] = 'death_rate.svg'
    print(colored('finished generating death rate graph', 'green'))


def generate_and_save_cumulative_positive_rate_graph():
    seq1 = get_state_data_by_method_name(std_dates, 'get_num_positive')
    seq1_grouped = group_by_region(seq1)
    seq1_sum = sum_keys(seq1_grouped)

    seq2 = get_state_data_by_method_name(std_dates, 'get_num_tested')
    seq2_goruped = group_by_region(seq2)
    seq2_sum = sum_keys(seq2_goruped)

    new_data = dict()
    for key in seq1_sum.keys():
        data1 = seq1_sum[key]
        data2 = seq2_sum[key]
        data3 = data1.astype(np.float) / data2.astype(np.float)
        new_data[key] = data3

    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates, new_data)
    #fig.suptitle('Cumulative Positive Rate by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/positive_rate.svg')
    plt.close()

    filename_dict['positive_rate'] = 'positive_rate.svg'
    print(colored('finished generating positive rate graph', 'green'))

def generate_and_save_daily_positive_rate_graph():
    seq1 = get_daily_diff(std_dates, 'get_num_positive')
    seq1_grouped = group_by_region(seq1)
    seq1_sum = sum_keys(seq1_grouped)

    seq2 = get_daily_diff(std_dates, 'get_num_tested')
    seq2_goruped = group_by_region(seq2)
    seq2_sum = sum_keys(seq2_goruped)

    new_data = dict()
    for key in seq1_sum.keys():
        data1 = seq1_sum[key]
        data2 = seq2_sum[key]

        denom = data2.astype(np.float)
        denom[np.abs(denom) < 1.0e-3] = np.nan
        data3 = data1.astype(np.float) / denom
        data3[np.isnan(data3)] = 0.0 # fill missing values with 0

        new_data[key] = data3



    fig, axs = plt.subplots(2, 2, figsize=(12, 9), sharex='all', sharey='all')
    graph_four_region_layout(axs, std_dates[1:], new_data)
    #fig.suptitle('Positive Rate Per Day by Region')
    fig.tight_layout()
    fig.savefig('./us-coronavirus-regional-plot/positive_rate_per_day.svg')
    plt.close()

    filename_dict['daily_positive_rate'] = 'positive_rate_per_day.svg'
    print(colored('finished generating daily positive rate graph', 'green'))


generate_and_save_daily_increment_graph()
generate_and_save_total_tests_graph()
generate_and_save_daily_tests_graph()
generate_and_save_positive_graph()
generate_and_save_death_graph()
generate_and_save_daily_death_graph()
generate_and_save_death_rate_graph()
generate_and_save_cumulative_positive_rate_graph()
generate_and_save_daily_positive_rate_graph()

now_time = datetime.now()
cprint('graph saved to file (latest update time: {})'.format(now_time.isoformat()), attrs=['bold'])
sys.stdout = old_stdout

stdout_io.seek(0)
previous_io = stdout_io.read()
print(previous_io)
converter = Ansi2HTMLConverter()
previous_io_html = '\n\n<pre>\n' + converter.convert(previous_io, full=False) + '</pre>\n\n'
previous_io_html_css = converter.produce_headers()
stdout_html = '\n'.join([previous_io_html_css, previous_io_html])

def get_img_tag(filename):
    path_prefix = '/us-coronavirus-regional-plot/'
    return '\n\n<div>\n<img src="{}">\n</div>\n\n'.format(path_prefix + filename)


with open('template.html', 'r') as infile:
    html_data = infile.read()

sub_re = re.compile(r'<p><span>%%(.*?)%%<\/span><\/p>')

pos = 0
while pos < len(html_data):
    next_match = sub_re.search(html_data, pos)

    if next_match is None:
        break

    kw = next_match.group(1)
    if kw == 'stdout':
        sub_str = stdout_html
    else:
        sub_str = get_img_tag(filename_dict[kw])

    f = html_data[:next_match.start()]
    b = html_data[next_match.end():]
    html_data = f + sub_str + b
    pos = next_match.start() + len(sub_str)

with open('./us-coronavirus-regional-plot/index.html', 'w') as outfile:
    outfile.write(html_data)
