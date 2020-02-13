# datascrape.py
# Author: Lucas Manning <lucassm@princeton.edu> 2018
#
# This script aggregates public polling data from FiveThirtyEight, Huffington
# Post Pollster, and RealClearPolitics. Output is a CSV file that has the data
# cleaned and duplicate removed from all sources. 
# 
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for noncommericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu

# GLOBALS ==========================================================================================

import requests, os, csv, pollster, string, sys
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import date, datetime, timedelta
from statistics import median
from numpy import std, sqrt, mean, array
import json

FIELD_NAMES = [
    'pollster', 'startdate', 'enddate', 'source', 
    'samplesize', 'D_support', 'R_support', 'subpopulation'
]

OUTFILE_NAME = 'PEC_2018_data.csv'

# MAIN =============================================================================================

def main():
    if len(sys.argv) == 1:
        scrape_general()
        scrape_senate()
        scrape_timeseries()
        return 0

    if '--senate' in sys.argv:
        scrape_senate()
    if '--timeseries' in sys.argv:
        scrape_timeseries()
    if '--general' in sys.argv:
        scrape_general()
   
    return 0

# SCRAPING =========================================================================================

def scrape_timeseries():
    five38_data = fetch_538_data()
    rcp_data = fetch_realclear_data()
    huffpo_data = fetch_huffpo_data()

    data = merge_data(merge_data(five38_data, rcp_data), huffpo_data)
    data_sorted = sorted(data, key=lambda k: k["enddate"], reverse=True)
    time_series = generate_time_series(remove_overlapping(data_sorted))
   
    with open('timeseries.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['startdate', 'enddate', 'D-R', 'MAD', '# Polls'])            
        writer.writeheader()
        for row in time_series:
            writer.writerow(row)
 
def scrape_general():
    five38_data = fetch_538_data()
    rcp_data = fetch_realclear_data()
    huffpo_data = fetch_huffpo_data()

    data = merge_data(merge_data(five38_data, rcp_data), huffpo_data)
    data_sorted = sorted(data, key=lambda k: k["enddate"], reverse=True)

    with open(OUTFILE_NAME, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES)            
        writer.writeheader()
        for row in data_sorted:
            writer.writerow(row)
 
def scrape_senate():
    evote_data = fetch_senate_evote()
    rcp_data = fetch_senate_rcp()
    five38_data = fetch_senate_five38()
    senate_data = merge_senate(five38_data, merge_senate(evote_data, rcp_data))
    data_sorted = sorted(senate_data, key=lambda k: k["enddate"], reverse=True)
    senate_medians(data_sorted)
    senate_html()
    with open('senate_2018.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_NAMES + ['Rep_cand','Dem_cand', 'State_code', 'poll_URL', 'middate'])            
        writer.writeheader()
        for row in data_sorted:
            writer.writerow(row)

def fetch_senate_five38():
    url = "https://projects.fivethirtyeight.com/polls/polls.json"
    outfilename = "five38_polls.json"
    download_file(url, outfilename)
    states = (
        'New Jersey', 'Montana', 'Nevada', 'Florida', 'Arizona',
        'Indiana', 'Missouri', 'Texas', 'Tennessee', 'North Dakota'
    )
    codes = {
        'New Jersey' : 'NJ', 'Montana' : 'MT', 'Nevada' : 'NV', 'Florida' : 'FL', 'Arizona' : 'AZ',
        'Indiana' : 'IN', 'Missouri' : 'MO', 'Texas' : 'TX', 'Tennessee' : 'TN', 'North Dakota' : 'ND'
    }
    output = []
    with open(outfilename, newline="", encoding='utf-8') as jsonfile:
        polldata = json.load(jsonfile)
        senatedata = [x for x in polldata if x["type"] == "senate"]
        keysenatedata = [x for x in senatedata if x["state"] in states]

        for poll in keysenatedata:
            if poll['population'] != 'lv': continue
            entry = {
                "pollster" : poll["pollster"],
                "source" : "FiveThirtyEight",
                "samplesize" : poll["sampleSize"],
                "subpopulation" : poll["population"],
                "poll_URL" : poll["url"],
                'State_code' : codes[poll['state']]
            } 
            datevals = poll['startDate'].split('-')
            entry['startdate'] = date(int(datevals[0]), int(datevals[1]), int(datevals[2]))
            datevals = poll['endDate'].split('-')
            entry['enddate'] = date(int(datevals[0]), int(datevals[1]), int(datevals[2]))
            delta = (entry['startdate'] - entry['enddate']) / 2
            entry['middate'] = entry['startdate'] + delta

            Dem_answer = [x for x in poll["answers"] if x["party"] == "Dem"][0]
            Rep_answer = [x for x in poll["answers"] if x["party"] == "Rep"][0]

            entry["Dem_cand"] = Dem_answer["choice"]
            entry["Rep_cand"] = Rep_answer["choice"]
            entry["D_support"] = float(round(float(Dem_answer["pct"])))
            entry["R_support"] = float(round(float(Rep_answer["pct"])))

            output.append(entry)

    os.remove(outfilename)    
    return remove_dups_senate(output)

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

# Clean up the polls, following Sam's rules
def clean_polls(polls, day):

    num_recent_polls_to_use = 3
    # -1. Make sure there's something to clean
    if not polls:
        return []

    # 0. Sort the polls by ending date
    polls.sort(key = lambda x: x['enddate'], reverse = True)

    # 1. Drop all polls ending after "today"
    polls = filter(lambda x: x['enddate'] < day, polls)

    # 2. Only use the latest poll from each organization
    pollsters = []
    def seen(pollster):
        if pollster in pollsters:
            return True
        else:
            pollsters.append(pollster)
            return False

    polls = [poll for poll in polls if not seen(poll['pollster'])]

    # If we don't need to eliminate any more polls, return
    if len(polls) < num_recent_polls_to_use:

        return polls

    # 3. Find third oldest mid date of a poll, and include any from this date or newer
    polls.sort(key=lambda x: x['middate'], reverse=True)
    third_oldest_date = polls[num_recent_polls_to_use - 1]['middate']

    # 4. Find N weeks ago, where N is a function of "today"
    if day < date(2018, 8, 1): # Before August 1
        n = timedelta(7 * 6, 0, 0) # 6 weeks
    elif day < date(2018, 9, 1):   # Month of August
        n = timedelta(7 * 4, 0, 0) # 4 weeks
    elif day < date(2018, 10, 1):  # September
        #n = datetime.timedelta(7 * 2, 0, 0) # 2 weeks
	    n = timedelta(28 - (day.day - 1) / 2, 0, 0) # Ease from 28 days to 14 over the course of the month
    else:                                   # October onwards
        n = timedelta(7 * 2, 0, 0) # now also 2 weeks
    n_weeks_ago = day - n

    # 5. Return all polls with a median date of (#3) or newer, or an ending date of (#4) or newer
    return list(filter(lambda x: x['middate'] >= third_oldest_date or x['enddate'] >= n_weeks_ago, polls))

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
        margin = float(polls[0]['D_support']) - float(polls[0]['R_support'])
        sem = 0.05
        w(num, date, (margin, sem))
    elif num == 2:
        margins = [float(poll['D_support']) - float(poll['R_support']) for poll in polls]
        w(num, date, get_two_statistics(array(margins)))
    else:
        margins = [float(poll['D_support']) - float(poll['R_support']) for poll in polls]
        w(num, date, get_statistics(array(margins)))

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

    with open("stateprobs.html", "w") as outf:
        outf.write(html)

def senate_medians(data):
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

    f = open('2018.Senate.polls.median.txt', 'w')
    ndays = end_date - start_date
    since_beg = start_date - ref_date
    for i in range(ndays.days):
        for state_num, state in one_indexed_enumerate(sorted(CANDIDATES.keys())):
            state_polls = [x for x in data if x['State_code'].lower() == state.lower()]
            delta = timedelta(days=i)
            day = start_date + delta
            polls = list(clean_polls(state_polls, day))
            if len(polls) == 0: 
                f.write('%2d  ' % len(list(polls)))
                f.write('%3s  ' % day.strftime("%j"))
                f.write('% 5.1f  %.4f  ' % (float(CANDIDATES[state][1]), 3.0))
            else:
                write_statistics(f, polls)
            f.write('%d  %s\n' % (i + since_beg.days, state_num))
    f.close()

def remove_dups_senate(data):
    s = set()
    new_data = []
    for row in data:
        dminusr = row['D_support'] - row['R_support']
        rowstring = "".join([str(dminusr), str(row['startdate']), str(row['enddate'])])
        if rowstring in s: continue
        s.add(rowstring)
        new_data.append(row)
    return new_data

def merge_senate(t1, t2):
    t3 = []
    for row1 in t1:
        has_dup = False
        for row2 in t2:
            critera = 0
            if abs((row1['D_support'] - row1['R_support']) - (row2['D_support'] - row2['R_support'])) <= 2:
                critera += 1
            if row1['pollster'] == row2['pollster']:
                critera += 1

            deltastart = abs(row1['startdate'] - row2['startdate'])
            deltaend = abs(row1['enddate'] - row2['enddate'])

            if deltastart.days < 2 and deltaend.days < 2:
                critera += 1

            if row1['samplesize'] == row2['samplesize']:
                criteria += 1

            if row1['State_code'] == row2['State_code'] and critera >= 2:
                has_dup = True
                break
        if has_dup == False:
            t3.append(row1)
    return t3 + t2

def fetch_huffpo_data():
    url = "https://elections.huffingtonpost.com/pollster/api/v2/questions/18-US-House/poll-responses-clean.tsv"
    outfilename = "huffpo_2018_data.csv"
    download_file(url, outfilename)

    data = []
    with open(outfilename, newline="", encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            datarow = {}
            datarow["D_support"] = row["Democrat"]
            datarow["R_support"] = row["Republican"]
            datarow["pollster"] = row["survey_house"]
            datarow["subpopulation"] = row["sample_subpopulation"]

            date_parts = row["start_date"].split("-")
            datarow["startdate"] = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))

            date_parts = row["end_date"].split("-")
            datarow["enddate"] = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))

            datarow["samplesize"] = row["observations"]
            datarow["source"] = "HuffPost Pollster"

            data.append(datarow)

    os.remove(outfilename)
    return remove_dups(data)

def fetch_538_data():
    url = "https://projects.fivethirtyeight.com/generic-ballot-data/generic_polllist.csv"
    outfilename = "538_2018_data.csv"
    download_file(url, outfilename)

    data = []
    subpop_key = {'rv' : 'Registered Voters', 'lv' : 'Likely Voters', 'a' : 'Adults', 'v' : 'Voters'}
    with open(outfilename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            datarow = {}
            datarow["D_support"] = row["dem"]
            datarow["R_support"] = row["rep"]
            datarow["pollster"] = row["pollster"]
            datarow["subpopulation"] = subpop_key[row["population"]]

            date_parts = row["startdate"].split("/")
            datarow["startdate"] = date(int(date_parts[2]), int(date_parts[0]), int(date_parts[1]))

            date_parts = row["enddate"].split("/")
            datarow["enddate"] = date(int(date_parts[2]), int(date_parts[0]), int(date_parts[1]))

            datarow["samplesize"] = row["samplesize"]
            datarow["source"] = "FiveThirtyEight"

            data.append(datarow)
    
    os.remove(outfilename)
    return remove_dups(data)

def fetch_senate_evote():
    url = 'http://electoral-vote.com/evp2018/Senate/senate_polls.txt'
    outfile = 'senate_polls.txt'
    # hardcoded for now
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
    download_file(url, outfile)

    data = []
    with open(outfile, newline="") as txtfile:     
        for line in txtfile:
            datarow = {}
            values = line.split(' ')
            datarow['State_code'] = values[0].upper()
            if not datarow['State_code'] in CANDIDATES.keys(): continue
            datarow['Dem_cand'] = CANDIDATES[datarow['State_code']][0]
            datarow['Rep_cand'] = CANDIDATES[datarow['State_code']][1]
            datarow['D_support'] = float(values[1])
            datarow['R_support'] = float(values[2])
            datarow['pollster'] = " ".join(values[8:])
            datarow['pollster'] = datarow['pollster'][:-1]
            datarow['poll_URL'] = "https://electoral-vote.com/evp2018/Info/datagalore.html"
            datarow['source'] = 'electoral-vote'
            datarow['samplesize'] = -1
            
            if datarow['pollster'] == 'Marist' or datarow['pollster'] == 'Suffolk': continue
            if "Siena" in datarow['pollster']: continue

            start_month = values[4]
            start_day = values[5]

            end_month = values[6]
            end_day = values[7]

            startdate = datetime.strptime('2018-' + start_month + '-' + start_day, '%Y-%b-%d').date()
            enddate = datetime.strptime('2018-' + end_month + '-' + end_day, '%Y-%b-%d').date()
            if enddate.month < 3: continue
            
            datarow['startdate'] = startdate
            delta = enddate - startdate
            datarow['middate'] = startdate + (delta / 2)
            datarow['enddate'] = enddate

            data.append(datarow)

    os.remove(outfile)
    return remove_dups_senate(data)
            
def fetch_senate_rcp():
    KEY_SENATE_RACE_URLS = [
        'https://www.realclearpolitics.com/epolls/2018/senate/az/arizona_senate_mcsally_vs_sinema-6328.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/fl/florida_senate_scott_vs_nelson-6246.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/in/indiana_senate_braun_vs_donnelly-6573.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/mo/missouri_senate_hawley_vs_mccaskill-6280.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/mt/montana_senate_rosendale_vs_tester-6306.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/nd/north_dakota_senate_cramer_vs_heitkamp-6485.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/nj/new_jersey_senate_hugin_vs_menendez-6506.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/nv/nevada_senate_heller_vs_rosen-6304.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/tn/tennessee_senate_blackburn_vs_bredesen-6308.html',
        'https://www.realclearpolitics.com/epolls/2018/senate/tx/texas_senate_cruz_vs_orourke-6310.html',
    ]

    data = []
    subpop_key = {'RV' : 'Registered Voters', 'LV' : 'Likely Voters', 'A' : 'Adults'}
    for race_url in KEY_SENATE_RACE_URLS:
        outfilename = 'realclearsenate.html'
        download_file(race_url, outfilename)
        with open(outfilename, newline="") as htmlfile:
            soup = BeautifulSoup(htmlfile, 'html.parser')
            rows = soup(id='polling-data-full')[0].find_all('tr', attrs={'data-id' : True})

            # this is so annoying. 
            d_column = 4
            r_column = 5
            r_name = list(soup(id='polling-data-full')[0].find('tr').children)[r_column].string
            d_name = list(soup(id='polling-data-full')[0].find('tr').children)[d_column].string
            if '(R)' in d_name:
                tmp = d_name
                d_name = r_name
                r_name = tmp
                d_column = 5
                r_column = 4

            if (len(rows) > 7):
                rows = rows[:7]

            for row in rows:
                datarow = {}
                columns = list(row.children)
                datarow["pollster"] = columns[0].a.string
                datarow['poll_URL'] = columns[0].a["href"]  
                try:
                    datarow["samplesize"] = int(columns[2].string.split(' ')[0])
                    datarow["subpopulation"] = subpop_key[columns[2].string.split(' ')[1]]
                except Exception:
                    # not given in real clearj
                    datarow["samplesize"] = -1
                    datarow["subpopulation"] = subpop_key[columns[2].string.split(' ')[0]]

                datarow["D_support"] = float(columns[d_column].string)
                datarow["R_support"] = float(columns[r_column].string)
                datarow["source"] = "Real Clear Politics"
                datarow['State_code'] = race_url.split('/')[6].upper()
                datarow['Rep_cand'] = r_name.split(' ')[0]
                datarow['Dem_cand'] = d_name.split(' ')[0]

                # parse the annoying formatting of start and end date on RCP
                # It comes in as "7/1 - 7/5" with no year info
                thisyear = date.today().year
                datestring = columns[1].string
                dates = datestring.split('-')

                date_values = [int(x) for x in dates[0].split('/')]
                startdate = date(thisyear, date_values[0], date_values[1])
                
                if startdate > date.today():
                    startdate = startdate.replace(year=thisyear - 1) 

                date_values = [int(x) for x in dates[1].split('/')]
                enddate = date(thisyear, date_values[0], date_values[1])
                
                if enddate > date.today():
                    enddate = enddate.replace(year=thisyear - 1) 
                
                datarow["startdate"] = startdate
                delta = enddate - startdate
                datarow['middate'] = startdate + (delta / 2)
                datarow["enddate"] = enddate

                data.append(datarow)

        os.remove(outfilename)
    return data

def fetch_realclear_data():
    url = "https://www.realclearpolitics.com/epolls/other/2018_generic_congressional_vote-6185.html#polls"
    outfilename = "realclear.html"
    download_file(url, outfilename)

    data = []
    subpop_key = {'RV' : 'Registered Voters', 'LV' : 'Likely Voters', 'A' : 'Adults'}
    with open(outfilename, newline="") as htmlfile:
        soup = BeautifulSoup(htmlfile, "html.parser")
        rows = soup("tr", attrs={"data-id":True})
        for row in rows:
            datarow = {}
            columns = list(row.children)
            datarow["pollster"] = columns[0].a.string
            try:
                datarow["samplesize"] = int(columns[2].string.split(' ')[0])
                datarow["subpopulation"] = subpop_key[columns[2].string.split(' ')[1]]
            except Exception:
                # not given in real clearj
                datarow["samplesize"] = -1
                datarow["subpopulation"] = subpop_key[columns[2].string.split(' ')[0]]

            datarow["D_support"] = columns[3].string
            datarow["R_support"] = columns[4].string
            datarow["source"] = "Real Clear Politics"

            # parse the annoying formatting of start and end date on RCP
            # It comes in as "7/1 - 7/5" with no year info
            thisyear = date.today().year
            datestring = columns[1].string
            dates = datestring.split('-')

            date_values = [int(x) for x in dates[0].split('/')]
            startdate = date(thisyear, date_values[0], date_values[1])
            
            if startdate > date.today():
                startdate = startdate.replace(year=thisyear - 1) 

            date_values = [int(x) for x in dates[1].split('/')]
            enddate = date(thisyear, date_values[0], date_values[1])
            
            if enddate > date.today():
                enddate = enddate.replace(year=thisyear - 1) 
            
            datarow["startdate"] = startdate
            datarow["enddate"] = enddate

            data.append(datarow)

    os.remove(outfilename)
    return remove_dups(data)

# STATISTICS =======================================================================================

# Generates a time series of the median of a weeks worth of D-R
def generate_time_series(data):
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

        dminusr_data = [float(d['D_support']) - float(d['R_support']) for d in agg_data]
        dminusr_median = median(dminusr_data) 
        mad = median([abs(d - dminusr_median) for d in dminusr_data])

        row = {'enddate' : end_date, 'startdate' : start_date, 'D-R' : dminusr_median, 'MAD' : mad, 
            '# Polls' : len(dminusr_data)}
        output.append(row)
        current_date += delta
    return output

# UTILITY ==========================================================================================

# detects "rolling average polls" that have overlapping dates and removes them. This cleans up the 
# data slightly for the time series
def remove_overlapping(data):
    output = []
    for row in data:
        found_overlap = False
        for row1 in output:
            if row['pollster'] == row1['pollster'] and row['startdate'] <= row1['enddate'] and row1['startdate'] <= row['enddate']:
                found_overlap = True
        if not found_overlap:
            output.append(row)
    return output

# helper that takes in a url and filename and downloads the content of that url to a file names
# outfilename
def download_file(url, outfilename):
    # read in the csv file with the data
    r = requests.get(url, stream=True)
    with open(outfilename, "wb") as fd: 
        for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

# merges the two data from different sources, removing entries that are from the same pollster 
# taken at the same time (these are highly likely to be the same poll)
def merge_data(t1, t2):
    t3 = []
    for row1 in t1:
        has_dup = False
        for row2 in t2:
            if row2['samplesize'] == row1['samplesize']:
            # if row1["pollster"] in row2["pollster"] or row2["pollster"] in row1["pollster"]:
                if row1["startdate"] == row2["startdate"] and row1["enddate"] == row2["enddate"]:
                    has_dup = True
        if not has_dup:
            t3.append(row1)
    return t3 + t2

# Takes in an array of dictionaries containing data formatted with FIELDNAME fields and removes rows
# that are exactly the same
def remove_dups(data):
    s = set()
    new_data = []
    for row in data:
        str_row = [str(e) for e in row.values()]
        rowstring = "".join(str_row)
        if rowstring in s: continue
        s.add(rowstring)
        new_data.append(row)
    return new_data

# Take an iterable and enumerate it, but use 1-indexing
# This makes MATLAB happy
def one_indexed_enumerate(d):
    for num, item in enumerate(d):
        yield (num + 1, item)


# Main function boilerplate
if __name__ == "__main__":
    exit(main())
