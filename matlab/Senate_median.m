%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%% The calculation %%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Changes for Senate projection
%    make the histogram num_states wide
%    use EV variable to give 1 seat per race (keep variable name same)
%
% Calculate z-score and convert to probability, assuming normal distribution.
% Changed df of t distribution to be 3
polls.z=(polls.margin+biaspct)./polls.SEM;
polls.prob_Dem_win=tcdf(polls.z,3); % polls.prob_Dem_win=(erf(polls.z/sqrt(2))+1)/2;
polls.prob_GOP_win=1-polls.prob_Dem_win;
%
polls.znov=(polls.margin+biaspct)./sqrt(polls.SEM.*polls.SEM+5*5);
polls.prob_Dem_November=tcdf(polls.znov,3);
%polls.prob_Dem_November=(erf(polls.znov/sqrt(2))+1)/2;
%
stateprobs=round(polls.prob_Dem_win*100);
statenovprobs=round(polls.prob_Dem_November*100);

% The meta-magic
EV_distribution=[1-polls.prob_Dem_win(1) polls.prob_Dem_win(1)];
for i=2:num_states
    nextEV=[1-polls.prob_Dem_win(i) polls.prob_Dem_win(i)];
    EV_distribution=conv(EV_distribution,nextEV);
end
clear nextEV
% EV_distribution is the exact probability distribution of 
% all 2,251,799,813,685,248 (2.3 quadrillion) possible outcomes. (Wow!)
% 5 July 2014: code is same for Senate. In 2014, 36 races with 11 races in
% question. Therefore 2^11=2048 possibilities. In 2018, 10 races so 1024
% possibilities. In 2022, 12 races, 4096 possibilities. In 2024, 11 & 2048.

% Cumulative histogram of all possibilities
histogram=EV_distribution(1:num_states);
% histogram=EV_distribution(2:num_states+1); %index of 1 for 1 Dem/Ind seat...num_states for num_states seats
%  Truncate distribution by 1, which implicitly assumes at least one race will go to Democrats.
%  Seems ok, since otherwise we wouldn't bother doing a simulation.
cumulative_prob=cumsum(histogram);

%
% Calculate properties of distribution using cumulative histogram
% 5 July 2014: All variables below this line are new relative to EV_median.m
%
Senateseats=Demsafe+1:Demsafe+num_states;
R_Senate_control_probability=cumulative_prob(max(50-Demsafe,0));
% if Democrats/Independents get 49 or fewer, Republicans take over
% 49 because VP Harris is a Democrat. will need Demsafe from other script
% 50 in years when VP is a Republican.
D_Senate_control_probability=1-R_Senate_control_probability;
median_seats=Senateseats(min(find(cumulative_prob>=0.5))); % 50% of outcomes
mean_seats=sum(histogram.*Senateseats);
mean_seats=round(mean_seats*100)/100;