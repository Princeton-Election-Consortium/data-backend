import os
import csv

from datetime import datetime, timedelta
from decimal import *

# ======================================================================
# GLOBAL VARIABLES

YEAR = 2024

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# House
HOUSE_POLLS_CSV = os.path.join(DIR_PATH, '../scraping/outputs', f'{YEAR}.house.polls.median.csv')

# Senate
SENATE_ESTIMATES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'Senate_estimates_{YEAR}.csv')
SENATE_JERSEYVOTES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'Senate_jerseyvotes_{YEAR}.csv')

# Presidential
EV_ESTIMATES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'EV_estimates_{YEAR}.csv')
EV_JERSEYVOTES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'EV_jerseyvotes_{YEAR}.csv')

# Constants to set for the current election cycle
HOUSE_OFFSET = 0    # Same as custom_twin_axis_offset in graphics_util.py

# ======================================================================
# HELPER

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

# ======================================================================
# HOUSE

def parse_house():
    estimates = get_estimates(HOUSE_POLLS_CSV, dict_csv=True)
    gen_metamargin = (Decimal(estimates['median_margin']) - HOUSE_OFFSET).quantize(Decimal('0.1'))
    gen_polling = (Decimal(estimates['median_margin'])).quantize(Decimal('0.1'))

    gen_ahead_str = 'D+'
    if gen_metamargin < 0:
        gen_ahead_str = 'R+'
    elif gen_metamargin == 0:
        gen_ahead_str = 'Tie '

    gen_polling_ahead_str = 'D+'
    if gen_polling < 0:
        gen_polling_ahead_str = 'R+'
    elif gen_polling == 0:
        gen_polling_ahead_str = 'Tie '
    
    return gen_polling, gen_polling_ahead_str, gen_metamargin, gen_ahead_str

def write_house_banner(gen_poll_mm_str, gen_mm_str):
    banner_house = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-part-1-the-u-s-house/">House</a> Generic polling: {gen_poll_mm_str} Control: {gen_mm_str}</span>
    </div>
    """

    path = os.path.join(DIR_PATH, 'banner_house.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_house)

# ======================================================================
# SENATE

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

def write_senate_banner(dem_seats, rep_seats, sen_mm_str):
    banner_senate = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> Senate: {dem_seats} | {rep_seats} (range: 47-52) Control: {sen_mm_str} from toss-up</span>
    </div>
    """

    path = os.path.join(DIR_PATH, 'banner_senate.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_senate)

def write_senate_moneyball_banner(sen_moneyball_states):
    banner_senate_moneyball = f"""
        <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
            <span><a href="/election-tracking-{YEAR}-u-s-senate/">Senate</a> {sen_moneyball_states}, Governor/SoS: NV AZ Supreme Courts: OH NC</span>
        </div>
    """

    path = os.path.join(DIR_PATH, 'banner_senate_moneyball.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_senate_moneyball)

# ======================================================================
# PRESIDENTIAL

def parse_ev():
    estimates = get_estimates(EV_ESTIMATES_CSV)
    ev_rep = int(estimates[1])
    ev_dem = int(estimates[0])

    ev_metamargin = Decimal(estimates[12]).quantize(Decimal('0.1'))

    ev_ahead_str = 'D+'
    if ev_metamargin < 0:
        ev_ahead_str = 'R+'

    return ev_dem, ev_rep, ev_metamargin, ev_ahead_str

def get_ev_moneyball_states(n):
    pres_string = ""
    read = 0

    with open(EV_JERSEYVOTES_CSV, 'r') as f:
        reader = csv.reader(f)
        for row in reader: 
            if read == n:
                return pres_string
            if read == n - 1:
                # Maine CDs
                if row [1] == 'M1':
                    pres_string += 'ME-01'
                elif row[1] == 'M2':
                    pres_string += 'ME-02'
                    
                # Nebraska CDs
                elif row[1] == 'N1':
                    pres_string += 'NE-01'
                elif row[1] == 'N2':
                    pres_string += 'NE-02'
                elif row[1] == 'N3':
                    pres_string += 'NE-03'
                      
                else:
                    pres_string += row[1]
            else:
                # Maine CDs
                if row [1] == 'M1':
                    pres_string += 'ME-01' + " "
                elif row[1] == 'M2':
                    pres_string += 'ME-02' + " "
                    
                # Nebraska CDs
                elif row[1] == 'N1':
                    pres_string += 'NE-01' + " "
                elif row[1] == 'N2':
                    pres_string += 'NE-02' + " "
                elif row[1] == 'N3':
                    pres_string += 'NE-03' + " "
                    
                else:
                    pres_string += row[1] + " "
            read += 1
            
    return pres_string

def write_ev_banner(ev_dem, ev_mm_str, ev_moneyball_states):
    banner_ev = f"""
    <div style="font-weight: 600; width: 970px; color:black ; background-color: #eee ; line-height: 30px; font-family: Helvetica; font-size: 20px">
        <span>Nov 3 polls: Harris: {ev_dem} EV ({ev_mm_str} from toss-up)</span>
        <br>
        <span><a href="/data/moneyball/">Moneyball</a> states: President {ev_moneyball_states}</span>
    </div>
    """

    path = os.path.join(DIR_PATH, 'banner_ev.html')
    with open(path, 'w') as bannerfile:
        bannerfile.write(banner_ev)

# ======================================================================

def main():
    # HOUSE
    gen_polling, gen_polling_ahead_str, gen_metamargin, gen_ahead_str = parse_house()
    gen_poll_mm_str = f'{gen_polling_ahead_str}{abs(gen_polling)}%'
    gen_mm_str = f'{gen_ahead_str}{abs(gen_metamargin)}%'

    write_house_banner(gen_poll_mm_str, gen_mm_str)

    # SENATE
    sen_seats_dem, sen_seats_rep, sen_metamargin, sen_ahead_str = parse_senate()
    dem_seats = f'{sen_seats_dem}{" Dem"}'
    rep_seats = f'{sen_seats_rep}{" Rep"}'
    sen_mm_str = f'{sen_ahead_str}{abs(sen_metamargin)}%'

    sen_moneyball_states = get_sen_moneyball_states(3)
    
    write_senate_banner(dem_seats, rep_seats, sen_mm_str)
    write_senate_moneyball_banner(sen_moneyball_states)

    # PRESIDENTIAL
    ev_dem, ev_rep, ev_metamargin, ev_ahead_str = parse_ev()
    ev_mm_str = f'{ev_ahead_str}{abs(ev_metamargin)}%'
    ev_moneyball_states = get_ev_moneyball_states(3)

    write_ev_banner(ev_dem, ev_mm_str, ev_moneyball_states)    
    

if __name__ == "__main__":
    main()
