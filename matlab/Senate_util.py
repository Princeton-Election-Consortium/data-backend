import numpy as np
import pandas as pd
from scipy.stats import t
from datetime import datetime

# Initialize global variables
data_file = '../scraping/outputs/2024.Senate.polls.median.csv'
output_path = 'outputs/'
# TODO: Check with the spreadsheet
polling_states = ['AZ', 'FL', 'MD', 'MI', 'MT', 'NV', 'OH', 'PA', 'TX', 'WI', 'WV'] # 11 races
num_polling_states = len(polling_states)
# contested_races = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
contested_races = list(range(1, num_polling_states // 3 + 1)) # races in serious question


# == SENATE ============================================================

def Senate_median(polls, bias_pct, num_states, dem_safe):
    """
    Args:
        polls, biaspct, num_states, and Demsafe
        
    Returns: 
        various calculated values that correspond to their MATLAB counterparts
        Note that the tcdf function needs to be replaced with the appropriate Python function

    scipy.stats.t.cdf
    computes the cumulative distribution function (CDF) of the t-distribution
    
    x = np.array([-1, 0, 3, 4])  # Values at which to evaluate the CDF
    df = 10  # Degrees of freedom
    p = t.cdf(x, df)  # Compute the CDF

    print(p)
    # Output: [0.19146012 0.5        0.99330715 0.99864852]

    """

    # Working with pandas.DataFrame
    
    num_polls = polls['num_polls'] 
    # julian_date = polls[:, 1]
    # date_most_recent_poll = polls[:, 2]
    # median_margin = polls[:, 3]
    # est_std_dev = polls[:, 4]
    # state_num = polls[:, 5]

    # Calculate z-score and convert to probability, assuming normal distribution.
    polls['z'] = (polls['median_margin'] + bias_pct) / polls['est_std_dev']
    

    polls['prob_Dem_win'] = t.cdf(polls['z'], df=2)
    polls['prob_GOP_win'] = 1 - polls['prob_Dem_win']

    # using ESD, not SEM
    # polls_znov = (polls['median_margin'] + bias_pct) / np.sqrt(polls['SEM'] * polls['SEM'] + 5 * 5)
    # SEM = ESD / sqrt (N) where N = num of polls
    polls_znov = (polls['median_margin'] + bias_pct) / np.sqrt(polls['est_std_dev'] * polls['est_std_dev'] + 5 * 5)
    polls['prob_Dem_November'] = t.cdf(polls_znov, 2)

    state_probs = np.round(polls['prob_Dem_win'] * 100)
    state_nov_probs = np.round(polls['prob_Dem_November'] * 100)

    # print(state_nov_probs)

    # The meta-magic: store the Electoral Votes (EV) distribution,
    # the exact probability distribution of all possible outcomes
    # Initialize a list to store the EV distribution
    EV_distribution = [1 - polls['prob_Dem_win'].iloc[0], polls['prob_Dem_win'].iloc[0]]
    for i in range(1, num_states):
        nextEV = [1 - polls['prob_Dem_win'].iloc[i], polls['prob_Dem_win'].iloc[i]]
        EV_distribution = np.convolve(EV_distribution, nextEV)
    
    print("Printing")
    print(EV_distribution)
    print("Done")

    # Cumulative histogram of all possibilities
    histogram = EV_distribution[1:num_states + 1]
    cumulative_prob = np.cumsum(histogram)

    print(histogram)

    # Range of Senate seats Democratics are projected to win
    senate_seats = range(dem_safe + 1, dem_safe + num_states + 1)
    print(senate_seats)
    R_Senate_control_probability = cumulative_prob[max(50 - dem_safe, 0)]
    D_Senate_control_probability = 1 - R_Senate_control_probability

    # Calculate Senate seat that represents the median of distribution of outcomes
    median_index = next(i for i, prob in enumerate(cumulative_prob) if prob >= 0.5)
    median_seats = senate_seats[median_index]

    # Calculate the mean number of expected Senate seats 
    weighted_seats = [histogram[i] * senate_seats[i] for i in range(len(histogram))]
    mean_seats = round(sum(weighted_seats), 2)

    print(mean_seats)

    return state_probs, state_nov_probs, histogram, cumulative_prob, R_Senate_control_probability, D_Senate_control_probability, median_seats, mean_seats

# == SENATE ============================================================

def Senate_estimator(polls, bias_pct=0, for_history=0, analysis_date=0):
    # Distribution of Senate seats
    # Democratic, Republican, up for election
    assigned_EV = [0, 0, 0]
    # 0, 1, these are the seats not up for election or safe
    assigned_EV[0] = 42 # Democratic
    dem_safe = assigned_EV[0] # Initially considered safe for Dems
    assigned_EV[1] = 47 # Republican

    # Check if total number of assigned seats equals 0
    if np.sum(assigned_EV) != 100:
        print('Warning: Senate seats do not sum to 100!')
        print(assigned_EV)

    # Initialize other variables
    print(analysis_date)
    meta_calc = 1

    num_lines = sen_polls.shape[0]
    if num_lines % num_polling_states != 0:
        # TODO: Change this warning to include the file name
        print('Warning: polls.median.2022.Senate.txt is not a multiple of num_states lines long')
    
    # TODO: Test
    print(polls)
    print(num_lines) 
    print(num_polling_states)
    # Initialize an empty DataFrame with the same column names as polls
    # TODO: Replace all polldata with parsed_polls
    parsed_polls = pd.DataFrame(columns=polls.columns)
    if num_lines > num_polling_states: 
        if analysis_date > 0: 
            print(analysis_date)
            # Index of the first (most recent, assuming reverse time order) entry matching the analysis date
            i = np.where(polls['julian_date'] == analysis_date)[0]
            print(i)
            if i.size > 0:
                idx = i[0]
                print(idx)
                parsed_polls = polls.reset_index(drop=True).iloc[idx:idx+num_polling_states, :]
        else: 
            # polldata = polls[:num_polling_states, :]
            # Use default integer index
            parsed_polls = polls.reset_index(drop=True).iloc[:num_polling_states, :]

    print(parsed_polls)

    # Initialize polls data
    # TODO: calculate SEM 
    polls_SEM = np.maximum(parsed_polls['est_std_dev'], np.zeros(num_polling_states) + 3)  # Minimum uncertainty of 2%
    parsed_polls['est_std_dev'] = np.maximum(parsed_polls['est_std_dev'], 3)

    # Add electoral votes (EV) to all the states
    parsed_polls['EV'] = np.ones(num_polling_states)
    assigned_EV[2] = parsed_polls['EV'].sum()

    total_polls_used = np.sum(parsed_polls['num_polls'])
    print(total_polls_used)

    # Magic calculations
    # TODO: Rename these variables
    state_probs, state_nov_probs, histogram, cumulative_prob, R_control_probs, D_control_probs, median_seats, mean_seats = Senate_median(sen_polls, bias_pct, num_polling_states, dem_safe)

    # OUTPUTS----------------------
    # confidenceintervals(3)=Senateseats(find(cumulative_prob<=0.025,1,'last')); % 95-pct lower limit
    # confidenceintervals(1)=Senateseats(find(cumulative_prob<=0.15865,1,'last')); % 1-sigma lower limit
    # confidenceintervals(2)=Senateseats(find(cumulative_prob>=0.84135,1,'first')); % 1-sigma upper limit% confidenceintervals(4)=Senateseats(find(cumulative_prob>=0.975,1,'first')); % 95-pct upper limit

    # Print the assigned_EV for each range of state_probs
    print("State probs:", state_probs)
    print("Assigned EV:", assigned_EV)

    # Iterate over each range of state_probs
    # Recalculate safe EV for each party

    # Check i < len(parsed_polls) condition
    assigned_EV[0] += sum(parsed_polls['EV'].iloc[i] for i, prob in enumerate(state_probs) if prob >= 95 and i < len(parsed_polls))
    assigned_EV[1] += sum(parsed_polls['EV'].iloc[i] for i, prob in enumerate(state_probs) if prob <= 5 and i < len(parsed_polls))

    
    # assigned_EV[0] += np.sum(parsed_polls['EV'][np.where(state_probs >= 95)])
    # assigned_EV[1] += np.sum(parsed_polls['EV'][np.where(state_probs <= 5)])
    assigned_EV[2] = 100 - assigned_EV[0] - assigned_EV[1]

    print(assigned_EV)

    # uncertain = np.intersect1d(np.where(stateprobs < 95), np.where(stateprobs > 5))
    # uncertain_states = ', '.join([polling_states[i] for i in uncertain])

    # ------ Daily file update -----------------------------------
    # outputs = [median_seats, mean_seats, D_Senate_control_probability] + list(assigned_EV) + [total_polls_used] + \
    #         list(confidence_intervals) + [np.mean(polldata[contested, 2])]
    # if bias_pct == 0:
    #     np.savetxt(output_path + 'Senate_histogram_2022.csv', histogram)
    #     # Export state-by-state percentage probabilities as CSV
    #     # Update Senate_estimate_history_2022.csv

    # # Meta-margin calculation
    # reality = 1 - D_Senate_control_probability
    # if meta_calc == 0:
    #     metamargin = -999
    # else:
    #     foo = bias_pct
    #     bias_pct = -7
    #     Senate_median()
    #     while median_seats < 50:
    #         bias_pct += 0.02
    #         Senate_median()
    #     metamargin = -bias_pct
    #     bias_pct = foo

    # # Daily and History Update
    # # Write file update to Senate_estimates
    # outputs.append(metamargin)
    # np.savetxt(output_path + 'Senate_estimates_2022.csv', outputs, delimiter=',')  # Just today's estimate
    # if for_history:
    #     np.savetxt(output_path + 'Senate_estimate_history_2022.csv', np.hstack([polldata[0, 4], outputs]),
    #            delimiter=',', newline='\n', fmt='%s')  # Append to history file

# == SENATE ============================================================

def Senate_regenerate(polls):
    """
    iterates over dates starting from March 1st, 2024, up to the current date
    """
    start_date = datetime(2023, 12, 31)
    today_date = datetime.today()
    days_difference = (today_date - start_date).days

    # Regenerate data from April 21 (julian date 112) to the current date
    for analysis_date in range(111, days_difference + 1): 
        # Perform analysis for Senate estimation 
        Senate_estimator(polls, for_history=1, analysis_date=analysis_date) 
        
        # Copies histogram file to a destination folder
        # senate_hist_filename = f'oldhistograms/Senate_histogram_{analysis_date}.jpg'
        # shutil.copyfile('Senate_histogram_today.jpg', senate_hist_filename)

        # MATLAB
        # Senatehistfilename=['oldhistograms\Senate_histogram_' num2str(analysisdate,'%i') '.jpg']
        # copyfile('Senate_histogram_today.jpg',Senatehistfilename);

# == SENATE ============================================================

sen_polls = pd.read_csv(data_file)
# print(sen_polls)

# Senate_regenerate(sen_polls) is called in Senate_estimator
# Senate_median(sen_polls, 0, num_polling_states, 45)
Senate_estimator(sen_polls)