%%%  Senate_estimator.m - a MATLAB script
%%%  Copyright 2008, 2016 by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.

% Likelihood analysis of all possible outcomes of election based 
% on the meta-analytical methods of Prof. Sam Wang, Princeton University.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Senate_estimator.m
% 
% This script loads '2018.Senate.polls.median.txt' and generates or updates/replaces 4 CSV files:
% 
% Senate_estimates.csv
%    all in one line:
%    1 value - date of analysis
%    1 value - median_seats for Democrats/Independents (integer)
%    1 value - mean_seats for Democrats/Independents (round to 0.01)
%    1 value - Democratic/Independent control probability (round to 1%)
%    3 values - assigned (>95% prob) seats for each party (integers) and
%    uncertain
%    1 value - number of state polls used to make the estimates (integer)
%    1 value - +/-1 sigma CI for Democratic/Independent Senate seats (integers)
%    1 value - (calculated by Senate_metamargin and appended) the meta-margin
% 
% Another file, Senate_estimate_history, is updated with the same
% information as Senate_estimates.csv plus 1 value for the date.
%
% stateprobs.csv
%    An N-line file giving percentage probabilities for Dem/Ind win of the popular vote, state by state. 
%    Note that this is the same as the 2012 EV calculation, except 1 seat per race
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

% polls.state=[
% 'AL,AK,AZ,AR,CA,CO,CT,DC,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY '];
polls.state=['AZ,FL,IN,MO,MT,ND,NJ,NV,TN,TX ']; % 10 races
contested=[1 2 3 4 5 6 7 8 9 10]; % races in serious question
polls.EV=ones(1, length(polls.state)/3);
num_states=size(polls.EV,2);

assignedEV(3)=sum(polls.EV);
assignedEV(1)=43; assignedEV(2)=47; % these are the seats not up for election
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
forhistory=biaspct==0;

if ~exist('analysisdate','var')
    analysisdate=0;
else
disp(analysisdate)
end

if ~exist('metacalc','var')
    metacalc=1;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% Load and parse polling data %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
polldata=load('2018.Senate.polls.median.txt');
% column 1 - numpolls
% column 2 - lastdate
% column 3 - median margin
% column 4 - SEM 
% column 5 - date of monitoring
% column 6 - state index
% column 7 (not implemented yet)
% column 8 (not implemented yet)

numlines = size(polldata,1);
if mod(numlines,num_states)>0
    warning('Warning: polls.median.2016Senate.txt is not a multiple of num_states lines long');
end
% Currently we are using median and effective SEM of the last 3 polls.
% To de-emphasize extreme outliers, in place of SD we use (median absolute deviation)/0.6745

% find the desired data within the file
if analysisdate>0 && numlines>num_states
    foo=find(polldata(:,5)==analysisdate,1,'first'); % find the start of the entry matching analysisdate
    ind=min([size(polldata,1)-num_states+1 foo']);
    % foo2=find(polldata(:,5)==max(polldata(:,5)),1,'first'); % find the start of the freshest entry
    % ind=max([foo2 foo]); %assume reverse time order, take whichever of the two was done earlier, also protect against no data for analysisdate
    polldata=polldata(ind:ind+num_states-1,:);
    clear foo2 foo ind
elseif numlines>num_states
    polldata = polldata(numlines-num_states+1:numlines,:); % end of file
%    polldata = polldata(1:num_states,:); % top of file
end

% Use statistics from data file
polls.margin=polldata(:,3)';
polls.SEM=polldata(:,4)';
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
phandle=plot([50.5 50.5],[0 max(histogram)*105],'-r','LineWidth',1.5);
grid on
hold on
%
% now plot snapshot histogram
%
bar(Senateseats(1:7),histogram(1:7)*100,'r')
bar(Senateseats(8:10),histogram(8:10)*100,'b')
% obar=find(Senateseats==50); %Orman factor
% bar(Senateseats(obar),histogram(obar)*stateprobs(6),'g')
axis([Senateseats(1)-0.5 Senateseats(10)+0.5 0 max(histogram)*105])
xlabel('Democratic+Independent Senate seats','FontSize',14);
ylabel('Probability (%)','FontSize',14)
set(gcf, 'InvertHardCopy', 'off');
title('Distribution of all possible outcomes','FontSize',14)

Dstr=['D control: ',num2str(round(D_Senate_control_probability*100)),'%'];
Rstr=['R control: ',num2str(round(R_Senate_control_probability*100)),'%'];
% text(Senateseats(3)-0.35,max(histogram)*99,Rstr,'FontSize',18)
% text(Senateseats(13)-2.3,max(histogram)*99,Dstr,'FontSize',18)
if analysisdate==0
    datelabel=datestr(now);
else
    datelabel=datestr(analysisdate);
end
text(44,max(histogram)*97,datelabel(1:6),'FontSize',12)
text(44,max(histogram)*91,'election.princeton.edu','FontSize',12)
if biaspct==0
%    set(gcf,'PaperPositionMode','auto') % run this on laptop
%    print -djpeg Senate_histogram_today.jpg % run this on laptop
     screen2jpeg(['Senate_histogram_today.jpg']) % run this on server
end
%
% end plot
%

%
%    Start calculating some outputs
%
confidenceintervals(3)=Senateseats(find(cumulative_prob<=0.025,1,'last')); % 95-pct lower limit
confidenceintervals(1)=Senateseats(find(cumulative_prob<=0.15865,1,'last')); % 1-sigma lower limit
confidenceintervals(2)=Senateseats(find(cumulative_prob>=0.84135,1,'first')); % 1-sigma upper limit
confidenceintervals(4)=Senateseats(find(cumulative_prob>=0.975,1,'first')); % 95-pct upper limit

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
%    1 value - date of analysis
%    1 value - median_seats for Democrats/Independents (integer)
%    1 value - mean_seats for Democrats/Independents (round to 0.01)
%    1 value - Democratic/Independent control probability (round to 1%)
%    3 values - assigned (>95% prob) seats for each party (integers) and
%    uncertain
%    1 value - number of state polls used to make the estimates (integer)
%    1 value - +/-1 sigma CI for Democratic/Independent Senate seats (integers)
%    1 value - (calculated by Senate_metamargin and appended) the meta-margin
%    1 value - mean margin in contested states
% 
outputs=[median_seats mean_seats Dcontrolprobs assignedEV totalpollsused confidenceintervals(1:2) mean(polldata(contested,3))];    

if biaspct==0
%   Export probability histogram:
    dlmwrite('Senate_histogram.csv',histogram')
%   Export state-by-state percentage probabilities as CSV, with 2-letter state abbreviations:
%   Each line includes hypothetical probabilities for D+2% and R+2% biases
%   Also give margin
    if exist('Senate_stateprobs.csv','file')
        delete('Senate_stateprobs.csv')
    end
    
% old calculation, purely a snapshot with drift, used until October 11:
%    foo=(polls.margin)./sqrt(polls.SEM.^2+25);
%    statenovprobs=round((erf(foo/sqrt(2))+1)*50);
%    foo=(polls.margin+2)./polls.SEM;
%    D2probs=round((erf(foo/sqrt(2))+1)*50);
%    foo=(polls.margin-2)./polls.SEM;
%    R2probs=round((erf(foo/sqrt(2))+1)*50);

daystoelection=datenum('06-Nov-2018')-today; % days until election (note: November 6, Julian 311)
for istate=1:length(polls.margin)
    [~,statenovprobs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate),0.8,7,3,polls.margin(istate)+1.9,10);
    [~,D2probs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate)+2,0.8,7,3,polls.margin(istate)+1.9,10);
    [~,R2probs(istate),~]=Bayesian_November_prediction(daystoelection,polls.margin(istate)-2,0.8,7,3,polls.margin(istate)+1.9,10);
end
statenovprobs=round(statenovprobs*100); D2probs=round(D2probs*100); R2probs=round(R2probs*100);

% column 1: Today's snapshot D win probability
% column 2: November D win probability
% column 3: median margin (positive indicates D is front-runner)
% column 4: November win probability adding 2% to margin for D
% column 5: November win probability adding 2% to margin for R
% column 6: Two-letter postal abbreviation of state

for ii=1:num_states
        foo=[num2str(stateprobs(ii)) ',' num2str(statenovprobs(ii)) ',' num2str(polls.margin(ii)) ',' num2str(D2probs(ii)) ',' num2str(R2probs(ii)) ',' statename2(ii,polls.state)];
        dlmwrite('Senate_stateprobs.csv',foo,'-append','delimiter','')
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
    while median_seats < 51
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
dlmwrite('Senate_estimates.csv', outputs) % just today's estimate

todayrow = csvread('Senate_estimate_history.csv');
julian = today- datenum('1-Jan-2018')
if todayrow(end, 1) ~= julian - 1 || todayrow(end, end) ~= metamargin
	if forhistory
        if todayrow(end, 1) ~= julian - 1
	        dlmwrite('Senate_estimate_history.csv',[polldata(1,5) outputs],'-append')
        else
            todayrow(end, :) = [polldata(1,5) outputs];
	        dlmwrite('Senate_estimate_history.csv', todayrow);
        end
	end
end
