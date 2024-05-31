whereoutputs='outputs/';
Senate_history=load(strcat(whereoutputs,'Senate_estimate_history.csv'));
d=Senate_history(:,1);
mm=Senate_history(:,12);

% GE candidates are not even known until the end of August in some cases. 
% It is best to wait until 90 days before election to attempt Senate prediction
%
% Senate 2016: invoke as [predictmean,drift,bayes]=Bayesian_November_prediction(daystoelection,current_mm,0.6,5,1,1.9,6.8)
% Senate 2022: invoke as [predictmean,drift,bayes]=Bayesian_November_prediction(daystoelection,current_mm,0.6,5,1,2.5,8)
% 2016 the PriorMM (formerly called Prior 2016) was 1.9.
% 2022 set to 2.5
% maxdrift=4 would be be more than the drift for EV.
%Prior2016=1.9 % corresponds to 50.4 D+I seats: Sabato, lean=0.33/0.67, likely=0.2/0.8, tossup=0.5, interpolate using MM history
%Prior2016SD=6.8; 
   % For Senate, 14 races not "safe" according to Sabato. 
   % binomial error in #seats is sigma=0.4-0.5/race
   % Presidential year - use a propagated error that is midway between independence and total covariation.
   % midterm year - what to do? probably assume total covariation, big error.
   % June-August 2016: 1.7% MM per single-party seat change.

%%%%% Combine diffusion with a prognosticator-based prior (Sabato)
h=datenum('08-Nov-2022')-today; % days until election (note: November 8, Julian 314)
current_mm=mm(max(find(d==max(d)))); % Find the most recent Meta-Margin

[predicted_mm,drift,bayes]=Bayesian_November_prediction(h,current_mm,0.6,4.5,1.5,2.5,8)
D_November_control_probability=bayes*100;

dlmwrite(strcat(whereoutputs,'Senate_D_November_control_probability.csv'),[today-datenum('31-Dec-2021') D_November_control_probability predicted_mm])
%%%%% end November prediction calculation
