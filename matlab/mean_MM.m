function returnvalue=mean_MM(EVhistoryfile,defaultval)

if exist(EVhistoryfile,'file')
    historydata=dlmread(EVhistoryfile,',');
    dates=historydata(:,1);
    [C,IA,IC] = unique(dates);
    if length(IA)>0
        returnvalue=mean(historydata(IA,14));
    else
        returnvalue=defaultval;
    end
else
    returnvalue=defaultval;
end