%regenerate data from March 2 to now
for analysisdate=62:floor(today-datenum('31-dec-2021'))
    forhistory=1;
    Senate_estimator_2022
    % Senatehistfilename=['oldhistograms\Senate_histogram_' num2str(analysisdate,'%i') '.jpg']
    %copyfile('Senate_histogram_today.jpg',Senatehistfilename);
end