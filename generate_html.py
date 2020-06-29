import subprocess
from io import StringIO
import sys
from graph_data import *
from ansi2html import Ansi2HTMLConverter
import base64

def generate_and_save_graph():
    #get_offline_data() # debug only
    get_online_data()
    change_data_interpolation_type('slinear')
    std_dates = get_standardize_dates()
    daily_case_increment = get_daily_case_increment(std_dates)
    daily_case_increment_region_grouped = group_by_region(daily_case_increment)
    daily_case_increment_region_sum = sum_keys(daily_case_increment_region_grouped)

    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    graph_daily_increment(ax, std_dates, daily_case_increment_region_sum)
    ax.set_title('US Coronavirus Daily Increase by Region')
    plt.tight_layout()
    plt.legend(loc='upper center')
    plt.savefig('graph.svg', bbox_inches='tight')

old_stdout = sys.stdout
stdout_io = StringIO()
sys.stdout = stdout_io

generate_and_save_graph()
now_time = datetime.now()
cprint('graph saved to file (latest update time: {})'.format(now_time.isoformat()), attrs=['bold'])
sys.stdout = old_stdout

stdout_io.seek(0)
previous_io = stdout_io.read()
print(previous_io)
converter = Ansi2HTMLConverter()
previous_io_html = '<pre>\n' + converter.convert(previous_io, full=False) + '</pre>'
previous_io_html_css = converter.produce_headers()

# process graph
with open('graph.svg', 'rb') as infile:
    svg_data = infile.read()

svg_b64 = base64.b64encode(svg_data).decode('utf8')
image_data = r'''<div style="text-align:center;">
<img src="data:image/svg+xml;base64,{}" >
</div>
'''.format(svg_b64)


with open('template.html', 'r') as infile:
    html_data = infile.read()

html_data = html_data.replace('%%%%img', image_data)
html_data = html_data.replace('%%%%stdout', '\n'.join([previous_io_html_css, previous_io_html]))

with open('output.html', 'w') as outfile:
    outfile.write(html_data)
