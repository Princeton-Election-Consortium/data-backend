%%%  Senate_jerseyvotes.m - a MATLAB script
%%%  Copyright 2008, 2014, 2016. 2022 by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.
%%%
%%%  Updated by Andrew Ferguson on Oct 8, 2008 to ensure that at least ten
%%%  states are displayed.
%%%
%%%  Updated from EV to Senate-specific calculation in July 2014 by Sam
%%%  Wang. Updated to reflect current races in 2022.

% Likelihood analysis of all possible outcomes of election based 
% on the meta-analytical methods of Prof. Sam Wang, Princeton University.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Senate_jerseyvotes.m
% 
% This script assumes that Senate_estimator has just been run!!!
% This script generates 1 CSV file:
% 
% jerseyvotes.csv
%    The file has the same number of lines as the number of uncertain
%    states. These are not necessarily the same states.
%    Each line has 3 fields:
%       - the index number of a state
%       - its two-letter postal abbreviation
%       - the power of a voter in that state to influence the overall
%           election outcome, normalized to a voter in NJ
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set up range of possibilities
%clear now
%today=floor(now);
%daystoelection=ELECTION_DATE-today; % assuming date is set correctly in machine


% Phousawanh; implement closed form from Sam 

%{

DAYS_UNTIL_ELECTION = days(datetime(2024,11,5) - datetime('today'));

MMsigma=max(sqrt(DAYS_UNTIL_ELECTION),1.5);

% A distribution of possible amounts of drift from now to Election Day:
Mrange=[-2*MMsigma:0.1:2*MMsigma];% cover range of +/-2*MMsigma
nowdensity=tpdf(Mrange/MMsigma,3); % long-tailed distribution. you never know.
nowdensity=nowdensity/sum(nowdensity);

jerseyv_accumulator=zeros(1,num_states);



for ii=length(Mrange)
    polls.margin=polls.margin+Mrange(ii); % set polls to one possible amount of drift

    % biaspct=0;
    if metamargin>-999
        biaspct=-metamargin; % changed on 8/8/08 to reflect discussion w/reader James
    end
    Senate_median
    midpoint=cumulative_prob(min(find(Senateseats>=50))); % P(Dem control) under knife-edge conditions

    clear difference
    for state=1:num_states
        polls.margin(state)=polls.margin(state)-0.1; % perturb one poll by 0.1 percentage point
        Senate_median
        probability_GOP_win=cumulative_prob(min(find(Senateseats>=50)));
        difference(state)=(probability_GOP_win-midpoint)*10000; % how much is P(Dem control) changed?
        polls.margin(state)=polls.margin(state)+0.1; % put the poll back where it was
    end

    % actual number of voters in previous election
    % data from: http://www.electproject.org/2016g
    % be sure that the order of this array matches the order of the state array in Senate_estimator
    % in 2022: 'AZ,CO,FL,GA,MO,NC,NH,NV,OH,PA,UT,WI ' 12 races.
    % kvoters=[3387 3257 11067 5000 3026 5525 806 1405 5922 6915 1488]; %2020 numbers -- need to fix for 2024
    % in 2024: 'AZ,FL,MD,MI,MT,NE,NV,OH,PA,TX,WI,WV' 11 races 
    
    %kvoters = [2592 7797 2031 4500 468 1024 4201 5410 8152 2673 495]; % 2022 numbers -- should update when 2024 comes out
    kvoters = [3420 11145 3067 5579 612 966 1408 5974 6958 11350 3310 803];
    disp(size(difference))
    disp(size(kvoters))
    jerseyvotes=difference./kvoters; % convert to per-voter power

    jerseyv_accumulator=jerseyv_accumulator+jerseyvotes*nowdensity(ii);
    polls.margin=polls.margin-Mrange(ii); % set polls back to their true medians
end

% jerseyvotes=jerseyvotes/jerseyvotes(31); % gives exact ratios
% jerseyvotes=round(10*jerseyvotes/jerseyvotes(31))/10; % gives tenths
% jerseyvotes=roundn(jerseyvotes,floor(log10(jerseyvotes))-1); % gives top two significant figures

jerseyvotes=100*jerseyv_accumulator/max(jerseyv_accumulator); 
% normalizes to the most powerful state, which is defined as 100; see
% discussion 8/8/08 with James


for i=1:num_states
    %if i~=31
        % jerseyvotes(i)=roundn(jerseyvotes(i),-1); % roundn deprecated %  No need to do this since NJ is not included in Senate
    jerseyvotes(i)=round(jerseyvotes(i),-1);
end
% round everything but NJ itself to the nearest tenth 
% the index of 31 is not actually right; it needs to be whatever the index
% of NJ is this year. Decided to leave it out; a step toward retiring the
% jerseyvote concept

%}

%%{
sigma = 6; 
impact = 1; 
df = 1;
% in 2024: 'AZ,FL,MD,MI,MT,NE,NV,OH,PA,TX,WI,WV' 11 races 
% kvoters = [2592 7797 2031 4500 468 1024 4201 5410 8152 2673 495];

kvoters = [3420 11145 3067 5579 612 966 1408 5974 6958 11350 3310 803];
Senate_median

z = (polls.margin - metamargin)/sigma;
voterpower = (tpdf(z,df).*impact)./kvoters; 
voterpower = (voterpower / max(voterpower))*100;

% round 
for i=1:num_states
    voterpower(i) = round(voterpower(i));
end

jerseyvotes = voterpower; % change later so all jerseyvotes -> voterpower
%}

[foo, ijersey]=sort(jerseyvotes);
display_num=max(size(uncertain,2), 10);
display_num=num_states;

if ~exist(whereoutput)
        whereoutput='';
end
if exist(strcat(whereoutput,SENATE_JERSEYVOTES_CSV),'file')
        delete(strcat(whereoutput,SENATE_JERSEYVOTES_CSV))
end
for i=num_states:-1:(num_states-display_num+1)
    foo=[num2str(ijersey(i)) ',' statename2(ijersey(i),polls.state) ',' num2str(polldata(ijersey(i),3)) ',' num2str(jerseyvotes(ijersey(i))) ];
    dlmwrite(strcat(whereoutput,SENATE_JERSEYVOTES_CSV),foo,'-append','delimiter','')
end
%foo=[num2str(31) ',' statename(31) ',' num2str(jerseyvotes(31)) ];
%dlmwrite('jerseyvotes.csv',foo,'-append','delimiter','')
