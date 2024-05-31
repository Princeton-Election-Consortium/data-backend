function [URL1 URL2 URL3]=write_270towin_strings(statep,Dprobs,Rprobs,path270,pathhere);
% Generates URLs like http://www.270towin.com/maps/22211111130162122221111522232211131621512226211112211222
% The string is a 56-digit sequence in which the first 51 correspond to the states+DC in alphabetical order by two-letter postal abbreviation, i.e.
% AK AL AZ AR CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY
% Note that this is not the same order as PEC! :-P
%
% In these first 51 characters, the entries for ME and NE appear not to do anything. Then positions 52-53 show Maine's special district rule, and 54-55-56 show Nebraska's special district rule.
% Code positions 22, 52, and 53 are based on the Maine probability statewide and with PVI corrections by district. 30, 54, 55, and 56 the same based on the Nebraska probability.
%
% Create a string based on the lookup table in column 1 of stateprobs.csv, as follows:
% 1= deep blue, 95-100%
% 3=medium blue, 80-94.99%
% 5=light blue, 60-79.99%
% 0=gray, 40-60%
% 6=light red, 20.01-40%
% 4=medium red, 5.01-20%
% 2= deep red, 0-5%
%
% Then make a +2% for the Democratic candidate using column 3, and a +2% for the Republican candidate using column 4. 
 
colors270=['2','4','6','0','5','3','1'];
thresholds270=[-0.1 5 20 40 60 80 95];

PEC_order='AL,AK,AZ,AR,CA,CO,CT,DC,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY,M1,M2,N1,N2,N3 ';
towin_ord='AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY M1 M2 N1 N2 N3 ';
for iPEC=1:56
    P270(iPEC)=(findstr(towin_ord(iPEC*3-2:iPEC*3-1),PEC_order)+2)/3;
end

str270=path270; str270_D=path270; str270_R=path270;
for i270=1:56
    str270=[str270 colors270(max([find(statep(P270(i270))>=thresholds270) 1]))];
    str270_D=[str270_D colors270(max([find(Dprobs(P270(i270))>=thresholds270) 1]))];
    str270_R=[str270_R colors270(max([find(Rprobs(P270(i270))>=thresholds270) 1]))];
end

% write outputs
    if exist('pathhere','var')
        fid270=fopen(strcat(pathhere,'270towin_URL.txt'),'w');
    else
        fid270=fopen('270towin_URL.txt','w');
    end 
    fprintf(fid270,[str270 '\r'])
    fprintf(fid270,[str270_D '\r'])
    fprintf(fid270,[str270_R '\r'])
    fclose(fid270)
    URL1=str270; URL2=str270_D; URL3=str270_R;
end
