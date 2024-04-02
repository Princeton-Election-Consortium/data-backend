import os
import csv 
import pandas as pd
from datetime import datetime, timedelta


states = [] 
sen_states = []
dem_cands = []
rep_cands = []

start_date = datetime(year=2024, month=1, day=1)
dir_path = os.path.dirname(os.path.realpath(__file__))

FIVETHIRTYEIGHT_API_URL = 'https://projects.fivethirtyeight.com/polls/polls.json'
start_date = datetime(year=2024, month=1, day=1)

def parse_candidate(row, party='Dem'):
    """
    Parse each row 
    
    Example answer group
    [{'choice': 'Justice', 'pct': '54.0', 'party': 'Rep', 'incumbent': False}, {'choice': 'Mooney', 'pct': '16.7', 'party': 'Rep', 'incumbent': False}]
    
    Usage:
    dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem'
    """
    answer_group = row['answers']
    
    choice = None

    # Iterate through each answer in the answer group
    for answer in answer_group:
        if party == 'Dem':
        # if party == 'Dem' and answer['choice'] in dem_cands:
            choice = answer['choice']
            break   # Stop iterating once choice is found
        if party == 'Rep':
        # elif party == 'Rep' and answer['choice'] in rep_cands: 
            choice = answer['choice']
            break   # Stop iterating once choice is found
    
    # If no candidate choice is found, return an error
    if not choice:
        print("parse candiate error: " + str(answer_group))
        return "parse_candidate_error"

    return choice

def parse_dminusr(row, generic=False):
    """
    Parses 'dminusr' values for a poll row.

    Args:
        row (Series): Poll data row.
        generic (bool): Whether or not the poll is generic.
    
    Returns:
        dminusr (float): Margin between Dem and Rep candidate.

    """
    # Determine keyword based on generic flag
    keyword = 'party' if not generic else 'choice'
    
    d_sum = 0
    r_sum = 0

    # Iterate through answer group in given poll
    for answer in row['answers']:
        # Calculate sums based on party/choice
        if answer[keyword] == 'Dem':
            d_sum += float(answer['pct'])
        elif answer[keyword] == 'Rep':
            r_sum += float(answer['pct'])

    # Calculate and return 'dminusr'
    return d_sum - r_sum 

def get_polls_in_timespan(day=None, polls=None, dynamic_timespan=True):
    """
    Filters polls based on their end dates within a specified timespan 

    day: Reference day for which the timespan is calculated
    polls: DataFrame with poll data
    dynamic_timespan: Whether to adjust the timespan dynamically based on the current month

    Returns the filtered DataFrame with the polls that fall within the timespan
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

def drop_duplicate_pollsters(df):

    # Temporarily sort 'population' categories for sorting
    # Registered Voters (RV), Likely Voters (LV), All Adults (A)
    df.loc[df['population'] == 'lv', 'population'] = '1lv'
    df.loc[df['population'] == 'rv', 'population'] = '2rv'
    df.loc[df['population'] == 'a', 'population'] = '3a'

    # Sort the DataFrame by 'population' and 'endDate' in descending order
    df = df.sort_values(by=['population']).sort_values(by=['endDate'], ascending=False)
    
    # Drop duplicates based on 'pollster' column, keeping the first occurrence
    df = df.drop_duplicates(['pollster'], keep='first')

    # Revert the transformation of 'population'
    df.loc[df['population'] == '1lv', 'population'] = 'lv'
    df.loc[df['population'] == '2rv', 'population'] = 'rv'
    df.loc[df['population'] == '3a', 'population'] = 'a'

    return df

def clean_and_filter_polls(day=None, polls=None, state=None, dynamic_timespan=True):
    """
    TODO: Remove state arg?
    """
    # if state and state['name'] != 'Georgia-Special':
    #     polls = polls[(polls['dem_cand'] == state['dem']) & (polls['rep_cand'] == state['rep'])]

    # Get polls within timespan
    filtered_polls = get_polls_in_timespan(day=day, polls=polls, dynamic_timespan=dynamic_timespan)
    
    # Sort filtered polls by end date in descending order
    sorted_polls = filtered_polls.sort_values(by=['endDate'], ascending=False)
    
    # Drop duplicate polls and sort by end date
    deduped_polls = drop_duplicate_pollsters(sorted_polls).sort_values(by=['endDate'], ascending=False)

    # Get at least 3 polls or polls from the last n weeks, whichever is more
    final_polls = deduped_polls
    if len(final_polls.index) < 3:
        # Get the three most recent from all the polls
        filtered_polls = polls[polls['endDate'] <= day]
        sorted_polls = filtered_polls.sort_values(by=['endDate'], ascending=False)
        final_polls = drop_duplicate_pollsters(sorted_polls).sort_values(by=['endDate'], ascending=False).head(3)

    return final_polls

def write_state_day_stats(day=None, state=None, polls=None, file=None):
    '''
    Writes statistical information about election polls for a specific state on a particular day.
    Writes to a file.
    '''
    # Calculate the nmber of polls
    num_polls = len(polls.index)

    # Get the Julian date of the specified date
    julian_date = day.strftime("%j")

    # Get the state number from state information
    state_num = int(state['num'])

    # Initialize default/prior values
    date_most_recent_poll = datetime(year=2024, month=1, day=1).strftime("%j")
    median_margin = float(state['prior'])
    est_std_dev = -999

    # If there are polls, update statistics
    if num_polls > 0:
        date_most_recent_poll = polls['endDate'].iloc[0].strftime("%j")
        median_margin = polls['dminusr'].median()
        # Deprecated - Returns the mean absolute deviation of the values
        # est_std_dev = polls['dminusr'].mad() * 1.4826
        est_std_dev = polls['dminusr'].sub(polls['dminusr'].mean()).abs().mean()

    # Write the statistics to the specified file
    file.write('%-3d %-4s %-7.2f %-7.2f %-4s %-3d\n' % (num_polls, date_most_recent_poll, median_margin, 
        est_std_dev, julian_date, state_num))
    
    # Return a dictionary with the calculated statistics
    return dict(num_polls=num_polls, 
                julian_date=julian_date, 
                date_most_recent_poll=date_most_recent_poll, 
                median_margin=median_margin, 
                est_std_dev=est_std_dev, 
                state_num=state_num)



# ======================================================================

def process_house_polls(polls, start_date):
    # Filter 'house' polls
    print("Number of polls before filtering:", len(polls))
    house_polls = polls[polls['type'] == 'generic-ballot']
    print("Number of polls after filtering:", len(house_polls))

    # Calculate 'dminusr' values for the house polls DataFrame
    # TODO: Fix syntax
    house_polls.loc[:, 'dminusr'] = house_polls.apply(lambda row: parse_dminusr(row, generic=True), axis=1)

    # Open file for writing
    path = os.path.join(dir_path, 'outputs/2024.house.polls.median.txt')
    all_output = []

    with open(path, 'w') as f:

        # Process polls for each day starting from start_date
        for idx in range((datetime.today() - start_date).days):
            day = datetime.today() - timedelta(days=idx)

            # Clean and filter polls for the current day
            final_polls = clean_and_filter_polls(day=day, 
                                                 polls=house_polls, 
                                                 dynamic_timespan=False)

            # Calculate statistics
            num_polls = len(final_polls.index)
            julian_date = day.strftime("%j")
            date_most_recent_poll = final_polls['endDate'].iloc[0].strftime("%j")
            median_margin = final_polls['dminusr'].median()
            # esd = final_polls['dminusr'].mad() * 1.4826
            est_std_dev = final_polls['dminusr'].sub(final_polls['dminusr'].mean()).abs().mean()

            # Append statistics to all_output_list
            all_output.append(dict(num_polls=num_polls, 
                                   julian_date=julian_date, 
                                   date_most_recent_poll=date_most_recent_poll, 
                                   median_margin=median_margin,
                                   est_std_dev=est_std_dev))

            # Write statistics to file
            f.write('%-3d %-4s %-4s %-7.2f %-7.2f \n' % (num_polls, 
                julian_date,
                date_most_recent_poll, 
                median_margin, 
                esd))
    
    # Convert all_output to DataFrame and write to CSV file
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, 'outputs/2024.house.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

    print("Done generating House medians...")

def process_senate_polls(polls, start_date):
    # Filter 'senate' polls
    print("Number of polls before filtering:", len(polls))
    sen_polls = polls[polls['type'] == 'senate']
    print("Number of polls after filtering:", len(sen_polls))

    # Parse 'dminusr', Democratic candidate, and Republican candidate for each poll
    # TODO: Check parse_candidate
    sen_polls = sen_polls.assign(
        dminusr=lambda x: x.apply(parse_dminusr, axis=1),
        dem_cand=lambda x: x.apply(parse_candidate, axis=1, party='Dem'),
        rep_cand=lambda x: x.apply(parse_candidate, axis=1, party='Rep'))
    
    # Remove rows with parse candidate errors
    sen_polls = sen_polls[(sen_polls['dem_cand'] != "parse_candiate_error") & (sen_polls['rep_cand'] != "parse_candiate_error")]
    
    print(sen_polls)

    # Open file for writing
    path = os.path.join(dir_path, 'outputs/2024.Senate.polls.median.txt')
    all_output = [] 

    with open(path, 'w') as f:

        # Process polls for each day starting from start_date
        for idx in range((datetime.today() - start_date).days):
            day = datetime.today() - timedelta(days=idx)

            # Special handling for Senate states
            for state in sen_states:

                sen_polls_state = sen_polls[sen_polls['state'] == state['name']] 

                # Clean and filter polls for the current day
                final_polls = clean_and_filter_polls(day=day, 
                                                    polls=sen_polls_state)

                # Write state-day statistics to file and append to all_output
                row = write_state_day_stats(day=day,
                                            state=state, 
                                            polls=final_polls, 
                                            file=f)
                all_output.append(row)

    # Convert all_output to DataFrame and write to CSV file
    df = pd.DataFrame(all_output)
    path = os.path.join(dir_path, 'outputs/2024.Senate.polls.median.csv')
    df.to_csv(path, index=False, float_format='%.2f')

    print("Done generating Senate medians...")

def process_presidential_polls(polls):
    '''
    Process and aggregate presidential election polls data.
    Generate a CSV file with the aggregated results.
    '''
    # Filter polls for the 'president-general' type
    pres_polls = polls[polls['type'] == 'president-general']

    # Extract and add additional columns using custom functions
    pres_polls = pres_polls.assign(
        dminusr=lambda x: x.apply(parse_dminusr, axis=1), 
    #     dem_cand=lambda x: x.apply(parse_candidate, axis=1)
    )

    # Filter polls for the 'Biden' candidate
    # pres_polls = pres_polls[pres_polls['dem_cand'] == 'Biden']
   
    # Exclude national polls
    # pres_polls = pres_polls[pres_polls['state'] != 'National']

    print(pres_polls)
    print(pres_polls.columns)
    
    
    all_output = []
    
    # Write to another file
    path = os.path.join(dir_path, 'outputs/2024.EV.polls.median.test.txt')
    with open(path, 'w') as f:
        for idx in range((datetime.today() - start_date).days):
            for state in states:
                pres_polls_state = pres_polls[pres_polls['state'] == state['name']] 
                day = datetime.today() - timedelta(days=idx)
                
                final_polls = clean_and_filter_polls(day=day, polls=pres_polls_state)
                row = write_state_day_stats(day=day, state=state, polls=final_polls, file=f)
                all_output.append(row)
    
    # Create a DataFrame from the collected output
    df = pd.DataFrame(all_output)

    # Save the DataFrame to a CSV file
    path = os.path.join(dir_path, 'outputs/2024.EV.polls.median.test.csv')
    df.to_csv(path, index=False, float_format='%.2f')

# ======================================================================

def clean_districts(polls):
    """
    Cleans poll data by adjusting percentages and dropping irrelevant 
    rows based on specific state districts (Maine and Nebraska). 
    
    Args:
        polls (DataFrame): The DataFrame containing poll data.

    Returns:
        polls (DataFrame): The cleaned DataFrame.
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

def get_sen_states(): 
    # TODO: Fix Senate candidate data
    # Get state election prior and candidate data
    path = os.path.join(dir_path, '2024.Senate.priors.csv')
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sen_states.append(row) # dict format

    cand_list = pd.DataFrame(sen_states)
    dem_cands = cand_list['dem'].tolist()
    rep_cands = cand_list['rep'].tolist()

    return [dem_cands, rep_cands]

def get_all_polls(year):
    '''
    Gets all polls from 538 API...
    '''
    all_polls = pd.read_json(FIVETHIRTYEIGHT_API_URL)
    
    # Convert dates to standard datetime format
    all_polls.loc[:, 'endDate'] = pd.to_datetime(all_polls['endDate'])
    all_polls.loc[:, 'startDate'] = pd.to_datetime(all_polls['startDate'])
    
    # Filter by election year
    all_polls = all_polls[all_polls['endDate'] > datetime(year=year, month=1, day=1)]
    
    all_polls = clean_districts(all_polls)

    print("Printing all polls after cleaning districts...")
    print(all_polls)
    
    sen_states = get_sen_states()
    dem_cands = sen_states[0]
    rep_cands = sen_states[1]
    print(sen_states) 
    print(dem_cands)
    print(rep_cands)


    # Get presidential election prior data
    # path = os.path.join(dir_path, '2024.EV.priors.csv')
    # with open(path, 'r') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         states.append(row)
    # print(states)
    
    # print('Generating House medians...')
    # process_house_polls(all_polls, start_date)
    print('Generating Senate medians...')
    process_senate_polls(all_polls, start_date)
    # print('Generating presidential medians...')
    # process_presidential_polls(all_polls)

def main():

    get_all_polls(2024)

if __name__ == '__main__':
    main()