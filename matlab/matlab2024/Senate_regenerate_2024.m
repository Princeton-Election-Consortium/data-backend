%regenerate data from April 21 to now
for analysisdate=112:floor(today-datenum('31-dec-2023'))
    forhistory=1;
    Senate_estimator_2024
    Senatehistfilename=['oldhistograms\Senate_histogram_' num2str(analysisdate,'%i') '.jpg']
    copyfile('Senate_histogram_today.jpg',Senatehistfilename);
end