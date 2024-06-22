import os
import csv 

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ======================================================================
# GLOBAL VARIABLES

dir_path = os.path.dirname(os.path.realpath(__file__))
FIVETHIRTYEIGHT_API_URL = 'https://projects.fivethirtyeight.com/polls/polls.json'

YEAR = 2024
START_DATE = datetime(year=YEAR, month=1, day=1)    
PRES_CANDS = [['Biden'], ['Trump']] # must be Dem, Rep order
DEM_CAND = 'Biden'
REP_CAND = 'Trump'

# ======================================================================
# MAIN 538 POLL SCRAPING / CLEANING

def clean_districts(polls):
    """
    NOTE: Helper function for get_all_polls. 

    Cleans poll data by adjusting percentages and dropping irrelevant 
    rows based on specific state districts (Maine and Nebraska). 
    
    Args:
    - polls (DataFrame): DataFrame with poll data.

    Returns:
    - polls (DataFrame): DataFrame with cleaned district poll data.
    """

    dropped = 0     # Counter for the number of dropped rows
    adjusted = 0    # Counter for the number of adjusted rows

    # Iterate through each row (poll)
    for index in polls.index: 
        # Check if the poll is associated with a specific district
        if polls.loc[index, 'district'] > 0:
            adjusted += 1

            # Check if the poll is of type 'president-general'
            if polls.loc[index, 'type'] == 'president-general':
                # Adjust percentages for Maine districts
                if polls.loc[index, 'state'] == "Maine":
                    if polls.loc[index, 'district'] == 1:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) - 10
                    elif polls.loc[index, 'district'] == 2:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) + 10
                    else: 
                        # Drop rows for invalid districts
                        polls = polls.drop(index)
                        dropped += 1

                # Adjust percentages for Nebraska districts
                elif polls.loc[index, 'state'] == "Nebraska":
                    if polls.loc[index, 'district'] == 1:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) - 6
                    elif polls.loc[index, 'district'] == 2:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) - 20
                    elif polls.loc[index, 'district'] == 3:
                        polls.loc[index, 'answers'][0]['pct'] = float(polls.loc[index, 'answers'][0]['pct']) + 26
                    else: 
                        # Drop rows for invalid districts
                        polls = polls.drop(index)
                        dropped += 1
                
                # Drop rows for states other than Maine or Nebraska
                else: 
                    polls = polls.drop(index)
                    dropped += 1
            
            # Drop rows for polls not of 'president-general' type
            else: 
                polls = polls.drop(index) 
                dropped += 1

    # Print summary of cleaning process
    print(f"Cleaning districts: Dropped {dropped}, Adjusted {adjusted - dropped}")

    return polls 

def get_all_polls(year):
    """
    Gets all available polls from the 538 API for the specified year.
    
    Args:
    - year (int): Specific (election) year.

    Returns:
    - all_polls (pandas.DataFrame): DataFrame with all polls in the 
        specified year.
    """
    all_polls = pd.read_json(FIVETHIRTYEIGHT_API_URL)
    
    # Convert dates to standard datetime format
    all_polls.loc[:, 'endDate'] = pd.to_datetime(all_polls['endDate'])
    all_polls.loc[:, 'startDate'] = pd.to_datetime(all_polls['startDate'])
    
    # Filter by election year and clean specific districts
    all_polls = all_polls[all_polls['endDate'] > datetime(year=year, month=1, day=1)]
    all_polls = clean_districts(all_polls)
   
    return all_polls

# ======================================================================
# ROW-BY-ROW POLL CLEANING

def parse_candidate(row, party, cand_list=None):
    """
    NOTE: Used for Senate and Presidential polls only.

    Parses a poll (row) to extract the candidate choice based on party 
    affiliation. Returns "parse_candidate_error" if the candidate is not 
    in the provided cand_list. 

    Args:
    - row (pandas.Series): A row of poll data with the 'answers' field.
    - party (str, optional): Party affiliation to filter the candidate choices. 
    - cand_list (list of lists, optional): A list containing two lists,
        the first for Dem candidate(s), the second for Rep candidate(s). 
        Used to verify the extracted candidate choice. Default is None.

    Returns: 
    - choice (str): The name of the candidate choice based on specified party.
    """
    choice = None

    # Extract the 'answers' from the row
    answers = row['answers']

    # Iterate through answers until choice is found
    for answer in answers:
        # Check if the candidate choice matches the specified party 
        # and (if applicable) is in the list of candidates
        if answer['party'] == party: 
            if party == 'Dem' and (cand_list is None or answer['choice'] in cand_list[0]): 
                choice = answer['choice']
                break   
            elif party == 'Rep' and (cand_list is None or answer['choice'] in cand_list[1]):
                choice = answer['choice']
                break 
    
    # If no candidate choice is found, return an error
    if not choice:
        # print("PARSE CANDIDATE ERROR IN {} FOR {}: {}".format(row['state'].upper(), party.upper(), answers))
        return "parse_candidate_error"

    # print(choice)
    return choice

def parse_dminusr(row, generic=False, dem_cand=None, rep_cand=None):
    """
    NOTE: Used for House, Senate, and Presidential polls.

    Parses a poll (row) to calculate the margin between the Dem and Rep 
    party/candidate.

    Args:
    - row (pandas.Series): A row of poll data with the 'answers' field.
    - generic (bool, optional): Whether or not the poll is generic (meaning for House). 
        Default is False.
    - dem_cand (str, optional: Name of Democratic candidate choice.
        Default is None (not needed for generic polls).
    - rep_cand (str, optional): Name of Republican candidate choice.
        Default if None (not needed for generic polls).
    
    Returns:
    - dminusr (float): Margin between the Dem and Rep candidates.
    """
    d_sum = 0
    r_sum = 0

    # Extract the 'answers' from the row
    answers = row['answers']

    # Iterate through answers and calculate polling sums
    if generic: 
        for answer in answers:
            if answer['choice'] == 'Dem':
                d_sum += float(answer['pct'])
            elif answer['choice'] == 'Rep':
                r_sum += float(answer['pct'])
    
    else: # dem_cand, rep_cand are not None
        for answer in answers:
            if answer['party'] == 'Dem' and answer['choice'] == dem_cand:
                d_sum += float(answer['pct'])
            elif answer['party'] == 'Rep' and answer['choice'] == rep_cand:
                r_sum += float(answer['pct'])

    # Calculate and return the margin
    return d_sum - r_sum

# ======================================================================
# COLLECTIVE POLL CLEANING

def get_polls_in_timespan(day, polls, dynamic_timespan=True):
    """
    NOTE: Helper function for filter_day_polls.

    Filters polls based on their end dates within a specified timespan
    (which may be dynamic).

    Args:
    - day (datetime.date): Reference day for determining the time span.
    - polls (pandas.DataFrame): DataFrame with poll data. 
    - dynamic_timespan (bool, optional): Whether to adjust the timespan 
        dynamically based on the current month. Default is True.

    Returns:
    - filtered_polls (pandas.DataFrame): DataFrame with the polls that 
        fall within the timespan.
    """
    current_month = datetime.today().month
    timespan = timedelta(weeks=2)

    if dynamic_timespan:
        # Adjust timespan based on the current_month
        if current_month < 9:       # Before September
            timespan = timedelta(weeks=4)
        elif current_month < 10:    # Before October
            timespan = timedelta(weeks=3)
        else:                       # October - November
            timespan = timedelta(weeks=2)

    # Filter polls based on end dates within the specified timespan
    filtered_polls = polls[(polls['endDate'] >= day - timespan)
        & (polls['endDate'] <= day)]
    
    return filtered_polls

def drop_duplicate_pollsters(polls):
    """
    NOTE: Helper function for filter_day_polls.

    Drops duplicate pollsters. Temporarily transforms 'population' fields
    to sort the DataFrame. Then, drops 'pollster' duplicates
    and reverts the temporary transformation. 

    Args:
    - polls (pandas.DataFrame): DataFrame with poll data.

    Returns:
    - polls (pandas.DataFrame): DataFrame with duplicate pollsters removed.
    """

    # Temporarily tranform 'population' categories for sorting
    # Likely Voters (LV), Registered Voters (RV), All Adults (A)
    polls.loc[polls['population'] == 'lv', 'population'] = '1lv'
    polls.loc[polls['population'] == 'rv', 'population'] = '2rv'
    polls.loc[polls['population'] == 'a', 'population'] = '3a'

    # Sort the DataFrame by 'population' and 'endDate' in descending order
    polls = polls.sort_values(by=['population']).sort_values(by=['endDate'], ascending=False)
    
    # Drop duplicates based on 'pollster' and 'endDate' columns, keeping the first occurrence
    polls = polls.drop_duplicates(['pollster', 'endDate'], keep='first')

    # Revert the transformation of 'population'
    polls.loc[polls['population'] == '1lv', 'population'] = 'lv'
    polls.loc[polls['population'] == '2rv', 'population'] = 'rv'
    polls.loc[polls['population'] == '3a', 'population'] = 'a'

    return polls

def clean_and_filter_polls(day, polls, dynamic_timespan=True):
    """
    NOTE: Used for House, Senate, and Presidential polls.

    Filters, sorts, and deduplicates polls within a specified (dynamic)
    time span. Returns the cleaned polls.

    Args:
    - day (datetime.date): Reference day for determining the time span.
    - polls (pandas.DataFrame): DataFrame with poll data.
    - dynamic_timespan (int): Number of weeks to consider for dynamic time span. Default is True.

    Returns:
    - final_polls (pandas.DataFrame): DataFrame with at least
        3 polls or polls from the last n weeks, whichever is more, 
        sorted by end date in descending order.
    """
    # Get polls within timespan based on end dates
    filtered_polls = get_polls_in_timespan(day=day, polls=polls, dynamic_timespan=dynamic_timespan)
    
    # Sort filtered polls by end date in descending order
    sorted_polls = filtered_polls.sort_values(by=['endDate'], ascending=False)
    
    # Drop duplicate polls and sort by end date
    deduped_polls = drop_duplicate_pollsters(sorted_polls).sort_values(by=['endDate'], ascending=False)

    # Get at least 3 polls or polls from the last N weeks, whichever is more data
    final_polls = deduped_polls
    if len(final_polls.index) < 3:
        # Get the three most recent from *all* polls
        filtered_all_polls = polls[polls['endDate'] <= day]
        sorted_all_polls = filtered_all_polls.sort_values(by=['endDate'], ascending=False)
        final_polls = drop_duplicate_pollsters(sorted_all_polls).sort_values(by=['endDate'], ascending=False).head(3)

    return final_polls

def write_state_day_stats(day, state, polls, file):
    """
    NOTE: Used for Senate and Presidential polls only.

    Calculates statistics based on poll data for a specified day and state.
    Writes them to a specified file (assumed TXT).

    Args:
    - day (datetime.date): Reference day for calculating statistics.
    - state (dict): State information (number, code, etc.)
    - polls (pandas.DataFrame): DataFrame with poll data.
    - file (file object): File object to write statistics to.

    Returns:
    - dict: Calculated statistics:
        - number of polls
        - Julian date
        - date of the most recent poll
        - median margin
        - median standard deviation
        - state number
        - state code
    """
    # Calculate the number of polls
    num_polls = len(polls.index)

    # Get the Julian date of the specified date
    julian_date = day.strftime("%j")

    # Parse state information
    state_num = int(state['num'])

    # Initialize default/prior values
    date_most_recent_poll = datetime(year=YEAR, month=1, day=1).strftime("%j")
    median_margin = float(state['prior'])
    median_std_dev = -999

    # If there are polls, update statistics
    if num_polls > 0:
        date_most_recent_poll = polls['endDate'].iloc[0].strftime("%j")

        x = pd.Series(polls['dminusr'])
        median_margin = x.median()
        median_abs_dev = x.sub(x.median()).abs().median()
        median_std_dev = median_abs_dev * 1.4826 # set multiplicative factor

    # Write the statistics to the specified file
    file.write('%-3d %-4s %-4s %-7.2f %-7.2f %-3d\n' % (num_polls, 
                                                       julian_date,
                                                       date_most_recent_poll, 
                                                       median_margin, 
                                                       median_std_dev,
                                                       state_num))
    
    # Return a dictionary with the calculated statistics
    return dict(num_polls=num_polls, 
                julian_date=julian_date, 
                date_most_recent_poll=date_most_recent_poll, 
                median_margin=median_margin, 
                median_std_dev=median_std_dev, 
                state_num=state_num)

# ======================================================================
# HOUSE ELECTION DATA

def process_house_polls(polls, start_date):
    """
    Filters and parses generic (House) polls. Calculates poll statistics 
    by day, and generates relevant TXT/CSV files.

    Args:
    - polls (pandas.DataFrame): DataFrame with generic poll data.
    - start_date (datetime.date): Start date for processing polls.

    Returns:
    - None: Generates TXT/CSV files.
    """
    # Filter 'generic-ballot' polls
    house_polls = polls[polls['type'] == 'generic-ballot']
    print("Number of 'generic-ballot' polls:", len(house_polls))

    # For each poll, calculate D-R margins
    # house_polls.loc[:, 'dminusr'] = house_polls.apply(lambda row: parse_dminusr(row, generic=True), axis=1)
    # June 2024: Getting rid of 'SettingWithCopyWarning' 
    house_polls_copy = house_polls.copy()
    house_polls_copy['dminusr'] = house_polls_copy.apply(lambda row: parse_dminusr(row, generic=True), axis=1)
    house_polls = house_polls_copy

    # --> Generic algorithm
    path = os.path.join(dir_path, f'outputs/{YEAR}.house.polls.median.txt') 
    all_output = []

    with open(path, 'w') as f:

        for idx in range((datetime.today() - start_date).days):

            # Filter polls for the current day
            day = datetime.today() - timedelta(days=idx)
            final_polls = clean_and_filter_polls(day=day, 
                                        polls=house_polls, 
                                        dynamic_timespan=False)

            # Calculate statistics and write to TXT file
            num_polls = len(final_polls.index)
            julian_date = day.strftime("%j")
            date_most_recent_poll = final_polls['endDate'].iloc[0].strftime("%j")
            median_margin = final_polls['dminusr'].median()

            x = pd.Series(final_polls['dminusr'])
            median_abs_dev = x.sub(x.median()).abs().median() 
            median_std_dev = median_abs_dev * 1.4826 # set multiplicative factor

            f.write('%-3d %-4s %-4s %-7.2f %-7.2f \n' % (num_polls, 
                                                        julian_date,
                                                        date_most_recent_poll, 
                                                        median_margin, 
                                                        median_std_dev))

            # Append statistics to all_output list
            all_output.append(dict(num_polls=num_polls, 
                                   julian_date=julian_date, 
                                   date_most_recent_poll=date_most_recent_poll, 
                                   median_margin=median_margin,
                                   median_std_dev=median_std_dev))

    # Convert all_output to DataFrame and write to CSV file
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, f'outputs/{YEAR}.house.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

# ======================================================================
# SENATE ELECTION DATA

def get_sen_states_cands(): 
    """
    Reads from the Senate priors CSV. Extracts data for the Senate
    election states, as well as their Democratic and Republican candidates.

    Returns: 
    - tuple:
        - sen_states (list of dicts): Information about Senate races in
            different states: code, name, num, prior, dem, rep.
        - dem_cands (list): Democratic candidate names for all states.
        - rep_cands (list): Republican candidate names for all states.
    """
    sen_states = []
    
    path = os.path.join(dir_path, f'{YEAR}.Senate.priors.csv')
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sen_states.append(row) 

    cand_list = pd.DataFrame(sen_states)
    dem_cands = cand_list['dem'].tolist()
    rep_cands = cand_list['rep'].tolist()

    return [sen_states, dem_cands, rep_cands]

def process_senate_polls(polls, start_date, sen_states, sen_cands):
    """
    Filters, parses, and cleans Senate polls. Calculates poll statistics 
    by state and day, and generates relevant TXT/CSV files.

    Args:
    - polls (pandas.DataFrame): DataFrame with Senate poll data.
    - start_date (datetime.date): Start date for processing polls.
    - sen_states (list of dicts): Information about Senate races by state.
    - sen_cands (list of lists): Two lists: Democratic and Republican 
        candidates(s).

    Returns:
    - None: Generates TXT/CSV files.
    """
    # Filter 'senate' polls
    sen_polls = polls[polls['type'] == 'senate']
    print("Number of 'senate' polls:", len(sen_polls))

    # For each poll, parse Dem/Rep candidates
    sen_polls = sen_polls.assign(
        dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem', cand_list=sen_cands),
        rep_cand=lambda x: x.apply(parse_candidate, axis=1, party='Rep', cand_list=sen_cands)
    )
    
    # Cleaning: Remove rows with parse candidate errors
    sen_polls = sen_polls[(sen_polls['dem_cand'] != "parse_candidate_error") & (sen_polls['rep_cand'] != "parse_candidate_error")]

    print("Number of polls after cleaning:", len(sen_polls))

    # For each poll, calculate D-R margins
    sen_polls['dminusr'] = sen_polls.apply(lambda row: parse_dminusr(row, dem_cand=row['dem_cand'], rep_cand=row['rep_cand']), axis=1)

    # --> Generic algorithm
    path = os.path.join(dir_path, f'outputs/{YEAR}.Senate.polls.median.txt')
    all_output = [] 

    with open(path, 'w') as f:

        for idx in range((datetime.today() - start_date).days):
            # Filter polls for the current day
            day = datetime.today() - timedelta(days=idx)

            # Filter polls for specific states
            for state in sen_states:
                sen_polls_state = sen_polls[sen_polls['state'] == state['name']] 
                final_polls = clean_and_filter_polls(day=day, 
                                            polls=sen_polls_state)

                # Calculate statistics (dict) and write to TXT file
                row = write_state_day_stats(day=day,
                                            state=state, 
                                            polls=final_polls, 
                                            file=f)
                
                # Append statistics to all_output list
                all_output.append(row)

    # Convert all_output to DataFrame and write to CSV file
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, f'outputs/{YEAR}.Senate.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

# ======================================================================
# PRESIDENTIAL ELECTION DATA

def get_pres_states(): 
    """
    Reads from the EV priors CSV. Extracts data for the Presidential 
    election states (all 50 states + D.C.).

    Returns:
    - states (list of dicts): Information about Presidential race in
        different states: code, name, num, prior.
    """
    states = [] 

    path = os.path.join(dir_path, f'{YEAR}.EV.priors.csv')
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            states.append(row)
    
    return states

def process_presidential_polls(polls, start_date, states):
    """
    Filters, parses, and cleans Presidential polls. Calculates poll statistics 
    by state and day, and generates relevant TXT/CSV files.

    Args:
    - polls (pandas.DataFrame): DataFrame with Presidential poll data.
    - start_date (datetime.date): Start date for processing polls.
    - states (list of dicts): Information about Presidential race by state.

    Returns:
    - None: Generates TXT/CSV files.
    """
    # Filter 'president-general' polls
    pres_polls = polls[polls['type'] == 'president-general']
    print("Number of 'president-general' polls:", len(pres_polls))

    # For each poll, parse Dem/Rep candidates
    pres_polls = pres_polls.assign(
        dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem', cand_list=PRES_CANDS),
        rep_cand=lambda x: x.apply(parse_candidate, axis=1, party='Rep', cand_list=PRES_CANDS)
    )

    # Cleaning: Remove rows with other match-ups and national polls
    pres_polls = pres_polls[(pres_polls['dem_cand'] == DEM_CAND) & (pres_polls['rep_cand'] == REP_CAND)]
    pres_polls = pres_polls[pres_polls['state'] != 'National']

    print("Number of polls after cleaning:", len(pres_polls))

    # For each poll, calculate D-R margins
    pres_polls['dminusr'] = pres_polls.apply(lambda row: parse_dminusr(row, dem_cand=DEM_CAND, rep_cand=REP_CAND), axis=1)

    # --> Generic algorithm
    path = os.path.join(dir_path, f'outputs/{YEAR}.EV.polls.median.txt')
    all_output = []

    with open(path, 'w') as f:

        for idx in range((datetime.today() - start_date).days):

            # Filter polls for the current day
            day = datetime.today() - timedelta(days=idx)

            # Filter polls for specific states
            for state in states:
                pres_polls_state = pres_polls[pres_polls['state'] == state['name']] 
                final_polls = clean_and_filter_polls(day=day, 
                                            polls=pres_polls_state)

                # Calculate statistics (dict) and write to TXT file
                row = write_state_day_stats(day=day, 
                                            state=state, 
                                            polls=final_polls, 
                                            file=f)
                
                # Append statistics to all_output list
                all_output.append(row)
    
    # Convert all_output to DataFrame and write to CSV file
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, f'outputs/{YEAR}.EV.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

# ======================================================================

def main():
    print("Scraping all 538 API polls...")
    all_polls = get_all_polls(YEAR)
    print("Total number of polls:", len(all_polls))

    # HOUSE
    print("Generating House medians...")
    process_house_polls(all_polls, START_DATE)
    print("Done generating House medians...")

    # SENATE
    print("Generating Senate medians...")
    sen_states = get_sen_states_cands()[0]
    sen_cands = get_sen_states_cands()[1:]
    # print("sen_states:", sen_states)
    # print("sen_cands:", sen_cands)
    process_senate_polls(all_polls, START_DATE, sen_states, sen_cands)
    print("Done generating Senate medians...")

    # PRESIDENTIAL
    print("Generating Presidential medians...")
    pres_states = get_pres_states() 
    # print("pres_states:", pres_states)
    process_presidential_polls(all_polls, START_DATE, pres_states)
    print("Done generating Presidential medians...")

if __name__ == '__main__':
    main()