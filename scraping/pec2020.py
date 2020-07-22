# Author: Lucas Manning <lucassm@princeton.edu> 2020
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for non-commericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu

import requests
import os
import csv
import pandas as pd
from datetime import datetime, timedelta

states = []
sen_states = []
start_date = datetime(year=2020, month=3, day=1)
dir_path = os.path.dirname(os.path.realpath(__file__))

def parse_candidate(row, party='Dem'):
    answer_group = row['answers']
    choice = next((answer for answer in answer_group if answer['party'] == party), None)
    if choice is None:
        print("parse candiate error: " + str(answer_group))
        return "parse_candiate_error"

    return choice['choice'] 

def parse_dminusr(row, generic=False):
    answer_group = row['answers']
    d_sum = 0
    r_sum = 0

    keyword = 'party'
    if generic:
        keyword = 'choice'

    for answer in answer_group:
        if answer[keyword] == 'Dem':
            d_sum += float(answer['pct'])
        elif answer[keyword] == 'Rep':
            r_sum += float(answer['pct'])

    return d_sum - r_sum 

def drop_duplicate_pollsters(df):
    # this allows us to sort these in the order we want for deletion
    df.loc[df['population'] == 'lv', 'population'] = '1lv'
    df.loc[df['population'] == 'rv', 'population'] = '2rv'
    df.loc[df['population'] == 'a', 'population'] = '3a'

    df = df.sort_values(by=['population']).sort_values(by=['endDate'], ascending=False).drop_duplicates(['pollster'], keep='first')

    df.loc[df['population'] == '1lv', 'population'] = 'lv'
    df.loc[df['population'] == '2rv', 'population'] = 'rv'
    df.loc[df['population'] == '3a', 'population'] = 'a'

    return df

def get_polls_in_timespan(day=None, polls=None, dynamic_timespan=True):
    current_month = datetime.today().month
    timespan = timedelta(weeks=2)

    if dynamic_timespan:
        # before september
        if current_month < 9:
            timespan = timedelta(weeks=4)
        # before october
        elif current_month < 10:
            timespan = timedelta(weeks=3)
        # october-november
        else:
            timespan = timedelta(weeks=2)

    # within timespan
    filtered_polls = polls[(polls['endDate'] >= day - timespan)
        & (polls['endDate'] <= day)]
    
    return filtered_polls

def clean_and_filter_polls(day=None, polls=None, state=None, dynamic_timespan=True):
    if state and state['name'] != 'Georgia-Special':
        polls = polls[(polls['dem_cand'] == state['dem']) & (polls['rep_cand'] == state['rep'])]

    filtered_polls = get_polls_in_timespan(day=day, polls=polls, dynamic_timespan=dynamic_timespan)
    # sort by date
    sorted_polls = filtered_polls.sort_values(by=['endDate'], ascending=False)
    # one poll per pollster: preference lv > rv > a
    deduped_polls = drop_duplicate_pollsters(sorted_polls).sort_values(by=['endDate'], ascending=False)

    # 3 polls or last n weeks, whichever is more data
    final_polls = deduped_polls
    if len(final_polls.index) < 3:
        # just grab all the polls and get the three most recent
        filtered_polls = polls[polls['endDate'] <= day]
        sorted_polls = filtered_polls.sort_values(by=['endDate'], ascending=False)
        final_polls = drop_duplicate_pollsters(sorted_polls).sort_values(by=['endDate'], ascending=False).head(3)
    
    return final_polls

def write_state_day_stats(day=None, state=None, polls=None, file=None):
    num_polls = len(polls.index)
    julian_date = day.strftime("%j")
    state_num = int(state['num'])
    # if no polls, use the prior as a poll with the date at jan 1st
    date_most_recent_poll = datetime(year=2020, month=1, day=1).strftime("%j")
    median_margin = float(state['prior'])
    esd = -999

    if num_polls > 0:
        date_most_recent_poll = polls['endDate'].iloc[0].strftime("%j")
        median_margin = polls['dminusr'].median()
        esd = polls['dminusr'].mad() * 1.4826

    file.write('%-3d %-4s %-7.2f %-7.2f %-4s %-3d\n' % (num_polls, date_most_recent_poll, median_margin, 
        esd, julian_date, state_num))
    
    return dict(num_polls=num_polls, julian_date=julian_date, date_most_recent_poll=date_most_recent_poll, median_margin=median_margin, esd=esd, state_num=state_num)

def presidential(polls):
    pres_polls = polls[polls['type'] == 'president-general']
    pres_polls = pres_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1), 
        dem_cand=lambda x: x.apply(parse_candidate, axis=1))
    pres_polls = pres_polls[pres_polls['dem_cand'] == 'Biden']
    # exclude national polls
    pres_polls = pres_polls[pres_polls['state'] != 'National']
    
    all_output = []
    path = os.path.join(dir_path, 'outputs/2020.EV.polls.median.txt')
    f = open(path, 'w')
    for idx in range((datetime.today() - start_date).days):
        for state in states:
            pres_polls_state = pres_polls[pres_polls['state'] == state['name']] 
            day = datetime.today() - timedelta(days=idx)
            
            final_polls = clean_and_filter_polls(day=day, polls=pres_polls_state)
            row = write_state_day_stats(day=day, state=state, polls=final_polls, file=f)
            all_output.append(row)
    
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, 'outputs/2020.EV.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

    f.close()

def senate(polls):
    sen_polls = polls[polls['type'] == 'senate']
    sen_polls = sen_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1),
        dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem'),
        rep_cand=lambda x: x.apply(parse_candidate, axis=1, party='Rep'))

    all_output = [] 
    path = os.path.join(dir_path, 'outputs/2020.Senate.polls.median.txt')
    f = open(path, 'w')
    for idx in range((datetime.today() - start_date).days):
        for state in sen_states:
            sen_polls_state = None 

            if state['name'] == 'Georgia-Special':
                sen_polls_state = sen_polls[(sen_polls['state'] == 'Georgia') & (sen_polls['seat_name'] == 'Class III')]
            elif state['name'] == 'Georgia':
                sen_polls_state = sen_polls[(sen_polls['state'] == 'Georgia') & (sen_polls['seat_name'] == 'Class II')]
            elif state['name'] == 'Kentucky':
                sen_polls_state = sen_polls[(sen_polls['state'] == 'Kentucky') & (sen_polls['dem_cand'] == 'McGrath')]
            else:
                sen_polls_state = sen_polls[sen_polls['state'] == state['name']] 

            day = datetime.today() - timedelta(days=idx)

            final_polls = clean_and_filter_polls(day=day, state=state, polls=sen_polls_state)
            row = write_state_day_stats(day=day, state=state, polls=final_polls, file=f)
            all_output.append(row)

    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, 'outputs/2020.Senate.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

    f.close()

def generic(polls):
    gen_polls = polls[polls['type'] == 'generic-ballot']
    gen_polls = gen_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1, generic=True))

    path = os.path.join(dir_path, 'outputs/2020.generic.polls.median.txt')
    f = open(path, 'w')
    all_output = []
    for idx in range((datetime.today() - start_date).days):
        day = datetime.today() - timedelta(days=idx)

        final_polls = clean_and_filter_polls(day=day, polls=gen_polls, dynamic_timespan=False)

        num_polls = len(final_polls.index)
        julian_date = day.strftime("%j")
        date_most_recent_poll = final_polls['endDate'].iloc[0].strftime("%j")
        median_margin = final_polls['dminusr'].median()
        esd = final_polls['dminusr'].mad() * 1.4826

        all_output.append(dict(num_polls=num_polls, julian_date=julian_date, date_most_recent_poll=date_most_recent_poll, median_margin=median_margin, esd=esd))

        f.write('%-3d %-4s %-7.2f %-7.2f %-4s\n' % (num_polls, date_most_recent_poll, median_margin, 
            esd, julian_date))
    
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, 'outputs/2020.generic.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

    f.close()

def clean_districts(polls):
    dropped = 0
    adjusted = 0

    for index in polls.index: 
        # get all polls with a specified district
        if polls.loc[index, 'district'] > 0:
            adjusted += 1
            if polls.loc[index, 'type'] == 'president-general':
                # Maine: District 1 subtract 10, District 2 add 10 to convert to statewide
                if polls.loc[index, 'state'] == "Maine":
                    if polls.loc[index, 'district'] == 2:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) + 10
                    elif polls.loc[index, 'district'] == 1:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) - 10
                    else: 
                        polls = polls.drop(index)
                        dropped+=1

                # Nebraska: District 1 subtract 6, District 2 subtract 20, District 3 add 26 to convert to statewide
                elif polls.loc[index, 'state'] == "Nebraska":
                    if polls.loc[index, 'district'] == 1:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) -6
                    elif polls.loc[index, 'district'] == 2:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) - 20
                    elif polls.loc[index, 'district'] == 3:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) + 26
                    else: 
                        polls = polls.drop(index)
                        dropped+=1
                else: 
                    polls = polls.drop(index)
                    dropped+=1
            else: 
                polls = polls.drop(index) 
                dropped+=1

    print(f"District Clean: Dropped {dropped}  Adjusted {adjusted - dropped}")

    return polls 


def main():
    data_url = 'https://projects.fivethirtyeight.com/polls/polls.json'
    all_polls = pd.read_json(data_url)
    all_polls.loc[:, 'endDate'] = pd.to_datetime(all_polls['endDate'])
    all_polls.loc[:, 'startDate'] = pd.to_datetime(all_polls['startDate'])
    all_2020_polls = all_polls[all_polls['endDate'] > datetime(year=2020, month=1, day=1)]
    all_2020_polls = clean_districts(all_2020_polls)


    path = os.path.join(dir_path, '2020.Senate.priors.csv')
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sen_states.append(row)

    path = os.path.join(dir_path, '2020.EV.priors.csv')
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            states.append(row)

    print('Generating presidential medians...')
    presidential(all_2020_polls)
    print('Generating House medians...')
    generic(all_2020_polls)
    print('Generating Senate medians...')
    senate(all_2020_polls)

if __name__ == '__main__':
    main()