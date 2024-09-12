
import os
import csv

from decimal import *
from state_code_util import *
from collections import OrderedDict
from datetime import datetime
import operator

# ======================================================================
# GLOBAL VARIABLES

YEAR = 2024

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# Senate
SENATE_PRIORS_CSV = os.path.join(DIR_PATH, '../scraping/', f'{YEAR}.Senate.priors.csv')
SENATE_POLLS_CSV = os.path.join(DIR_PATH, '../scraping/outputs/', f'{YEAR}.Senate.polls.median.csv')
SENATE_JERSEYVOTES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'Senate_jerseyvotes_{YEAR}.csv')
FIVETHIRTYEIGHT_SENATE_URL = f"https://projects.fivethirtyeight.com/polls/senate/{YEAR}/"

# Presidential
EV_STATEPROBS_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'EV_stateprobs_{YEAR}.csv')
EV_JERSEYVOTES_CSV = os.path.join(DIR_PATH, '../matlab/outputs/', f'EV_jerseyvotes_{YEAR}.csv')
FIVETHIRTYEIGHT_EV_URL = f"https://projects.fivethirtyeight.com/polls/president-general/{YEAR}/"

# Constants to set for the current election cycle
D_SEATS_START = 43
SENATE_STATES = {
        1: 'AZ',
        2: 'FL',
        3: 'MD', 
        4: 'MI',
        5: 'MT',
        6: 'NE',
        7: 'NV',
        8: 'OH',
        9: 'PA',
        10: 'TX',
        11: 'WI',
        12: 'WV'
    }
EV_CANDIDATES = {
    "dem" : "Harris",
    "rep" : "Trump"
}

# ======================================================================
# HTML SNIPPETS

# Used for both Senate and Presidential table
# Columns: State, Margin, Voter Power
style_and_start = """
<style scoped>
    label {
        font-family: sans-serif;
        font-size: 14px;
    }
    table{
        font-family: sans-serif;
        border-collapse: collapse;
        border-spacing: 2px;
        border-color: gray;
        display: table;
        width: 100%;
        max-width: 640px;
        font-size: 12px;
        border: 1px solid #eee;
        border-bottom: 1px solid #eee;
        border-left: 1px solid #eee;
        border-top: 1px solid #eee;
        border-right: 1px solid #eee;
    }

    th {
        text-align: center;
        vertical-align: inherit;
        border: 1px solid #eee;
        font-weight: bold;
        display: table-cell;
    }

    tr:not(:last-child) {
        border-bottom: 1px solid #eee
    }

    table > tr {
        vertical-align: middle;
    }

    tr {
        display: table-row;
        border-color: inherit;
    }

    td {
        display: table-cell;
        vertical-align: inherit;
        text-align: center;
        border: 1px solid #eee;
    }
</style>

<div>
<table id="table">
    <tr> 
        <th colspan="1">State</th>
        <th colspan="1">Margin</th>
        <th colspan="1">Voter Power</th>
    </tr>"""

style_and_start2 = """
<style scoped>
    label {
        font-family: sans-serif;
        font-size: 14px;
    }
    table{
        font-family: sans-serif;
        border-collapse: collapse;
        border-spacing: 2px;
        border-color: gray;
        display: table;
        width: 100%;
        max-width: 640px;
        font-size: 12px;
        border: 1px solid #eee;
    }

    th {
        text-align: center;
        vertical-align: inherit;
        border: 1px solid #eee;
        font-weight: bold;
        display: table-cell;
    }

    tr:not(:last-child) {
        border-bottom: 1px solid #eee
    }

    table > tr {
        vertical-align: middle;
    }

    tr {
        display: table-row;
        border-color: inherit;
    }

    td {
        display: table-cell;
        vertical-align: inherit;
        text-align: center;
        border: 1px solid #eee;
    }
</style>

<div>
<table id="senate-table">
    <tr> 
        <th colspan="1">State</th>
        <th colspan="1">Margin</th>
        <th colspan="1">Voter Power</th>
        <th colspan="1">D seats</th>

    </tr>"""

close = """
</table>
</div>"""

# ======================================================================
# HELPER

def sort(margins):
    tempMargins = {}
    sorted_dict = {}

    for key, value in margins.items():
        tempMargins[key] = value['margin']


    sort_dict= dict(sorted(tempMargins.items(), key=operator.itemgetter(1), reverse=True))
    return sort_dict

# FOR EV
def get_538_link(postal_code):
    # no links available for following states:
    # DC, HI, ID, IN, KY, ND, VT, WY
    if postal_code not in ["DC", "HI", "ID", "IN", "KY", "ND", "VT", "WY"]:
        return FIVETHIRTYEIGHT_EV_URL + get_formatted_state(postal_code, url_format=True)
    return FIVETHIRTYEIGHT_EV_URL 

# ======================================================================
# SENATE

def get_sen_candidates(path):
    candidates = {}
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates[row['code']] = {
                'dem' : row['dem'],
                'rep' : row['rep']
            }
    return candidates

def get_sen_jerseyvotes(path):
    """
    *** note *** currently relies on Senate_jerseyvotes.m to be maximal voting power 
    sorted in order for table to be like-so   
    """
    votes = OrderedDict({})

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            votes[row[1]] = {
                'margin' : round(float(row[2]), 1),
                'jersey_votes' : round(float(row[3]), 1),
            }
    return votes

# **** made in response to apparent matlab issue processing poll margins 7/22/20
# *** can be deleted in future
def get_sen_margins(path):

    today = datetime.now()
    # julian_date = today.strftime("%j")

    margins = OrderedDict({})

    with open(path, 'r') as f:
        reader = csv.reader(f)

        i = 0
        for row in reader:
            julian_date = row[1]
            state_num = row[5]
            median_margin = row[3] 

            # Check that the scraping file is up-to-date
            if julian_date < today.strftime("%j"):
                break

            if i >0:
                margins[SENATE_STATES[int(state_num)]] = {
                    'margin': round(float(median_margin), 1)
                }
            i+=1
    return margins

def write_senate_jv_widget(names, margins, votes):
    ## append style + table start, iteratively add rows, append close
    html = style_and_start

    n = 0
    for key in votes:
        postal_code = key
        state_full = get_formatted_state(key, inverse=True)
        hyperlink = FIVETHIRTYEIGHT_SENATE_URL +  get_formatted_state(key, url_format=True)
        candiate_str = ""
        link_color = "#000000"
        # set leading candidate str based of margin as well as link color
        if margins[key]['margin'] > 0:
            candiate_str = names[key]['dem']
            link_color = "#1660CE"
        elif margins[key]['margin'] < 0:
            candiate_str = names[key]['rep']
            link_color = "#C62535"
        else: candiate_str = "Tie"

        margin = " +" + str(margins[key]['margin']).replace('-','')
        jersey_votes = votes[key]['jersey_votes']

        # only add districts above thresholds to widget table
        if votes[key]['jersey_votes'] >= 30 or n<6:
            html += "\n\t" + "<tr>"
            html += "\n\t\t" + f"<td>{postal_code}</td>"
            html += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
            html += "\n\t\t" + f"<td>{jersey_votes}</td>"
            html += "\n\t" + "</tr>"


        n += 1
    
    html += close

    path = os.path.join(DIR_PATH, 'Senate_JV_Widget.html')
    with open(path, 'w') as widget:
        widget.write(html)

def write_senate_table(names, margins, votes):
    sorted_margins = sort(margins)

    html_full = style_and_start2
    n = 0
    count = 0
    for key in sorted_margins:
        seats = D_SEATS_START +count
        postal_code = key
        state_full = get_formatted_state(key, inverse=True)
        hyperlink = FIVETHIRTYEIGHT_SENATE_URL +  get_formatted_state(key, url_format=True)
        candiate_str = ""
        link_color = "#000000"
        # set leading candidate str based of margin as well as link color
        if margins[key]['margin'] > 0:
            candiate_str = names[key]['dem']
            link_color = "#1660CE"
        elif margins[key]['margin'] < 0:
            candiate_str = names[key]['rep']
            link_color = "#C62535"
        else: candiate_str = "Tie"

        margin = " +" + str(margins[key]['margin']).replace('-','')
        jersey_votes = votes[key]['jersey_votes']


        # add all districts to full table    
        html_full += "\n\t" + "<tr>"
        html_full += "\n\t\t" + f"<td>{postal_code}</td>"
        html_full += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
        html_full += "\n\t\t" + f"<td>{jersey_votes}</td>"
        html_full += "\n\t\t" + f"<td>{seats}</td>"

        html_full += "\n\t" + "</tr>"

        n += 1
        count +=1
    
    html_full += close

    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, 'Senate_Table_Full.html')
    with open(path, 'w') as full:
        full.write(html_full)

# ======================================================================
# PRESIDENTIAL

# margin spread in which we consider polling to be tied (i.e. 0.5 for +-0.5 to be tie instead of Biden/Trump)
tie_threshold = 0.0

def get_ev_jerseyvotes(path):
    votes = OrderedDict({})

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #print(row[1] + " " + str(round(float(row[2]), 1)))
            if row[1] == "NJ":
                votes[row[1]] = {
                    'jersey_votes' : float(row[2])
                }
            else :
                votes[row[1]] = {
                    'jersey_votes' : round(float(row[2]), 1)
                }
    return votes

def get_ev_margins(path):
    margins = {}
    
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            margins[row[4]] = {
                'state'  : row[4],
                'margin' : round(float(row[1]),1)
            }
    return margins

def write_presidential_race_table(margins, votes):
    ## append style + table start, iteratively add rows, append close
    html = style_and_start
    
    n = 0

    for key in votes: 
        postal_code = key
        # state_full = get_formatted_state(key, inverse=True)
        state_full = key 
        if "1" in key or "2" in key or "3" in key:
            state_full = get_formatted_state(key, electoral_district=True)
        hyperlink = get_538_link(postal_code)
        candiate_str = ""
        link_color = "#000000"
        # set leading candidate str based of margin as well as link color
        if margins[key]['margin'] > 0:
            candiate_str = EV_CANDIDATES["dem"]
            link_color = "#1660CE"
        elif margins[key]['margin'] < 0:
            candiate_str = EV_CANDIDATES["rep"]
            link_color = "#C62535"
        else: candiate_str = "Tie"

        margin = " +" + str(margins[key]['margin']).replace('-','')
        jersey_votes = votes[key]['jersey_votes']
        ## force NJ to display 2 significant digits (value often quite small)
        if key == "NJ":
            jersey_votes = format(votes[key]['jersey_votes'], '.2g')

        # only add districts above thresholds to widget table
        if votes[key]['jersey_votes'] >= 50 or n<6 or key=="NJ":
            html += "\n\t" + "<tr>"
            html += "\n\t\t" + f"<td>{state_full}</td>"
            html += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
            html += "\n\t\t" + f"<td>{jersey_votes}</td>"
            html += "\n\t" + "</tr>"

        n += 1
    
    html += close

    path = os.path.join(DIR_PATH, 'Presidential_Race_Table.html')
    with open(path, 'w') as widget:
        widget.write(html)
    
def write_presidential_race_table_full(margins, votes):
    html_full = style_and_start

    n = 0

    for key in votes: 
        postal_code = key
        # state_full = get_formatted_state(key, inverse=True)
        state_full = key 
        if "1" in key or "2" in key or "3" in key:
            state_full = get_formatted_state(key, electoral_district=True)
        hyperlink = get_538_link(postal_code)
        candiate_str = ""
        link_color = "#000000"
        # set leading candidate str based of margin as well as link color
        if margins[key]['margin'] > 0:
            candiate_str = EV_CANDIDATES["dem"]
            link_color = "#1660CE"
        elif margins[key]['margin'] < 0:
            candiate_str = EV_CANDIDATES["rep"]
            link_color = "#C62535"
        else: candiate_str = "Tie"

        margin = " +" + str(margins[key]['margin']).replace('-','')
        jersey_votes = votes[key]['jersey_votes']
        ## force NJ to display 2 significant digits (value often quite small)
        if key == "NJ":
            jersey_votes = format(votes[key]['jersey_votes'], '.2g')
        
        # add all districts to full table
        html_full += "\n\t" + "<tr>"
        html_full += "\n\t\t" + f"<td>{state_full}</td>"
        html_full += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
        html_full += "\n\t\t" + f"<td>{jersey_votes}</td>"
        html_full += "\n\t" + "</tr>"

        n += 1
    
    html_full += close

    path = os.path.join(DIR_PATH, 'Presidential_Race_Table_Full.html')
    with open(path, 'w') as full:
        full.write(html_full)

# ======================================================================

def main():
    # SENATE
    sen_names = get_sen_candidates(SENATE_PRIORS_CSV)
    sen_margins = get_sen_margins(SENATE_POLLS_CSV)
    sen_votes = get_sen_jerseyvotes(SENATE_JERSEYVOTES_CSV)
    
    write_senate_jv_widget(sen_names, sen_margins, sen_votes)
    write_senate_table(sen_names, sen_margins, sen_votes)

    # PRESIDENTIAL
    ev_margins = get_ev_margins(EV_STATEPROBS_CSV)
    ev_votes = get_ev_jerseyvotes(EV_JERSEYVOTES_CSV)

    write_presidential_race_table(ev_margins, ev_votes)
    write_presidential_race_table_full(ev_margins, ev_votes)

if __name__ == "__main__":
    main()
