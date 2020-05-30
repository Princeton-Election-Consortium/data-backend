%clear
close
load outputs/EV_estimate_history.csv
%    Each line of EV_estimate_history should contain:
%    1 value - date code
%    2 values - medianEV for the two candidates, where a margin>0 favors the first candidate (in our case, Clinton);
%    2 values - modeEV for the two candidates;
%    3 values - assigned (>95% prob) EV for each candidate, with a third entry for undecided;
%    4 values - confidence intervals for candidate 1's EV: +/-1 sigma, then
%    95% band; and
%    1 value - number of state polls used to make the estimates.
%    1 value - (calculated by EV_metamargin and appended) the meta-margin.

load outputs/EV_prediction.csv
%    EV_prediction.csv currently contains 2-sigma and 1-sigma confidence
%    bands for landing on Election Day

[dates,ix]=sort(EV_estimate_history(:,1));
medianDT=538-EV_estimate_history(ix,2); % Invert everything to score EV for GOP incumbent president
modeDT=538-EV_estimate_history(ix,4);
lowDT95=538-EV_estimate_history(ix,11);
highDT95=538-EV_estimate_history(ix,12);

phandle=plot([0 365],[269 269],'r-','LineWidth',1);
hold on
monthticks=datenum(0,4:12,1);
set(gca,'xtick',monthticks)
set(gca,'ytick',[100:20:400])
set(gca,'XTickLabel',{'              Apr','              May','              Jun','              Jul','              Aug','              Sep','              Oct','         Nov'})
grid on
maxEV=360;
axis([90 320 100 maxEV])
set(gcf, 'InvertHardCopy', 'off');
title('President 2020 - state-poll-based estimator [95% CI]','FontSize',14)
ylabel('Trump electoral votes','FontSize',14)
text(95,maxEV-12,'election.princeton.edu','FontSize',11)
text(125,277,'Trump leads','FontSize',11)
text(125,263,'Biden leads','FontSize',11)

plot(dates,medianDT,'-k','LineWidth',1.5)
plot(dates(length(dates)),medianDT(length(dates)),'.k','LineWidth',1.5)
strikedate=datenum('4-nov-2020')-datenum('31-dec-2019');
plot([strikedate strikedate],[538-EV_prediction(3:4)],'-y','LineWidth',3)
plot([strikedate strikedate],[538-EV_prediction(1:2)],'-r','LineWidth',3)

[fillhandle,msg]=jbfill(dates',highDT95',lowDT95','k','w',1,0.2);
% see http://www.mathworks.com/matlabcentral/fileexchange/loadFile.do?objectId=13188&objectType=FILE

% still could add:
% right hand axis labels for McCain EV
% text(330,285,'McCain EV','Rotation',270,'HorizontalAlignment','center','VerticalAlignment','middle','FontSize',14)

set(gcf,'PaperPositionMode','auto')
print -djpeg EV_history.jpg
