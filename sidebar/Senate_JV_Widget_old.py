
import csv
import os
from decimal import *
from state_code_util import *
from collections import OrderedDict
from datetime import datetime

fivethirtyeight = "https://projects.fivethirtyeight.com/polls/senate/"

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
    </tr>"""

close = """
</table>
</div>"""

def get_candidates(path):
    candidates = {}
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates[row['code']] = {
                'dem' : row['dem'],
                'rep' : row['rep']
            }
    return candidates

# *** note *** currently relies on Senate_jerseyvotes.m to be maximal voting power 
# sorted in order for table to be like-so
def get_jerseyvotes(path):
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
def get_margins(path):

    hash = {
        1: 'AL',
        2: 'AK',
        3: 'AZ',
        4: 'CO',
        5: 'GA',
        6: 'GS',
        7: 'IA',
        8: 'KS',
        9: 'KY',
        10: 'ME',
        11: 'MI',
        12: 'MN',
        13: 'MT',
        14: 'NH',
        15: 'NM',
        16: 'NC',
        17: 'SC',
        18: 'TX',
        19: 'MS'}


    today = datetime.now()
    julian_date = today.strftime("%j")

    margins = OrderedDict({})

    with open(path, 'r') as f:
        reader = csv.reader(f)

        i = 0
        for row in reader:
            if row[1] < julian_date: break

            if i >0:
                margins[hash[int(row[5])]] = {
                    'margin': round(float(row[3]), 1)
                }
            i+=1

    return margins



def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    path = os.path.join(dir_path, '../scraping/outputs/2020.Senate.priors.csv')
    names = get_candidates(path)

    path = os.path.join(dir_path, '../scraping/outputs/2020.Senate.polls.median.csv')
    margins = get_margins(path)

    path = os.path.join(dir_path, '../matlab/outputs/Senate_jerseyvotes.csv')
    votes = get_jerseyvotes(path)

    ## append style + table start, iteratively add rows, append close
    html = style_and_start
    html_full = style_and_start

    n = 0

    for key in votes:
        postal_code = key
        state_full = get_formatted_state(key, inverse=True)
        hyperlink = fivethirtyeight +  get_formatted_state(key, url_format=True)
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

        # add all districts to full table    
        html_full += "\n\t" + "<tr>"
        html_full += "\n\t\t" + f"<td>{postal_code}</td>"
        html_full += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
        html_full += "\n\t\t" + f"<td>{jersey_votes}</td>"
        html_full += "\n\t" + "</tr>"

        n += 1
    
    html += close
    html_full += close

    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, 'Senate_JV_Widget_old.html')
    with open(path, 'w') as widget:
        widget.write(html)
    path = os.path.join(dir_path, 'Senate_Table_Full_old.html')
    with open(path, 'w') as full:
        full.write(html_full)



if __name__ == "__main__":
    main()

