%%%  Senate_estimator.m - a MATLAB script
%%%  Copyright 2008, 2016, 2020, 2022, 2024 by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.

% Likelihood analysis of all possible outcomes of election based 
% on the meta-analytical methods of Prof. Sam Wang, Princeton University.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Senate_estimator.m
% 
% This script loads 'Senate.polls.median.txt' for the current election year
% and generates or updates/replaces 4 CSV files:
% 
% Senate_estimates.csv
%    all in one line:
%    1 value - median_seats for Democrats/Independents (integer)
%    1 value - mean_seats for Democrats/Independents (round to 0.01)
%    1 value - Democratic/Independent control probability (round to 1%)
%    3 values - assigned (>95% prob) seats for each party (integers) and
%    uncertain
%    1 value - number of state polls used to make the estimates (integer)
%    2 values - +/-1 sigma CI for Democratic/Independent Senate seats (integers)
%    1 value - mean margin in contested states
%    1 value - (calculated by Senate_metamargin and appended) the meta-margin
% 
% Another file, Senate_estimate_history.csv, is updated with 1 value for 
% the date and then the same information as Senate_estimates.csv.
%
% Senate_stateprobs.csv
%    An N-line file giving percentage probabilities for Dem/Ind win of the popular vote, state by state. 
%    This is the same as the 2012 EV calculation, but 1 seat per race i.e. 'EV' is a Senate seat
%    The second field on each line is the current median polling margin.
%    The third field on each line is the two-letter postal abbreviation.
% 
% Senate_histogram.csv
%    A 100-line file giving the probability histogram of each seat-count outcome. Line 1 is 
%    the probability of party #1 (Democrats/Independents) getting 1 seat. Line 2 is 2 seat, and so on. 
%    Note that 0 seat is left out of this histogram for ease of indexing.
% 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% This routine expects the global variables biaspct and analysisdate

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%% Initialize variables %%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

whereoutput='outputs/'; % the output path for CSV and TXT files
% cd(whereoutput)

polls.state=SENATE_STATES;
contested=CONTESTED_STATES; % races in serious question
polls.EV=ones(1, length(polls.state)/3);
num_states=size(polls.EV,2);

assignedEV(3)=sum(polls.EV);
assignedEV(1)=DEM_ASSIGNED; assignedEV(2)=REP_ASSIGNED; % seats not up for election or safe; updated 2024
Demsafe=assignedEV(1);
% 1=Dem, 2=GOP, 3=up for election
% checksum to make sure no double assignment or missed assignment
if (sum(assignedEV)~=100)
    warning('Warning: Senate seats do not sum to 100!')
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
todayte=floor(today-datenum('31-dec-2023'));

if ~exist('metacalc','var')
    metacalc=1;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% Load and parse polling data %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
polldata=load(SENATE_POLLS_TXT);
% see Stephanie's documentation of columns

numlines = size(polldata,1);
if mod(numlines,num_states)>0
    warning('Warning: ' + SENATE_POLLS_TXT + ' is not a multiple of num_states lines long');
end
% Currently we are using median and effective SEM of the last 3 polls.
% To de-emphasize extreme outliers, in place of SD we use (median absolute deviation)/0.6745

% find the desired data within the file
if analysisdate>0 && numlines>num_states
    foo=find(polldata(:,2)==analysisdate,1,'first'); % find the start of the entry matching analysisdate
 %   ind=min([size(polldata,1)-num_states+1 foo']);
    foo2=find(polldata(:,2)==max(polldata(:,5)),1,'first'); % find the start of the freshest entry
    ind=max([foo2 foo]); %assume reverse time order, take whichever of the two was done earlier, also protect against no data for analysisdate
    polldata=polldata(ind:ind+num_states-1,:);
    clear foo2 foo ind
elseif numlines>num_states
%    polldata = polldata(numlines-num_states+1:numlines,:); % end of file
    polldata = polldata(1:num_states,:); % top of file
end

% Use statistics from data file
polls.margin=polldata(:,4)';
polls.SEM=polldata(:,5)';
polls.SEM=max(polls.SEM,zeros(1,num_states)+3) % minimum uncertainty of 3%
totalpollsused=sum(polldata(:,1))

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%% Where the magic happens! %%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
Senate_median
stateprobs % is this just printing stuff?
Dcontrolprobs(1)=D_Senate_control_probability;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%% Plot the histogram %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
close
phandle=plot([49.5 49.5],[0 max(histogram)*105],'-r','LineWidth',1.5);
grid on
hold on
%
% now plot snapshot histogram
%
bar(Senateseats(3:49-assignedEV(1)),histogram(3:49-assignedEV(1))*100,'r')
bar(Senateseats(50-assignedEV(1):assignedEV(3)),histogram(50-assignedEV(1):assignedEV(3))*100,'b')
bar(Senateseats(50-assignedEV(1)),histogram(50-assignedEV(1))*50,'r') %hard-coded Presidential probability; could read from file but for now this

% obar=find(Senateseats==50); %Orman factor
% bar(Senateseats(obar),histogram(obar)*stateprobs(6),'g')
axis([Senateseats(3)-0.8 Senateseats(assignedEV(3))+0.5 0 max(histogram)*105])
xlabel('Democratic+Independent Senate seats','FontSize',14);
ylabel('Probability (%)','FontSize',14)
set(gcf, 'InvertHardCopy', 'off');
title('Distribution of possible outcomes - snapshot','FontSize',14)

Dstr=['D control: ',num2str(round(D_Senate_control_probability*100)),'%'];
Rstr=['R control: ',num2str(round(R_Senate_control_probability*100)),'%'];
% text(Senateseats(3)-0.35,max(histogram)*99,Rstr,'FontSize',18)
% text(Senateseats(13)-2.3,max(histogram)*99,Dstr,'FontSize',18)
if analysisdate==0
    datelabel=datestr(now);
else
    datelabel=datestr(analysisdate);
end
text(Senateseats(2)+0.3,max(histogram)*100,datelabel(1:6),'FontSize',12)
text(Senateseats(2)+0.3,max(histogram)*94,'election.princeton.edu','FontSize',12)
if biaspct==0
%    set(gcf,'PaperPositionMode','auto')
    print('-djpeg', SENATE_HISTOGRAM_TODAY_JPG);
    % screen2jpeg(['Senate_histogram_today_2024.jpg'])
end
%
% end plot
%

%
%    Start calculating some outputs
%

confidenceintervals(3)=Senateseats(find(cumulative_prob<=0.025,1,'last')); % 95-pct lower limit
confidenceintervals(1)=Senateseats(find(cumulative_prob<=0.15865,1,'last')); % 1-sigma lower limit
confidenceintervals(2)=Senateseats(find(cumulative_prob>=0.84135,1,'first')); % 1-sigma upper limit% confidenceintervals(4)=Senateseats(find(cumulative_prob>=0.975,1,'first')); % 95-pct upper limit

% Re-calculate safe EV for each party
assignedEV(1)=assignedEV(1)+sum(polls.EV(find(stateprobs>=95)));
assignedEV(2)=assignedEV(2)+sum(polls.EV(find(stateprobs<=5)));
assignedEV(3)=100-assignedEV(1)-assignedEV(2);

uncertain=intersect(find(stateprobs<95),find(stateprobs>5));
uncertainstates='';
for i=1:max(size(uncertain))
    uncertainstates=[uncertainstates statename2(uncertain(i),polls.state) ' '];
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% Daily file update %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% These are files that are based on a pure polling snapshot.
% Only write histogram and statewise probabilities if biaspct==0
%
%    1 value - date of analysis [for Senate_estimate_history.csv only]
%    1 value - median_seats for Democrats/Independents (integer)
%    1 value - mean_seats for Democrats/Independents (round to 0.01)
%    1 value - Democratic/Independent control probability (round to 1%)
%    3 values - assigned (>95% prob) seats for each party (integers) and
%    uncertain
%    1 value - number of state polls used to make the estimates (integer)
%    2 values - +/-1 sigma CI for Democratic/Independent Senate seats (integers)
%    1 value - mean margin in contested states
%    1 value - (calculated by Senate_metamargin and appended) the meta-margin
% 
outputs=[median_seats mean_seats Dcontrolprobs assignedEV totalpollsused confidenceintervals(1:2) mean(polldata(contested,4))];    

if biaspct==0
%   Export probability histogram:
    dlmwrite(strcat(whereoutput,SENATE_HISTOGRAM_CSV),histogram')
%   Export state-by-state percentage probabilities as CSV, with 2-letter state abbreviations:
%   Each line includes hypothetical probabilities for D+2% and R+2% biases
%   Also give margin
    
% old calculation, purely a snapshot with drift, used until October 11:
%    foo=(polls.margin)./sqrt(polls.SEM.^2+25);
%    statenovprobs=round((erf(foo/sqrt(2))+1)*50);
%    foo=(polls.margin+2)./polls.SEM;
%    D2probs=round((erf(foo/sqrt(2))+1)*50);
%    foo=(polls.margin-2)./polls.SEM;
%    R2probs=round((erf(foo/sqrt(2))+1)*50);

% daystoelection=ELECTION_DATE-today; % days until election (note: November 8, Julian 314)
% Where is the function Bayesian_November_prediction at?
daystoelection = DAYS_UNTIL_ELECTION; 
for istate=1:length(polls.margin)
    [~,statenovprobs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate),0.8,7,3,polls.margin(istate),10);
    [~,D2probs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate)+2,0.8,7,3,polls.margin(istate),10);
    [~,R2probs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate)-2,0.8,7,3,polls.margin(istate),10);
end
statenovprobs=round(statenovprobs*100); D2probs=round(D2probs*100); R2probs=round(R2probs*100);

if exist(strcat(whereoutput,SENATE_STATEPROBS_CSV),'file')
    delete(strcat(whereoutput,SENATE_STATEPROBS_CSV))
end
% what the columns mean in Senate_stateprobs.csv:
% column 1: Today's snapshot D win probability
% column 2: November D win probability
% column 3: median margin (positive indicates D is front-runner)
% column 4: November win probability adding 2% to margin for D
% column 5: November win probability adding 2% to margin for R
% column 6: Two-letter postal abbreviation of state
for ii=1:num_states
        foo=[num2str(stateprobs(ii)) ',' num2str(statenovprobs(ii)) ',' num2str(polls.margin(ii)) ',' num2str(D2probs(ii)) ',' num2str(R2probs(ii)) ',' statename2(ii,polls.state)];
        dlmwrite(strcat(whereoutput,SENATE_STATEPROBS_CSV),foo,'-append','delimiter','')
    end
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% The meta-margin %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

reality=1-Dcontrolprobs(1);

if metacalc==0
    metamargin=-999;
else
    foo=biaspct;
    biaspct=-7; % just brute force - might have to change this guess later
    Senate_median
    while median_seats < 50
        biaspct=biaspct+.02;
        Senate_median
    end
    metamargin=-biaspct
    biaspct=foo; 
    clear foo
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% Daily and History Update %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
outputs = [outputs metamargin];
dlmwrite(strcat(whereoutput,SENATE_ESTIMATES_CSV), outputs) % just today's estimate
if forhistory
   dlmwrite(strcat(whereoutput,SENATE_ESTIMATE_HISTORY_CSV),[polldata(1,2) outputs],'-append')
   display('appended history file')
end
