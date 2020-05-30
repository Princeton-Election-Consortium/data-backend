# Author: Lucas Manning <lucassm@princeton.edu> 2020
#
# Script written for election.princeton.edu run by Samuel S.-H. Wang under
# noncommercial-use-only license:
# You may use or modify this software, but only for non-commericial purposes.
# To seek a commercial-use license, contact sswang@princeton.edu

import requests
import pandas as pd
from datetime import datetime, timedelta
import csv

states = []
sen_states = []
start_date = datetime(year=2020, month=3, day=1)

def parse_candidate(row, party='Dem'):
    answer_group = row['answers']
    choice = next(answer for answer in answer_group if answer['party'] == party)
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

def presidential(polls):
    pres_polls = polls[polls['type'] == 'president-general']
    pres_polls = pres_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1), 
        dem_cand=lambda x: x.apply(parse_candidate, axis=1))
    pres_polls = pres_polls[pres_polls['dem_cand'] == 'Biden']
    # exclude national polls
    pres_polls = pres_polls[pres_polls['state'] != 'National']

    f = open('matlab/2020.EV.polls.median.txt', 'w')
    for idx in range((datetime.today() - start_date).days):
        for state in states:
            pres_polls_state = pres_polls[pres_polls['state'] == state['name']] 
            day = datetime.today() - timedelta(days=idx)
            
            final_polls = clean_and_filter_polls(day=day, polls=pres_polls_state)
            write_state_day_stats(day=day, state=state, polls=final_polls, file=f)
    f.close()

def senate(polls):
    sen_polls = polls[polls['type'] == 'senate']
    sen_polls = sen_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1),
        dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem'),
        rep_cand=lambda x: x.apply(parse_candidate, axis=1, party='Rep'))
    
    f = open('matlab/2020.Senate.polls.median.txt', 'w')
    for idx in range((datetime.today() - start_date).days):
        for state in sen_states:
            sen_polls_state = None 
            if state['name'] == 'Georgia-Special':
                sen_polls_state = sen_polls[(sen_polls['state'] == 'Georgia') & (sen_polls['seat_name'] == 'Class III')]
            elif state['name'] == 'Georgia':
                sen_polls_state = sen_polls[(sen_polls['state'] == 'Georgia') & (sen_polls['seat_name'] == 'Class II')]
            else:
                sen_polls_state = sen_polls[sen_polls['state'] == state['name']] 

            day = datetime.today() - timedelta(days=idx)

            final_polls = clean_and_filter_polls(day=day, state=state, polls=sen_polls_state)
            write_state_day_stats(day=day, state=state, polls=final_polls, file=f)
    f.close()

def generic(polls):
    gen_polls = polls[polls['type'] == 'generic-ballot']
    gen_polls = gen_polls.assign(dminusr=lambda x: x.apply(parse_dminusr, axis=1, generic=True))

    f = open('matlab/2020.generic.polls.median.txt', 'w')
    for idx in range((datetime.today() - start_date).days):
        day = datetime.today() - timedelta(days=idx)

        final_polls = clean_and_filter_polls(day=day, polls=gen_polls, dynamic_timespan=False)

        num_polls = len(final_polls.index)
        julian_date = day.strftime("%j")
        date_most_recent_poll = final_polls['endDate'].iloc[0].strftime("%j")
        median_margin = final_polls['dminusr'].median()
        esd = final_polls['dminusr'].mad() * 1.4826

        f.write('%-3d %-4s %-7.2f %-7.2f %-4s\n' % (num_polls, date_most_recent_poll, median_margin, 
            esd, julian_date))

    f.close()

def main():
    data_url = 'https://projects.fivethirtyeight.com/polls/polls.json'
    all_polls = pd.read_json(data_url)
    all_polls.loc[:, 'endDate'] = pd.to_datetime(all_polls['endDate'])
    all_polls.loc[:, 'startDate'] = pd.to_datetime(all_polls['startDate'])
    all_2020_polls = all_polls[all_polls['endDate'] > datetime(year=2020, month=1, day=1)]

    with open("matlab/2020.Senate.priors.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sen_states.append(row)

    with open("matlab/2020.EV.priors.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            states.append(row)

    print("Generating presidential medians...")
    presidential(all_2020_polls)
    print("Generating House medians...")
    generic(all_2020_polls)
    print("Generating Senate medians...")
    senate(all_2020_polls)

if __name__ == '__main__':
    main()