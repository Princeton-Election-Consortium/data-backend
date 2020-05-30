%LIBGL_DEBUG='verbose'
Senate_history=load(strcat(whereoutput,'Senate_estimate_history.csv'));
d=Senate_history(:,1);
medians=Senate_history(:,2);
means=Senate_history(:,3);
pr=Senate_history(:,4)*100;
meanm=Senate_history(:,11);
mm=Senate_history(:,12);

vrange=[46 56];
startday=datenum('01-Apr-0000')
endday=330
phandle=plot([60 endday],[49.5 49.5],'-r','LineWidth',1);
hold on
monthticks=datenum(0,4:12,1);
set(gca,'xtick',monthticks,'FontSize',12)
set(gca,'ytick',[vrange(1):vrange(2)],'FontSize',12)
set(gca,'XTickLabel',{'              Apr','              May','              Jun','              Jul','              Aug','              Sep','              Oct','         Nov'})
grid on
axis([startday endday vrange])
plot(d,means,'-k','LineWidth',1.5)
% monthstarts=[32 61 92 122 153 183 214 245 275 306];
% for ii=1:length(monthstarts)
%    plot([monthstarts(ii) monthstarts(ii)],vrange,'-k')
% end
ylabel('Democratic/Independent seats (%)','FontSize',14)
text(startday+3,0.95*vrange(1)+0.05*vrange(2),'election.princeton.edu','FontSize',12)
set(gcf, 'InvertHardCopy', 'off');
title('Snapshot of expected Democratic Senate seats, 2020','FontSize',14)

%set(gcf, 'Renderer', 'OpenGL')
opengl software % added 6/19/16 because suddenly MATLAB started hanging when trying to print a picture with transparency
[fillhandle,msg]=jbfill(d',Senate_history(:,10)'+0.1,Senate_history(:,9)'-0.1,'k','g',1,0.1); % for confidence interval band
% see http://www.mathworks.com/matlabcentral/fileexchange/loadFile.do?objectId=13188&objectType=FILE

%set(gcf,'PaperPositionMode','auto')
%print -djpeg Senate_seat_history.jpg
screen2jpeg(['Senate_seat_history.jpg'])
%saveas(gcf,'Senate_seat_history.jpg','jpg')
close

% Now do Meta-margin plot
vrange=[-2 6];
startday=datenum('01-Apr-0000')
endday=330

phandle=plot([60 endday],[0 0],'-r','LineWidth',1);
hold on
set(gca,'xtick',monthticks,'FontSize',12)
set(gca,'ytick',[vrange(1):vrange(2)],'FontSize',12)
set(gca,'XTickLabel',{'              Apr','              May','              Jun','              Jul','              Aug','              Sep','              Oct','         Nov'})
set(gca,'YTickLabel',{'R+2%','+1%','0','+1%','+2%','+3%','+4%','+5%','D+6%'})
grid on
axis([startday endday vrange])
plot(d,mm,'-k','LineWidth',1.5)
plot(d(length(d)),mm(length(d)),'ok','LineWidth',1)
ylabel('Meta-margin (%)','FontSize',14)
text(startday+3,0.95*vrange(1)+0.05*vrange(2),'election.princeton.edu','FontSize',12)
set(gcf, 'InvertHardCopy', 'off');
title('Popular meta-lead for Senate control, 2020','FontSize',14)

%set(gcf,'PaperPositionMode','auto')
%print -djpeg Senate_metamargin_history.jpg
screen2jpeg(['Senate_metamargin_history.jpg'])
