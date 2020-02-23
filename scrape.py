import csv, os, json
from datetime import date, datetime
from bs4 import BeautifulSoup
from .util import *


# ==================================================================================================
# GENERIC CONGRESSIONAL RACE
# ==================================================================================================

def fetch_538_generic():
    url = "https://projects.fivethirtyeight.com/generic-ballot-data/generic_polllist.csv"
    outfilename = "538_2020_generic.csv"
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
    return data

def fetch_rcp_generic():
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
    return data

# ==================================================================================================
# KEY SENATE RACES
# ==================================================================================================

def fetch_538_senate():
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
    return output

def fetch_evote_senate():
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
    return data
            

def fetch_rcp_senate():
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

