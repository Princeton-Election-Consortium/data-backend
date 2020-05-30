% The first three lines need to be removed, and replaced by passing the % Meta-Margin and today's date to the script.

MM=metamargin; % today's Meta-Margin

today=floor(now)
N=datenum(2020,11,3)-today; % assuming date is set correctly in machine
% MMdrift=sigmadrift;
% maxdrift=1.8; % empirical from 2012; used it that year
% maxdrift=6; % historical data, Eisenhower to 2012. Used this 6/1 to 8/19
maxdrift=3; % in between. Similar to what it was in 1996-2012. Assumes modern levels of entrenchment
MMdrift=min(0.4*sqrt(N),maxdrift);
MMdrift=real(max(MMdrift,1.5)); % just in case something is screwy like N<0. In 2016 the min ws set at 0.4 points, led to probability error. change to 1.5 for 2020 which would have given 31% win probability for Trump

% cover range of +/-4 sigma
Mrange=[MM-4*MMdrift:0.02:MM+4*MMdrift];

% What is near-term drift starting from conditions now?
nowdensity=tpdf((Mrange-MM)/MMdrift,3); % long-tailed distribution. you never know.
nowdensity=nowdensity/sum(nowdensity);

% What was long-term prediction? (the prior)
M2016=mean_MM('EV_estimate_history.csv',3.5); % starting 8/19, calculate this from time series for 2016
M2016SD=6; % parameters of long-term prediction; would September be a good time to start to use actual SD of MM?
prior=tpdf((Mrange-M2016)/M2016SD,1); %make it really long-tailed, df=1
prior=prior/sum(prior);

% Combine to make prediction
pred=nowdensity.*prior; % All hail Reverend Bayes
pred=pred/sum(pred);


plot(Mrange,nowdensity,'-k') % drift from today
hold on
plot(Mrange,prior,'-g') % the prior
plot(Mrange,pred,'-r') % the prediction
grid on

% Define mean and error bands for prediction
predictmean=sum(pred.*Mrange)/sum(pred)
for i=1:length(Mrange)
   cumulpredict(i)=sum(pred(1:i));
end
Msig1lo=Mrange(min(find(cumulpredict>normcdf(-1,0,1))))
Msig1hi=Mrange(min(find(cumulpredict>normcdf(+1,0,1))))
Msig2lo=Mrange(min(find(cumulpredict>normcdf(-2,0,1))))
Msig2hi=Mrange(min(find(cumulpredict>normcdf(+2,0,1))))

% Now convert to EV using data from poll-based calcuations and some added points at the
% ends. If the race swings far, these endpoints need to be re-evaluated.
%mmf=[-9.38 -4.38 -3.38 -2.38  -3 -2.5 -1.5 -0.5 0   0.5 1.5 2.5 3.62 4.62 5.62 6.62 7.62 8.62 9.62 10.62 11.62 12.62 13.62 14.62 15.62 16.62 17.62 18.62 19.62];
%evf=[170    214    224   236 228  234  247  260 269 276 293 309 328  343  358  374  391   406  412  412   412   412   412   413   413   413   416   422   425];
EV_MM_table=load('EV_MM_table.csv');
mmf=EV_MM_table(:,1);
evf=EV_MM_table(:,2);
[mmf,ia,ic]=unique(mmf);
evf=evf(ia);
bands = interp1(mmf,evf,[predictmean Msig1lo Msig1hi Msig2lo Msig2hi],'linear');
bands = round(bands)
ev_prediction = bands(1);
ev_1sig_low = bands(2);
ev_1sig_hi = bands(3);
ev_2sig_lo = bands(4);
ev_2sig_hi = bands(5);

bayesian_winprob=sum(pred(find(Mrange>=0)))/sum(pred)
drift_winprob=tcdf(MM/MMdrift,3)

if ~exist('whereoutput','var')
    whereoutput='';
end
%% write to csv for plotter scripts
outputs = [ ev_1sig_low ev_1sig_hi ev_2sig_lo ev_2sig_hi ];
dlmwrite(strcat(whereoutput,'EV_prediction.csv'), outputs)

%% write probabilities to csv
outputs = [ bayesian_winprob drift_winprob ];
dlmwrite(strcat(whereoutput,'EV_prediction_probs.csv'), outputs)

%% write meta-margin prediction to csv for plotter scripts
outputs = [ Msig1lo Msig1hi Msig2lo Msig2hi ];
dlmwrite(strcat(whereoutput,'EV_prediction_MM.csv'), outputs)
