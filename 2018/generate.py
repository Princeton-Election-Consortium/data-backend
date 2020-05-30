# Author: Lucas Manning <lucassm@princeton.edu> 2018
#
# This script aggregates public polling data from FiveThirtyEight, Huffington
# Post Pollster, and RealClearPolitics. Output is a CSV file that has the data
# cleaned and duplicate removed from all sources. 
# 
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for non-commericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu

# individual senate

# all senate aggregate

# presidential generic

# presidential jersey votes

import json, requests, os, csv, string, sys
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import date, datetime, timedelta
from statistics import median
from numpy import std, sqrt, mean, array

from clean import *
from scrape import *


def generic_timeseries():
    five38_data = fetch_538_generic()
    five38_data = remove_dups(five38_data)
    data_sorted = sorted(five38_data, key=lambda k: k["enddate"], reverse=True)
    time_series = generic_timeseries_data(remove_overlapping_timeseries(data_sorted))

    field_names = ('startdate', 'enddate', 'D-R', 'MAD', '# Polls')
    now = datetime.datetime.now()
   
    with open(f"out/generic-timeseries-{now.year}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)            
        writer.writeheader()
        for row in time_series:
            writer.writerow(row)
 
def generic_polls():
    five38_data = fetch_538_generic()
    five38_data = remove_dups(five38_data)

    field_names = ( 
        'pollster', 'startdate', 'enddate', 'source', 
        'samplesize', 'd_support', 'r_support', 'subpopulation'
    )
    now = datetime.datetime.now()

    data_sorted = sorted(five38_data, key=lambda k: k["enddate"], reverse=True)

    with open(f"out/allpolls-generic-{now.year}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)            
        writer.writeheader()
        for row in data_sorted:
            writer.writerow(row)
 
def senate_polls():
    five38_data = remove_dups_senate(fetch_538_senate())
    data_sorted = sorted(five38_data, key=lambda k: k["enddate"], reverse=True)

    field_names = ( 
        'pollster', 'startdate', 'enddate', 'source', 
        'samplesize', 'd_support', 'r_support', 'subpopulation'
        'rep_cand','dem_cand', 'state_code', 'poll_url', 'middate'
    )
    now = datetime.datetime.now()

    with open(f"out/allpolls-senate-{now.year}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)            
        writer.writeheader()
        for row in data_sorted:
            writer.writerow(row)

def presidential_polls():
    five38_data = fetch_538_presidential()
    data_sorted = sorted(five38_data, key=lambda k: k["enddate"], reverse=True)

    field_names = ( 
        'pollster', 'startdate', 'enddate', 'source', 
        'samplesize', 'd_support', 'r_support', 'subpopulation'
        'rep_cand','dem_cand', 'state_code', 'poll_url', 'middate'
    )
    now = datetime.datetime.now()

    with open(f"out/allpolls-presidential-{now.year}.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)            
        writer.writeheader()
        for row in data_sorted:
            writer.writerow(row)

def presidential_medians():
    pass

def senate_medians():
    five38_data = remove_dups_senate(fetch_538_senate())
    data = sorted(five38_data, key=lambda k: k["enddate"], reverse=True)

    # hardcoded for now
    CANDIDATES = {
        'AZ' : (['Sinema', 'McSally'], 5),
        'FL' : (['Nelson', 'Scott'], 0),
        'IN' : (['Donnelly', 'Braun'], 0),
        'MO' : (['McCaskill', 'Hawley'], 0),
        'MT' : (['Tester', 'Rosendale'], 3),
        'ND' : (['Heitkamp', 'Cramer'], -5),
        'NJ' : (['Menendez', 'Hugin'], 7),
        'NV' : (['Rosen', 'Heller'], 5),
        'TN' : (['Bredesen', 'Blackburn'], -5),
        'TX' : (['O\'Rourke', 'Cruz'], -5)
    }
     # need to iterate through each day since march 1 
     # iterate through each state
     # clean the polls
     # write the stats for the cleaned polls
     # then write the date and state
    out_data = []

    start_date = date(2018, 3, 1)
    ref_date = date(2018, 1, 1)
    end_date = date.today()

    now = datetime.datetime.now()
    f = open(f"{now.year}.Senate.polls.median.txt", 'w')
    ndays = end_date - start_date
    since_beg = start_date - ref_date
    for i in range(ndays.days):
        for state_num, state in one_indexed_enumerate(sorted(CANDIDATES.keys())):
            state_polls = [x for x in data if x['State_code'].lower() == state.lower()]
            delta = timedelta(days=i)
            day = start_date + delta
            polls = list(clean_polls_sam_rules(state_polls, day))
            if len(polls) == 0: 
                f.write('%2d  ' % len(list(polls)))
                f.write('%3s  ' % day.strftime("%j"))
                f.write('% 5.1f  %.4f  ' % (float(CANDIDATES[state][1]), 3.0))
            else:
                write_statistics(f, polls)
            f.write('%d  %s\n' % (i + since_beg.days, state_num))
    f.close()


def senate_html():
    html = """
    <style> #stateprobs th, #stateprobs td { border: 1px solid black;} </style>
    <table id="stateprobs" style="border: 1px solid black; text-align: center; font-family: sans-serif; font-size: initial; border-collapse: collapse; width: 100%">
<tbody><tr>
	<th rowspan="1">State</th>
	<th rowspan="1">Current Margin</th>
</tr>
    """
    CANDIDATES = {
        'AZ' : ['Sinema', 'McSally','https://www.realclearpolitics.com/epolls/2018/senate/az/arizona_senate_mcsally_vs_sinema-6328.html'],
        'FL' : ['Nelson', 'Scott', 'https://www.realclearpolitics.com/epolls/2018/senate/fl/florida_senate_scott_vs_nelson-6246.html'],
        'IN' : ['Donnelly', 'Braun', 'https://www.realclearpolitics.com/epolls/2018/senate/in/indiana_senate_braun_vs_donnelly-6573.html'],
        'MO' : ['McCaskill', 'Hawley', 'https://www.realclearpolitics.com/epolls/2018/senate/mo/missouri_senate_hawley_vs_mccaskill-6280.html'],
        'MT' : ['Tester', 'Rosendale', 'https://www.realclearpolitics.com/epolls/2018/senate/mt/montana_senate_rosendale_vs_tester-6306.html'],
        'ND' : ['Heitkamp', 'Cramer', 'https://www.realclearpolitics.com/epolls/2018/senate/nd/north_dakota_senate_cramer_vs_heitkamp-6485.html'],
        'NJ' : ['Menendez', 'Hugin', 'https://www.realclearpolitics.com/epolls/2018/senate/nj/new_jersey_senate_hugin_vs_menendez-6506.html'],
        'NV' : ['Rosen', 'Heller', 'https://www.realclearpolitics.com/epolls/2018/senate/nv/nevada_senate_heller_vs_rosen-6304.html'],
        'TN' : ['Bredesen', 'Blackburn', 'https://www.realclearpolitics.com/epolls/2018/senate/tn/tennessee_senate_blackburn_vs_bredesen-6308.html'],
        'TX' : ['O\'Rourke', 'Cruz', 'https://www.realclearpolitics.com/epolls/2018/senate/tx/texas_senate_cruz_vs_orourke-6310.html']
    }
    data = []
    with open('./Senate_stateprobs.csv') as stateprobscsv:
        reader = csv.reader(stateprobscsv)
        for row in reader:
            data.append({'state' : row[5].upper(), 'metamargin' : float(row[2])})
    data = sorted(data, key=lambda x: x['metamargin'], reverse=True)

    for row in data:
        rowhtml = "<tr><td>" + row['state'] + "</td>"
        if row['metamargin'] >= 0:
            dminusr = "{0} +{1}%".format(CANDIDATES[row['state']][0], float(row['metamargin']))
            rowhtml += '<td><a style="color: blue" href="{0}">'.format(CANDIDATES[row['state']][2])+dminusr+'</a></td>'
        else:
            dminusr = "{0} +{1}%".format(CANDIDATES[row['state']][1], abs(float(row['metamargin'])))
            rowhtml += '<td><a style="color: red" href="{0}">'.format(CANDIDATES[row['state']][2])+dminusr+'</a></td>'
        html += rowhtml
    html += "</tbody></table>" 

    with open("out/stateprobs.html", "w") as outf:
        outf.write(html)

############################################################################
#
# Returns the median and std. error
#
############################################################################

# The std. error is given by:
#         std. deviation / sqrt(num of polls)
#
# We robustly estimate the std. deviation from the median absolute
# deviation (MAD) using the standard formula:
#        std. deviation =  MAD / invcdf(0.75)
#
# The MAD is defined as median( abs[samples - median(samples)] )
# invcdf(0.75) is approximately 0.6745

def get_statistics(margins):
    num = margins.size
    assert num >= 3

    median_margin = median(margins)
    mad = median(abs(margins - median_margin))
    sem_est = mad/0.6745/sqrt(num)

    #Sometimes SEM is 0. Sam want this to be replaced by SD/sqrt(n)
    if sem_est == 0:
        sem_est = std(margins) / sqrt(num)

    return (median_margin, sem_est)

# Special case for when only two polls are available

def get_two_statistics(margins):

    assert margins.size == 2

    mean_margin = mean(margins)
    sem = max(std(margins) / sqrt(margins.size), 3)

    return (mean_margin, sem)

def write_statistics(pfile, polls):
    # Number of polls available on this date for this state
    num = len(polls)
    
    #rnum is the number of real polls (excluding pseudo)
    # rnum = num - 1 if pseudo else num

    polls.sort(key=lambda x: x['middate'], reverse=True)

    # Get the mid date of the oldest poll
    date = int(polls[-1]['middate'].strftime('%j'))

    def w(num, date, stats):
        pfile.write('%2d  ' % num)
        pfile.write('%3s  ' % int(date))
        pfile.write('% 5.1f  %.4f  ' % stats)

    if num == 0:
        assert False
    elif num == 1:
        margin = float(polls[0]['d_support']) - float(polls[0]['r_support'])
        sem = 0.05
        w(num, date, (margin, sem))
    elif num == 2:
        margins = [float(poll['d_support']) - float(poll['r_support']) for poll in polls]
        w(num, date, get_two_statistics(array(margins)))
    else:
        margins = [float(poll['d_support']) - float(poll['r_support']) for poll in polls]
        w(num, date, get_statistics(array(margins)))


# Generates a time series of the median of a weeks worth of D-R
def generic_timeseries_data(data):
    output = [] 
    NUM_POLLS = 10
    current_date = data[0]['enddate']
    delta = timedelta(days=-1)
    deltaweek = timedelta(days=-14)
    while current_date > date(2018, 3, 1):
        agg_data = [x for x in data if x["enddate"] > current_date + deltaweek and x["enddate"] < current_date]
        if len(agg_data) == 0:
            current_date += delta
            continue

        start_date = min([d['startdate'] for d in agg_data])
        end_date = max([d['enddate'] for d in agg_data])

        dminusr_data = [float(d['d_support']) - float(d['r_support']) for d in agg_data]
        dminusr_median = median(dminusr_data) 
        mad = median([abs(d - dminusr_median) for d in dminusr_data])

        row = {'enddate' : end_date, 'startdate' : start_date, 'D-R' : dminusr_median, 'MAD' : mad, 
            '# Polls' : len(dminusr_data)}
        output.append(row)
        current_date += delta
    return output


def main():
    if len(sys.argv) > 1:
        eval(sys.argv[1])
    return 0

# Main function boilerplate
if __name__ == "__main__":
    exit(main())
