%whereoutputs='C:\Users\sswang\Desktop\pollcalc\pollcalc20\outputs\'; 
whereoutputs='outputs/'; 

%House_history=load(strcat(whereoutputs,'2022.generic.polls.median.txt'));
House_history=load('2022.generic.polls.median.txt');
d=House_history(:,5);
House_m=House_history(:,3);
House_msd=House_history(:,4);

%%%%% Combine diffusion with a special-election-based prior 
today=floor(now)
N=datenum('08-Nov-2022')-today; % days until election (note for 2022: November 8, Julian 313)
current_mm=House_m(max(find(d==max(d)))); % Find the most recent median margin
current_msd=House_msd(max(find(d==max(d)))); % Find the most recent median margin

maxdrift=4.5; % assumes modern levels of entrenchment
Mdrift=min(0.4*sqrt(N),maxdrift); % following Presidential patterns; should fill this in with House data when available
Mdrift=real(max(Mdrift,2)); % just in case something is screwy like N<0. 

% cover range of +/-4 sigma
Mrange=[current_mm-4*Mdrift:0.02:current_mm+4*Mdrift];

% What is near-term drift starting from conditions now?
nowdensity=tpdf((Mrange-current_mm)/Mdrift,3); % t-distribution is long-tailed. you never know.
nowdensity=nowdensity/sum(nowdensity);

% What was long-term prediction? (the prior)
specials_2022=-1; % LAST UPDATE: August 22 2022
specials_2022SD=3; % not that many previous examples
prior=tpdf((Mrange-specials_2022)/specials_2022SD,1); % make it really long-tailed, df=1
prior=prior/sum(prior);

% Combine to make prediction
prediction=nowdensity.*prior; % All hail Reverend Bayes
prediction=prediction/sum(prediction);

% Define mean and error bands for prediction
predictmean=sum(prediction.*Mrange)/sum(prediction)
for i=1:length(Mrange)
   cumulpredict(i)=sum(prediction(1:i));
end
Msig1lo=Mrange(min(find(cumulpredict>normcdf(-1,0,1))))
Msig1hi=Mrange(min(find(cumulpredict>normcdf(+1,0,1))))
Msig2lo=Mrange(min(find(cumulpredict>normcdf(-2,0,1))))
Msig2hi=Mrange(min(find(cumulpredict>normcdf(+2,0,1))))

bayesian_winprob=sum(prediction(find(Mrange>=0)))/sum(prediction)
drift_winprob=tcdf(current_mm/Mdrift,3) % df=3

if ~exist('whereoutputs','var')
    whereoutputs='';
end

%% write median margin prediction to csv for plotter scripts
outputs = [predictmean Msig1lo Msig1hi Msig2lo Msig2hi bayesian_winprob drift_winprob];
dlmwrite(strcat(whereoutputs,'House_predictions.csv'), outputs)
