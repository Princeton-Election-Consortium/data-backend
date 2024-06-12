import os
import csv

from datetime import datetime, timedelta
from decimal import *

# ======================================================================
# GLOBAL VARIABLES

YEAR = 2024

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

SCRAPING_OUTPUTS_DIR = '../scraping/outputs'
HOUSE_POLLS_CSV = os.path.join(DIR_PATH, SCRAPING_OUTPUTS_DIR, f'{YEAR}.house.polls.median.csv')

MATLAB_OUTPUTS_DIR = '../matlab/outputs/'
SENATE_ESTIMATES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'Senate_estimates_{YEAR}.csv')
SENATE_JERSEYVOTES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'Senate_jerseyvotes_{YEAR}.csv')
EV_ESTIMATES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'EV_estimates_{YEAR}.csv')
EV_JERSEYVOTES_CSV = os.path.join(DIR_PATH, MATLAB_OUTPUTS_DIR, f'EV_jerseyvotes_{YEAR}.csv')

# Constants to set for the current election cycle
HOUSE_OFFSET = 0    # Same as custom_twin_axis_offset in graphics_util.py

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

# ======================================================================

def parse_house():
    estimates = get_estimates(HOUSE_POLLS_CSV, dict_csv=True)
    gen_metamargin = (Decimal(estimates['median_margin']) - HOUSE_OFFSET).quantize(Decimal('0.1'))
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
    
    return gen_polling, gen_polling_ahead_str, gen_metamargin, gen_ahead_str

def parse_senate():
    estimates = get_estimates(SENATE_ESTIMATES_CSV)
    sen_seats_dem = int(estimates[0])
    sen_seats_rep = 100 - sen_seats_dem
    sen_metamargin = Decimal(estimates[-1]).quantize(Decimal('0.1'))

    sen_ahead_str = 'D+'
    if sen_metamargin < 0:
        sen_ahead_str = 'R+'
    elif sen_metamargin == 0:
        sen_ahead_str  = 'Tie'

    return sen_seats_dem, sen_seats_rep, sen_metamargin, sen_ahead_str

def parse_ev():
    estimates = get_estimates(EV_ESTIMATES_CSV)
    ev_rep = int(estimates[1])
    ev_dem = int(estimates[0])

    ev_metamargin = Decimal(estimates[12]).quantize(Decimal('0.1'))

    ev_ahead_str = 'D+'
    if ev_metamargin < 0:
        ev_ahead_str = 'R+'

    return ev_dem, ev_rep, ev_metamargin, ev_ahead_str

def main():
    # HOUSE
    gen_polling, gen_polling_ahead_str, gen_metamargin, gen_ahead_str = parse_house()
    gen_mm_str = f'{gen_ahead_str}{abs(gen_metamargin)}%'
    gen_poll_mm_str = f'{gen_polling_ahead_str}{abs(gen_polling)}%'

    # SENATE
    sen_seats_dem, sen_seats_rep, sen_metamargin, sen_ahead_str = parse_senate()
    sen_moneyball_states = get_sen_moneyball_states(3)
    dem_seats = f'{sen_seats_dem}{" Dem"}'
    rep_seats = f'{sen_seats_rep}{" Rep"}'

    # PRESIDENTIAL
    ev_dem, ev_rep, ev_metamargin, ev_ahead_str = parse_ev()
    pres_moneyball_states = get_pres_moneyball_states(3)
    ev_mm_str = f'{ev_ahead_str}{abs(ev_metamargin)}%'
    sen_mm_str = f'{sen_ahead_str}{abs(sen_metamargin)}%'

    # print(ev_mm_str)
    # print(sen_mm_str)
    # print(gen_mm_str)
    # print(gen_poll_mm_str)
    # print(dem_seats)
    # print(rep_seats)

    weekday_num = datetime.now().date().weekday()
    past_sunday = datetime.now() + timedelta(days=-weekday_num)
    end_of_week = past_sunday + timedelta(days=6)
    weekstartnum = past_sunday.strftime("%d")
    weekendnum = end_of_week.strftime("%d")
    

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

    banner_senate = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> Senate: {dem_seats} | {rep_seats} (range: 47-52)Control: ({sen_mm_str}) from toss-up</span>
    </div>
    """

    banner_house = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House</a> Generic polling: {gen_poll_mm_str} Control {gen_mm_str}</span>
    </div>
    """

    
    banner_senate_moneyball = f"""
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

    path = os.path.join(DIR_PATH, 'banner_senate.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_senate)
    
    path = os.path.join(DIR_PATH, 'banner_house.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_house)

    path = os.path.join(DIR_PATH, 'banner_senate_moneyball.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_senate_moneyball)
    
    path = os.path.join(DIR_PATH, 'banner_old.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_old)

if __name__ == "__main__":
    main()
