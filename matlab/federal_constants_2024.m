% Define constant global variable values
YEAR = 2024;
DIR_PATH = '../scraping/outputs/';

TODAYTE = floor(today-datenum('31-dec-2023')); % today's date
%ELECTION_DATE = datenum(2024,11,5); % November 5, Julian 310
%DAYS_UNTIL_ELECTION = ELECTION_DATE - TODAYTE;

ELECTION_DATE = '2024-11-05';
DAYS_UNTIL_ELECTION = calculateDaysUntil(ELECTION_DATE);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EV CONSTANTS

% EV_regenerate
EV_START_DATE = 112; 

% EV_estimator
EV_POLLS_TXT = strcat(DIR_PATH, num2str(YEAR), '.EV.polls.median.txt');
EV_STATES = [
 'AL,AK,AZ,AR,CA,CO,CT,DC,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY,M1,M2,N1,N2,N3 '];
EV_PER_STATE = [9  3  11  6 54 10 7  3  3  30 16  4 4  19 11  6  6  8  8  2 10 11 15 10 6  10  4  2  6  4 14 5  28 16  3 17  7  8 19  4  9  3 11 40  6  3 13 12  4 10  3  1  1  1  1  1]; % add Maine and Nebraska - deployed October 28 2016

% EV_prediction
EV_MAXDRIFT = 4 % Sam 05/16/24

% Output files 
EV_ESTIMATES_CSV = strcat('EV_estimates_', num2str(YEAR), '.csv');
EV_ESTIMATE_HISTORY_CSV = strcat('EV_estimate_history_', num2str(YEAR), '.csv');
EV_HISTOGRAM_CSV = strcat('EV_histogram_', num2str(YEAR), '.csv');
EV_HISTOGRAM_TODAY_JPG = strcat('EV_histogram_today_', num2str(YEAR), '.jpg');
EV_STATEPROBS_CSV = strcat('EV_stateprobs_', num2str(YEAR), '.csv');
EV_MM_TABLE_CSV = strcat('EV_MM_table_', num2str(YEAR), '.csv');
EV_PREDICTION_CSV = strcat('EV_prediction_', num2str(YEAR), '.csv');
EV_PREDICTION_PROBS_CSV = strcat('EV_prediction_probs_', num2str(YEAR), '.csv');
EV_PREDICTION_MM_CSV = strcat('EV_prediction_MM_', num2str(YEAR), '.csv');
EV_HISTORY_JPG = strcat('EV_history_', num2str(YEAR), '.jpg');
EV_JERSEYVOTES_CSV = strcat('EV_jerseyvotes_', num2str(YEAR), '.csv');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% SENATE CONSTANTS

SENATE_START_DATE = 46; % February 15

% Senate_estimator
SENATE_POLLS_TXT = strcat(DIR_PATH, num2str(YEAR), '.Senate.polls.median.txt');
SENATE_STATES = ['AZ,FL,MD,MI,MT,NV,OH,PA,TX,WI,WV ']; % 11 races
CONTESTED_STATES = [1:length(SENATE_STATES)/3];
DEM_ASSIGNED = 42;
REP_ASSIGNED = 47;

% Output files 
% from Senate_estimator.m
SENATE_ESTIMATES_CSV = strcat('Senate_estimates_', num2str(YEAR), '.csv');
SENATE_ESTIMATE_HISTORY_CSV = strcat('Senate_estimate_history_', num2str(YEAR), '.csv');
SENATE_HISTOGRAM_CSV = strcat('Senate_histogram_', num2str(YEAR), '.csv');
SENATE_HISTOGRAM_TODAY_JPG = strcat('Senate_histogram_today_', num2str(YEAR), '.jpg');
SENATE_STATEPROBS_CSV = strcat('Senate_stateprobs_', num2str(YEAR), '.csv');
% from Senate_jerseyvotes.m
SENATE_JERSEYVOTES_CSV = strcat('Senate_jerseyvotes_', num2str(YEAR), '.csv'); 
% from Senate_November_prediction
SENATE_D_NOV_CONTROL_PROB_CSV = strcat('Senate_D_November_control_probability_', num2str(YEAR), '.csv'); 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% HOUSE CONSTANTS

% House_prediction
HOUSE_POLLS_TXT = strcat(DIR_PATH, num2str(YEAR), '.house.polls.median.txt');
HOUSE_SPECIALS_PRIOR = 4.5; % LAST UPDATE: 05/31/2024
HOUSE_SPECIALS_SD = 3.5; % not that many previous examples

% Output files
HOUSE_PREDICTIONS_CSV = strcat('House_predictions_', num2str(YEAR), '.csv');


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% HELPER FUNCTIONS 

function daysUntilDate = calculateDaysUntil(targetDate)
    % Get the current date
    currentDate = datetime('today');
    
    % Convert the target date to a datetime object if it is not already
    if ~isa(targetDate, 'datetime')
        targetDate = datetime(targetDate, 'InputFormat', 'yyyy-MM-dd');
    end
    
    % Calculate the difference in days
    daysUntilDate = days(targetDate - currentDate);
end

