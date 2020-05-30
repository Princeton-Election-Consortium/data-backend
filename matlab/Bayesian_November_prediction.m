function [predictmean,drift_winprob,bayesian_winprob]=Bayesian_November_prediction(daystoelection,MM,driftrate,maxdrift,mindrift,Prior2016,Prior2016SD)

MMdrift=min(driftrate*sqrt(daystoelection),maxdrift);
MMdrift=real(max(MMdrift,mindrift)); % just in case something is screwy like N<0

% cover range of +/-4 sigma
Mrange=[MM-4*MMdrift:0.02:MM+4*MMdrift];

% What is near-term drift starting from conditions now?
nowcond=tpdf((Mrange-MM)/MMdrift,3); % long-tailed distribution. you never know.
nowcond=nowcond/sum(nowcond);

% What was long-term prediction? (the prior)
prior=tpdf((Mrange-Prior2016)/Prior2016SD,1); %make it really long-tailed
prior=prior/sum(prior);

% Combine to make prediction
pred=nowcond.*prior; % All hail Reverend Bayes
pred=pred/sum(pred);

close
plot(Mrange,nowcond,'-k') % drift from today
hold on
plot(Mrange,prior,'-g') % the prior
plot(Mrange,pred,'-r') % the prediction
grid on

% Define mean and error bands for prediction
predictmean=sum(pred.*Mrange)/sum(pred);
for i=1:length(Mrange)
   cumulpredict(i)=sum(pred(1:i));
end

bayesian_winprob=sum(pred(find(Mrange>=0)))/sum(pred);
drift_winprob=tcdf(MM/MMdrift,3);
