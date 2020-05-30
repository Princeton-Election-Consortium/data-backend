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

% biaspct=0;
if metamargin>-999
    biaspct=-metamargin; % changed on 8/8/08 to reflect discussion w/reader James
end
Senate_median
midpoint=cumulative_prob(min(find(Senateseats>=51)));

for state=1:num_states
    polls.margin(state)=polls.margin(state)-0.1;
    Senate_median
    probability_GOP_win=cumulative_prob(min(find(Senateseats>=51)));
    difference(state)=(probability_GOP_win-midpoint)*10000;
    polls.margin(state)=polls.margin(state)+0.1;
end

% actual number of voters in previous election
% data from: http://www.electproject.org/2012g
% be sure that the order of this array matches the order of the state array in Senate_estimator
kvoters=[301 2324 2596 8538 1590 5278 2663 2015 2757 4542 719 1017 5632 5742 3068];
jerseyvotes=difference./kvoters;

% jerseyvotes=jerseyvotes/jerseyvotes(31); % gives exact ratios
% jerseyvotes=round(10*jerseyvotes/jerseyvotes(31))/10; % gives tenths
% jerseyvotes=roundn(jerseyvotes,floor(log10(jerseyvotes))-1); % gives top two significant figures

jerseyvotes=100*jerseyvotes/max(jerseyvotes); 
% normalizes to the most powerful state, which is defined as 100; see
% discussion 8/8/08 with James

for i=1:num_states
%    if i~=31
        jerseyvotes(i)=roundn(jerseyvotes(i),-1);
%    end
end
% round everything but NJ itself to the nearest tenth

[foo, ijersey]=sort(jerseyvotes);
display_num=max(size(uncertain,2), 10);
display_num=num_states;

if exist('Senate_jerseyvotes.csv','file')
        delete('Senate_jerseyvotes.csv')
end
for i=num_states:-1:(num_states-display_num+1)
    foo=[num2str(ijersey(i)) ',' statename2(ijersey(i),polls.state) ',' num2str(polldata(ijersey(i),3)) ',' num2str(jerseyvotes(ijersey(i))) ];
    dlmwrite('Senate_jerseyvotes.csv',foo,'-append','delimiter','')
end
%foo=[num2str(31) ',' statename(31) ',' num2str(jerseyvotes(31)) ];
%dlmwrite('jerseyvotes.csv',foo,'-append','delimiter','')
