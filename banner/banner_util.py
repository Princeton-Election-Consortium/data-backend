from datetime import datetime, timedelta
import csv
import os
from decimal import *

YEAR = 2024

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

MATLAB_OUTPUTS_DIR = '../matlab/outputs/'
EV_JERSEYVOTES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'EV_jerseyvotes_{YEAR}.csv')
SENATE_JERSEYVOTES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'Senate_jerseyvotes_{YEAR}.csv')
EV_ESTIMATES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'EV_estimates_{YEAR}.csv')
SENATE_ESTIMATES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'Senate_estimates_{YEAR}.csv')

SCRAPING_OUTPUTS_DIR = '../scraping/outputs'
HOUSE_POLLS_CSV = os.path.join(DIR_PATH, SCRAPING_OUTPUTS_DIR, f'{YEAR}.house.polls.median.csv')

# ======================================================================

def get_estimates(path, dict_csv=False):
    estimates = None
    with open(path, 'r') as est_file:
        reader = csv.reader(est_file)
        if dict_csv:
            reader = csv.DictReader(est_file)
        # only one line
        for row in reader:
            estimates = row
            break
    return estimates

def get_pres_moneyball_states(n):
    pres_string = ""
    read = 0

    with open(EV_JERSEYVOTES_CSV, 'r') as f:
        reader = csv.reader(f)
        for row in reader: 
            if read == n:
                return pres_string
            if read == n - 1:
                if row[1] == 'M2':
                    pres_string += 'ME-2'
                elif row[1] == 'N2':
                    pres_string += 'NE-2'
                else:
                    pres_string += row[1]
            else:
                if row[1] == 'M2':
                    pres_string += 'ME-2' + " "
                elif row[1] == 'N2':
                    pres_string += 'NE-2' + " "
                else:
                    pres_string += row[1] + " "
            read += 1
    
    return pres_string

def get_sen_moneyball_states(n):
    sen_string = ""
    read = 0

    with open(SENATE_JERSEYVOTES_CSV, 'r') as f:
        reader = csv.reader(f)
        for row in reader: 
            if read == n:
                return sen_string
            if read == n - 1:
                sen_string += row[1]
            else:
                sen_string += row[1] + " "
            read += 1
    
    return sen_string


def main():
    estimates = get_estimates(EV_ESTIMATES_CSV)
    ev_rep = int(estimates[1])
    ev_dem = int(estimates[0])

    ev_metamargin = Decimal(estimates[12]).quantize(Decimal('0.1'))

    ev_ahead_str = 'D+'
    if ev_metamargin < 0:
        ev_ahead_str = 'R+'

    estimates = get_estimates(SENATE_ESTIMATES_CSV)
    sen_seats_dem = int(estimates[0])
    sen_seats_rep = 100 - sen_seats_dem
    sen_metamargin = Decimal(estimates[-1]).quantize(Decimal('0.1'))

    sen_ahead_str = 'D+'
    if sen_metamargin < 0:
        sen_ahead_str = 'R+'
    elif sen_metamargin == 0:
        sen_ahead_str  = 'Tie'

    estimates = get_estimates(HOUSE_POLLS_CSV, dict_csv=True)
    gen_metamargin = (Decimal(estimates['median_margin']) - 2).quantize(Decimal('0.1'))
    print(estimates['median_margin'])
    gen_polling = (Decimal(estimates['median_margin'])).quantize(Decimal('0.1'))

    gen_ahead_str = 'D+'
    if gen_metamargin < 0:
        gen_ahead_str = 'R+'
    elif gen_metamargin == 0:
        gen_ahead_str = 'Tie'

    gen_polling_ahead_str = 'D+'
    if gen_polling < 0:
        gen_polling_ahead_str = 'R+'
    elif gen_polling == 0:
        gen_polling_ahead_str = 'Tie'

    weekday_num = datetime.now().date().weekday()
    past_sunday = datetime.now() + timedelta(days=-weekday_num)
    end_of_week = past_sunday + timedelta(days=6)
    weekstartnum = past_sunday.strftime("%d")
    weekendnum = end_of_week.strftime("%d")

#     datestring = ''
#     if past_sunday.month != end_of_week.month:
#         start_month = past_sunday.strftime("%b")
#         end_month = end_of_week.strftime("%b")
#         datestring = f'{start_month} {weekstartnum} - {end_month} {weekendnum}, 2022'
#     else:
#         month = past_sunday.strftime("%b")
#         datestring = f'{month} {weekstartnum}-{weekendnum}, 2022'
    
#     datestring = datetime.now().strftime("%b %d")

    ev_mm_str = f'{ev_ahead_str}{abs(ev_metamargin)}%'
    sen_mm_str = f'{sen_ahead_str}{abs(sen_metamargin)}%'
    gen_mm_str = f'{gen_ahead_str}{abs(gen_metamargin)}%'
    gen_poll_mm_str = f'{gen_polling_ahead_str}{abs(gen_polling)}%'
    dem_seats = f'{sen_seats_dem}{" Dem"}'
    rep_seats = f'{sen_seats_rep}{" Rep"}'

    pres_moneyball_states = get_pres_moneyball_states(3)
    sen_moneyball_states = get_sen_moneyball_states(3)

    banner = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> Senate: {dem_seats} | {rep_seats} (range: 47-52) Control: ({sen_mm_str}) from toss-up</span>
        <br>
        <span>  <a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House</a> Generic polling: {gen_poll_mm_str} Control {gen_mm_str}</span>
        <br>
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_moneyball_states}, Governor/SoS: NV AZ Supreme Courts: OH NC</span>
    </div>
    """

    banner_table = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <table>
            <tr><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> Senate: {dem_seats} | {rep_seats}  (range: 47-52) Control: ({sen_mm_str}) from toss-up<</tr>
            <br>
            <tr><a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House</a> Generic polling: {gen_poll_mm_str} Control {gen_mm_str}</tr>
            <br>
            <tr><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_moneyball_states}, Governor/SoS: NV AZ Supreme Courts: OH NC</tr>
        </table>
    </div>
    """

    banner_col1 = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> Senate: {dem_seats} | {rep_seats} (range: 47-52)Control: ({sen_mm_str}) from toss-up</span>
    </div>
    """

    banner_col2 = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House</a> Generic polling: {gen_poll_mm_str} Control {gen_mm_str}</span>
    </div>
    """

    
    banner_col3 = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_moneyball_states}, Governor/SoS: NV AZ Supreme Courts: OH NC</span>
    </div>
    """


    banner_old = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span>Nov 3 polls: Biden {ev_dem} EV ({ev_mm_str}), <a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_seats_dem} D, {sen_seats_rep} R ({sen_mm_str}), <a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House control</a> {gen_mm_str}</span>
        <br>
        <span><a href="/data/moneyball/">Moneyball</a> states: President {pres_moneyball_states}, <a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_moneyball_states}, <a href="/data/moneyball/">Legislatures</a> KS TX NC</span>
    </div>
    """

    path = os.path.join(DIR_PATH, 'banner.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner)

    path = os.path.join(DIR_PATH, 'banner_table.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_table)

    path = os.path.join(DIR_PATH, 'banner_col1.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_col1)
    
    path = os.path.join(DIR_PATH, 'banner_col2.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_col2)

    path = os.path.join(DIR_PATH, 'banner_col3.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_col3)
    
    path = os.path.join(DIR_PATH, 'banner_old.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_old)

if __name__ == "__main__":
    main()
