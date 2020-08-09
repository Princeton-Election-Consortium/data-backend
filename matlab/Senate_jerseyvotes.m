%%%  Senate_jerseyvotes.m - a MATLAB script
%%%  Copyright 2008, 2014, 2016 by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.
%%%
%%%  Updated by Andrew Ferguson on Oct 8, 2008 to ensure that at least ten
%%%  states are displayed.
%%%
%%%  Updated from EV to Senate-specific calculation in July 2014 by Sam
%%%  Wang. Updated to reflect current races in June 2016.

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
clear now
today=floor(now);
daystoelection=datenum(2020,11,3)-today; % assuming date is set correctly in machine
MMsigma=max(0.4*sqrt(daystoelection),1.5);

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
    midpoint=cumulative_prob(min(find(Senateseats>=51))); % P(Dem control) under knife-edge conditions

    clear difference
    for state=1:num_states
        polls.margin(state)=polls.margin(state)-0.1; % perturb one poll by 0.1 percentage point
        Senate_median
        probability_GOP_win=cumulative_prob(min(find(Senateseats>=51)));
        difference(state)=(probability_GOP_win-midpoint)*10000; % how much is P(Dem control) changed?
        polls.margin(state)=polls.margin(state)+0.1; % put the poll back where it was
    end

    % actual number of voters in previous election
    % data from: http://www.electproject.org/2016g
    % be sure that the order of this array matches the order of the state array in Senate_estimator
    % in 2020: 'AL,AK,AZ,CO,GA,GS,IA,KS,KY,ME,MI,MN,MT,NH,NM,NC,SC,TX ' 18 races. GS=Georgia special
    kvoters=[2134 321 2661 2859 4165 4165 1581 1226 1955 772 4875 2968 517 756 804 4770 2124 8975]; %2016 numbers
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
    if i~=31
        jerseyvotes(i)=roundn(jerseyvotes(i),-1);
    end
end
% round everything but NJ itself to the nearest tenth
% the index of 31 is not actually right; it needs to be whatever the index
% of NJ is this year. Decided to leave it out; a step toward retiring the
% jerseyvote concept

[foo, ijersey]=sort(jerseyvotes);
display_num=max(size(uncertain,2), 10);
display_num=num_states;

if ~exist(whereoutput)
        whereoutput='';
end
if exist(strcat(whereoutput,'Senate_jerseyvotes.csv'),'file')
        delete(strcat(whereoutput,'Senate_jerseyvotes.csv'))
end
for i=num_states:-1:(num_states-display_num+1)
    foo=[num2str(ijersey(i)) ',' statename2(ijersey(i),polls.state) ',' num2str(polldata(ijersey(i),3)) ',' num2str(jerseyvotes(ijersey(i))) ];
    dlmwrite(strcat(whereoutput,'Senate_jerseyvotes.csv'),foo,'-append','delimiter','')
end
%foo=[num2str(31) ',' statename(31) ',' num2str(jerseyvotes(31)) ];
%dlmwrite('jerseyvotes.csv',foo,'-append','delimiter','')
