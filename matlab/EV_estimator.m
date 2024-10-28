%%%  EV_estimator.m - a MATLAB script
%%%  Copyright 2008, 2016, 2020, 2022, 2024 by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.

% Likelihood analysis of all possible outcomes of election based 
% on the meta-analytical methods of Prof. Sam Wang, Princeton University.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EV_estimator.m
% 
% This script loads 'EV.polls.median.txt' for the current election year
% and generates or updates/replaces 4 CSV files:
% 
% EV_estimates.csv
%    all in one line:
%    2 values - medianEV for the two candidates, where a margin>0 favors the first candidate (in our case, Biden);
%    2 values - modeEV for the two candidates;
%    3 values - assigned (>95% prob) EV for each candidate, with a third entry for undecided;
%    4 values - confidence intervals for candidate 1's EV: +/-1 sigma, then
%    95% band; and
%    1 value - number of state polls used to make the estimates.
%    1 value - (calculated by EV_metamargin and appended) the meta-margin.
% 
% Another file, EV_estimate_history.csv, is updated with the same
% information as EV_estimates.csv plus 1 value for the date.
%
% EV_stateprobs.csv
%    A 51-line file giving percentage probabilities for candidate #1 win of the popular vote, state by state. 
%    Note that for EV calculation, NE and ME were assumed to have a winner-take-all rule, but in fact they do not. 
%    Because in practice NE and ME have not split their votes, for now this is a satisfactory approximation.
%    The second field on each line is the current median polling margin.
%    The third field on each line is the two-letter postal abbreviation.
% 
% EV_histogram.csv
%    A 538-line file giving the probability histogram of each EV outcome.
%    Line 1 is the probability of candidate #1 (Biden) getting 1 EV. Line 2 is 2 EV, and so on. 
%    Note that 0 EV is left out of this histogram for ease of indexing.
% 
% EV_perturbation.csv
%    A 1-line fine that gives the median EV for all polls perturbed by
%    +/- 2. The first entry is unperturbed, the second entry is +2, 
%    and the third entry is -2. 
%    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% This routine expects the global variables biaspct and analysisdate

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%% Initialize variables %%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

whereoutput='outputs/'; % the output path for CSV and TXT files

polls.state= EV_STATES
polls.EV= EV_PER_STATE
num_states=size(polls.EV,2);

assignedEV(3)=sum(polls.EV);
assignedEV(1)=0; assignedEV(2)=0; % do not assume any states are safe - calculate all 2^51 possibilities!
% 1=Dem, 2=GOP, 3=uncertain
% checksum to make sure no double assignment or missed assignment
if (sum(assignedEV)~=538)
    warning('Warning: Electoral votes do not sum to 538!')
    assignedEV
end

if ~exist('biaspct','var')
    biaspct=0;
end

if ~exist('forhistory','var')
    forhistory=0;
end


if ~exist('analysisdate','var')
    analysisdate=0;
end

if ~exist('metacalc','var')
    metacalc=1;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% Load and parse polling data %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
polldata=load(EV_POLLS_TXT);
% wants groups of 51 lines, most recent group first (reverse time order)
% in each line, fields should be 
%    #polls, datelastpoll?, pollmargin, pollSEM, date_update, statenum
numlines = size(polldata,1);
if mod(numlines,51)>0
    warning('Warning: ' + EV_POLLS_TXT + ' is not a multiple of 51 lines long');
end
% Currently we are using median and effective SEM of the last 3 polls.
% To de-emphasize extreme outliers, in place of SD we use (median absolute deviation)/0.6745

% find the desired data within the file;
if analysisdate>0  && numlines>51
    foo=find(polldata(:,2)==analysisdate,1,'first'); % find the specified date if available
    foo2=find(polldata(:,2)==max(polldata(:,5)),1,'first'); % find the newest data
    ind=max([foo2 foo]); % take whichever data comes further down in the file
    polldata=polldata(ind:ind+50,:);
    clear foo2 foo ind
elseif numlines>51
%    polldata = polldata(numlines-50:numlines,:);
    polldata = polldata(1:51,:); % take the top 51 lines of the file
end

% Use statistics from data file
polls.margin=polldata(:,4)';
polls.SEM=polldata(:,5)';
polls.SEM=max(polls.SEM,zeros(1,51)+3); % put a floor on the uncertainty of 3 percentage points
totalpollsused=sum(polldata(:,1));

% mock data in case we ever need to do a dry run
% Use three poll (as of 28 Sep 2012)
% polls.margin=[-18.5 -22 -10 -22.5 22 3.5 13 86 25 4 -7 36 -25 17 -6 3 -15 -14 -19 16 20 21 9 8 -13 -6.5 -9 -14 2 5 14 8 28 2 -15 5.5 -32 8 9 22.5 -6 -9 -6.5 -15 -32 31 2 17 -14 6.5 -32];
% polls.SEM=zeros(1,51)+3;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% Generate values for Maine, Nebraska districts %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%  PVI updated September 2024 %%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
polls.margin(52:53)=polls.margin(20)+[12 -12]; % the differences are 2* the deviation in D vote share from statewide average in davesredistricting.org
polls.SEM(52:53)=sqrt(polls.SEM(20)^2+4);
polls.margin(54:56)=polls.margin(28)+[8 21 -28]; % again the differences are 2* the deviation in D vote share from statewide average in davesredistricting.org
polls.SEM(54:56)=sqrt(polls.SEM(28)^2+4);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%% Where the magic happens! %%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
EV_median

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%% Plot the histogram %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close
phandle=plot([269 269],[0 max(histogram)*105],'-g','LineWidth',1.5);
EVmintick=220; EVmaxtick=420; EVticks=EVmintick:20:EVmaxtick;
grid on
hold on
bar(histogram*100,'k')
axis([EVmintick EVmaxtick 0 max(histogram)*105])
xlabel('Electoral votes for Harris','FontSize',14);
ylabel('Probability of exact # of EV (%)','FontSize',14)
set(gcf, 'InvertHardCopy', 'off');
title('Distribution of possible outcomes - snapshot','FontSize',14)
text(EVmintick+3,max(histogram)*99,'Trump wins','FontSize',14)
text(EVmaxtick-45,max(histogram)*99,'Harris wins','FontSize',14)
if analysisdate==0
    datelabel=datestr(today);
else
    datelabel=datestr(analysisdate);
end
text(EVmintick+2,max(histogram)*19,datelabel(1:6),'FontSize',12)
text(EVmintick+2,max(histogram)*13,'election.princeton.edu','FontSize',12)
if biaspct==0
    % set(gcf,'PaperPositionMode','auto')
    print('-djpeg', EV_HISTOGRAM_TODAY_JPG);
    % screen2jpeg([EV_HISTOGRAM_TODAY_JPG])
    % if analysisdate==0
    %     EVhistfilename=['oldhistograms/EV_histogram_' num2str(polldata(1,2),'%i') '.jpg'] % assumes a graph exists
    %     copyfile(EV_HISTOGRAM_TODAY_JPG,EVhistfilename);
    % end
end

% Calculate median and confidence bands from cumulative histogram
confidenceintervals(3)=electoralvotes(find(cumulative_prob<=0.025,1,'last')); % 95-pct lower limit
confidenceintervals(1)=electoralvotes(find(cumulative_prob<=0.15865,1,'last')); % 1-sigma lower limit
confidenceintervals(2)=electoralvotes(find(cumulative_prob>=0.84135,1,'first')); % 1-sigma upper limit
confidenceintervals(4)=electoralvotes(find(cumulative_prob>=0.975,1,'first')); % 95-pct upper limit
probability_GOP_win=cumulative_prob(find(electoralvotes>=269,1,'first'));
modeEV(1)=find(histogram==max(histogram));
medianEV(2)=538-medianEV(1); % assume no EV go to a third candidate
modeEV(2)=538-modeEV(1); % assume no EV go to a third candidate

% Re-calculate safe EV for each party
assignedEV(1)=sum(polls.EV(find(stateprobs>=95)));
assignedEV(2)=sum(polls.EV(find(stateprobs<=5)));
assignedEV(3)=538-assignedEV(1)-assignedEV(2);

uncertain=intersect(find(stateprobs<95),find(stateprobs>5));
uncertainstates='';
for i=1:max(size(uncertain))
    uncertainstates=[uncertainstates statename(uncertain(i)) ' '];
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% Daily file update %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Write a file of unbiased statewise percentage probabilities
% Only write this file if bias is zero!
outs=[medianEV modeEV assignedEV confidenceintervals totalpollsused];    
%daystoelection=ELECTION_DATE-today;
if DAYS_UNTIL_ELECTION>90
    sigmadrift=7;
elseif DAYS_UNTIL_ELECTION<1
    sigmadrift=1.5;
else
    sigmadrift=sqrt((DAYS_UNTIL_ELECTION/90*7)^2+1.5^2); % the 1.5 term adds a minimal uncertainty CHANGE FROM 2016
end
if biaspct==0
    % save 'EVoutput' %save workspace for inspection, doesn't go into whereoutput
%   Export probability histogram:
    dlmwrite(strcat(whereoutput,EV_HISTOGRAM_CSV),histogram')
%   Export state-by-state percentage probabilities as CSV, with 2-letter state abbreviations:
%   Each line includes hypothetical probabilities for D+2% and R+2% biases
    if exist(strcat(whereoutput,EV_STATEPROBS_CSV),'file')
        delete(strcat(whereoutput,EV_STATEPROBS_CSV))
    end
    foo=(polls.margin+2)./polls.SEM;
    D2probs=round((erf(foo/sqrt(2))+1)*50);
    foo=(polls.margin-2)./polls.SEM;
    R2probs=round((erf(foo/sqrt(2))+1)*50);
    foo=polls.margin./(sqrt(sigmadrift^2+polls.SEM.^2));
    Novprobs=round((erf(foo/sqrt(2))+1)*50);
    for i=1:num_states
        foo=[num2str(stateprobs(i)) ',' num2str(polls.margin(i)) ',' num2str(D2probs(i)) ',' num2str(R2probs(i)) ',' statename(i) ',' num2str(Novprobs(i))];
        dlmwrite(strcat(whereoutput,EV_STATEPROBS_CSV),foo,'-append','delimiter','')
    end
end
write_270towin_strings(stateprobs,D2probs,R2probs,'',whereoutput); % to make a working URL, set string to 'http://www.270towin.com/maps/'

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% The meta-margin %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
reality=probability_GOP_win;

if metacalc==0
    metamargin=-999;
else
    foo=biaspct;
        startrange=round((269-medianEV(1))/1.25)/10-2;
    testrange=startrange:0.02:startrange+6;
    scanrange=-20:1:20;
    testvalues=union(testrange,scanrange,'sorted');
    clear EVtest
    for itest=1:length(testvalues)
        biaspct=testvalues(itest);
        EV_median
        EVtest(itest)=medianEV(1);
    end
    metamargin=-min(testvalues(find(EVtest>=269)));
    dlmwrite(strcat(whereoutput,EV_MM_TABLE_CSV), [(testvalues+metamargin)' EVtest'])
    biaspct=foo; 
    clear foo
    outs=[outs metamargin];
end
outs=[outs 1-reality];

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%% November win probabilities %%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% note this call requires the sigmadrift variable, calculated above
EV_prediction % calculate drift-based and Bayesian win probability
% November_win_probability=tcdf(metamargin/sigmadrift,3);
November_win_probability=drift_winprob;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% Daily and History Update %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

outputs=[outs drift_winprob bayesian_winprob]
dlmwrite(strcat(whereoutput,EV_ESTIMATES_CSV), outputs)
if forhistory
   dlmwrite(strcat(whereoutput,EV_ESTIMATE_HISTORY_CSV),[polldata(1,2) outputs],'-append')
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% EV Median Range %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% We perturb the polls by +/- 2 to see the range of EV votes 

% Perturb by +2 
for state=1:num_states
        polls.margin(state)=polls.margin(state)+2;
end

EV_median
EV_median_plus_2 = medianEV(1);


for state=1:num_states 
    polls.margin(state)=polls.margin(state)-2;
end


% Perturb by -2 
for state=1:num_states
        polls.margin(state)=polls.margin(state)-2;
end

EV_median
EV_median_minus_2 = medianEV(1);

for state=1:num_states 
    polls.margin(state)=polls.margin(state)+2;
end

% Calculate EV median w/o pertubation (also to just make to properly reset
EV_median

output_ev_perturbation = [medianEV(1) EV_median_plus_2 EV_median_minus_2]; 

dlmwrite(strcat(whereoutput,EV_PERTURBATION_CSV), output_ev_perturbation); 
