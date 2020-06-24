import csv
import os
from decimal import *
from state_code_util import *
from collections import OrderedDict

## EV_stateprobs.csv fields
## 0           1                       2                 3               4              5
## P(D win)    current medial margin  P(D + 2 Win)       P(D R+2 win)    postal code    november P(D win)

## districts not in EV_jerseyvotes n1 n2 n3 m1 m2

## EV_jerseyvotes.csv fields
## 0           1                       2            
## statenum    postal code             jerseyvotes

# margin spread in which we consider polling to be tied (i.e. 0.5 for +-0.5 to be tie instead of Biden/Trump)
tie_threshold = 0.0

fivethirtyeight = "https://projects.fivethirtyeight.com/polls/president-general/"

candidates = {
    "dem" : "Biden",
    "rep" : "Trump"
}

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
<table id="presidential-table">
    <tr> 
        <th colspan="1">State</th>
        <th colspan="1">Margin</th>
        <th colspan="1">Voter Power</th>
    </tr>"""

close = """
</table>
</div>"""


def get_jerseyvotes(path):
    votes = OrderedDict({})

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            #print(row[1] + " " + str(round(float(row[2]), 1)))
            votes[row[1]] = {
                'jersey_votes' : round(float(row[2]), 1)
            }
    return votes

def get_margins(path):
    margins = {}
    
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            margins[row[4]] = {
                'state'  : row[4],
                'margin' : round(float(row[1]),1)
            }
    return margins

def get_538_link(postal_code):
    return fivethirtyeight #+  get_formatted_state(key, url_format=True)



def main():
    dir_path = os.path.join(os.path.dirname(__file__), '..')

    path = os.path.join(dir_path, './matlab/outputs/EV_jerseyvotes.csv')
    votes = get_jerseyvotes(path)

    path = os.path.join(dir_path, './matlab/outputs/EV_stateprobs.csv')
    margins = get_margins(path)

    # for key in votes:
    #     ## set jerseyvote threshold here: defaulting to 20 jersey votes
    #     if votes[key]['jersey_votes'] >= 10:
    #         print(key + str(margins[key]['margin']))

    ## append style + table start, iteratively add rows, append close
    html = style_and_start

    for key in votes:
        ## set jerseyvote threshold here: defaulting to 10 jersey votes
        if votes[key]['jersey_votes'] >= 10:
            postal_code = key
            state_full = get_formatted_state(key, inverse=True)
            hyperlink = get_538_link(postal_code)
            candiate_str = ""
            link_color = "#000000"
            # set leading candidate str based of margin as well as link color
            if margins[key]['margin'] > 0:
                candiate_str = candidates["dem"]
                link_color = "#1660CE"
            elif margins[key]['margin'] < 0:
                candiate_str = candidates["rep"]
                link_color = "#C62535"
            else: candiate_str = "Tie"

            margin = " +" + str(margins[key]['margin']).replace('-','')
            jersey_votes = votes[key]['jersey_votes']

            html += "\n\t" + "<tr>"
            html += "\n\t\t" + f"<td>{state_full}</td>"
            html += "\n\t\t" + f"<td><a href= {hyperlink} style=color:{link_color}; >{candiate_str}{margin}</a> </td>"
            html += "\n\t\t" + f"<td>{jersey_votes}</td>"
            html += "\n\t" + "</tr>"
    
    html += close

    path = os.path.join(dir_path, './sidebar/Presidential_Race_Table.html')
    with open(path, 'w') as widget:
        widget.write(html)
    





if __name__ == "__main__":
    main()