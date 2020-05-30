%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% The calculation %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Calculate z-score and convert to probability, assuming normal distribution.
polls.z=(polls.margin+biaspct)./polls.SEM;
polls.prob_Dem_win=(erf(polls.z/sqrt(2))+1)/2;
polls.prob_GOP_win=1-polls.prob_Dem_win;
stateprobs=round(polls.prob_Dem_win*100);

% The meta-magic
EV_distribution=[polls.prob_Dem_win(1) zeros(1, polls.EV(1)-1) 1-polls.prob_Dem_win(1)];
for i=2:num_states
    nextEV=[polls.prob_Dem_win(i) zeros(1, polls.EV(i)-1) 1-polls.prob_Dem_win(i)];
    EV_distribution=conv(EV_distribution,nextEV);
end
clear nextEV
% EV_distribution is the exact probability distribution of 
% all 2,251,799,813,685,248 (2.3 quadrillion) possible outcomes. (Wow!)

% Cumulative histogram of all possibilities
histogram=fliplr(EV_distribution(1:538)); %index of 1 for 1 EV...index of 538 for 538 EV
cumulative_prob=cumsum(histogram);
electoralvotes=1:538;

% Calculate median and confidence bands from cumulative histogram
medianEV(1)=electoralvotes(min(find(cumulative_prob>=0.5)));  % 50-pct outcome