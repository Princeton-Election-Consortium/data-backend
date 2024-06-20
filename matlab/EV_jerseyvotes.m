%%%  EV_jerseyvotes.m - a MATLAB script
%%%  Copyright by Samuel S.-H. Wang
%%%  Noncommercial-use-only license: 
%%%  You may use or modify this software, but only for noncommercial purposes. 
%%%  To seek a commercial-use license, contact the author at sswang@princeton.edu.

% Likelihood analysis of all possible outcomes of election based 
% on the meta-analytical methods of Prof. Sam Wang, Princeton University.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EV_jerseyvotes.m
% 
% This script assumes that EV_estimator has just been run!!!
% This script generates 1 CSV file:
% 
% jerseyvotes.csv
%    The file has the same number of lines as the number of uncertain
%    states. These are not necessarily the same states.
%    Each line has 3 fields:
%       - the index number of a state
%       - its two-letter postal abbreviation
%       - the power of a voter in that state to influence the overall
%           election outcome, normalized to a voter in NJs
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Set up range of possibilities
%clear now
%today=floor(now);

%daystoelection=ELECTION_DATE-today; % assuming date is set correctly in machine
MMsigma=min(0.4*sqrt(DAYS_UNTIL_ELECTION),3); % historical levels of Presidential drift post-2012 and consistent with 2020 so far
MMsigma=max(MMsigma,2); % final systematic uncertainty

Mrange=[-2*MMsigma:0.1:2*MMsigma];% cover range of +/-2*MMsigma
nowdensity=tpdf(Mrange/MMsigma,3); % long-tailed distribution. you never know.
nowdensity=nowdensity/sum(nowdensity);

jerseyv_accumulator=zeros(1,num_states);

for ii=length(Mrange)
    polls.margin=polls.margin+Mrange(ii);
    
    % biaspct=0;
%    if metamargin>-999
        biaspct=-metamargin; % shift data to a perfect toss-up
%    end

    EV_median
    midpoint=cumulative_prob(min(find(electoralvotes>=269)));

    for state=1:num_states
        polls.margin(state)=polls.margin(state)-0.1;
        EV_median
        probability_GOP_win=cumulative_prob(min(find(electoralvotes>=269)));
        difference(state)=(probability_GOP_win-midpoint)*10000;
        polls.margin(state)=polls.margin(state)+0.1;
    end

    % actual number of voters in previous election
    % data from: http://presidentelect.org/e2008.html
    % be sure that the order of this array matches the order of the state array in EV_estimator
    % 2004 data:  kvoters=[1883 313 2013 1055 12422 2130 1579 375 228 7610 3302 429 598 5274 2468 1507 1188 1796 1943 741 2387 2912 4839 2828 1152 2731 450 778 830 678 3612 756 7391 3501 313 5628 1464 1837 5770 437 1618 388 2437 7411 928 312 3198 2859 756 2997 243];
    % Data from 2020, needs to be updated with voter turnout in 2020
    % EV_STATES = [
    % 'AL,AK,AZ,AR,CA,CO,CT,DC,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY,M1,M2,N1,N2,N3 '];
    % old array used; 2008 data
    % voters = [1424 267 2592 914 11147 2541 1298 326 206 7797 3965 423 595 4144 1881 1230 1009 1503 1410 681 2032 2511 4500 2527 709 2304 468 682 1024 627 2646 715 5962 3790 243 4201 1153 1998 5410 361 1719 355 1757 8152 1085 292 3022 3068 495 2673 198]; 

    % voters=[2099819 326197 2293475 1086617 13464495 2401361 1646783 265853 412412 8390744 3921693 453568 655032 5513635 2751054 1530386 1235801 1826620 1960761 731163 2622549 3080985 5001766 2900873 1289865 2925205 490109 798444 961581 707611 3868237 830158 7590551 4296847 316621 5697927 1462661 1814251 5992384 471766 1920969 381975 2599749 8077795 942678 325046 3716905 3036878 713451 2976356 253137];
    % voters=[voters voters(20)/2 voters(20)/2 voters(28)/3 voters(28)/3 voters(28)/3]; % add Maine and Nebraska - deployed October 28 2016
    
    voters = [1424087 267047 2592313 914227 11146610 2540666 1297811 325632 205774 7796916 3964926 423443 595350 4144125 1880755 1230417 1008998 1502550 1410466 680909 2031635 2511461 4500400 2526646 709100 2304250 468326 682716 1023617 626931 2645539 714754 5962278 3790202 242566 4201368 1153284 1997689 5410022 361449 1718626 354670 1756397 8151590 1084634 291955 3021956 3067686 494753 2673154 198198]; 
    voters = [voters voters(20)/2 voters(20)/2 voters(28)/3 voters(28)/3 voters(28)/3]; % add Maine and Nebraska - deployed October 28 2016

    kvoters=round(voters/1000);
    jerseyvotes=difference./kvoters;

    jerseyv_accumulator=jerseyv_accumulator+jerseyvotes*nowdensity(ii);
    polls.margin=polls.margin-Mrange(ii);
end

% jerseyvotes=jerseyvotes/jerseyvotes(31); % gives exact ratios
% jerseyvotes=round(10*jerseyvotes/jerseyvotes(31))/10; % gives tenths
% jerseyvotes=roundn(jerseyvotes,floor(log10(jerseyvotes))-1); % gives top two significant figures

jerseyvotes=100*jerseyv_accumulator/max(jerseyv_accumulator); 
% normalizes to the most powerful state, which is defined as 100; see
% discussion 8/8/08 with James

% for i=1:num_states
%     if i~=31
%         jerseyvotes(i)=roundn(jerseyvotes(i),-1);
%     end
% end
% round everything but NJ itself to the nearest tenth

[foo, ijersey]=sort(jerseyvotes);
display_num=max(size(uncertain,2), 10);
display_num=56

if ~exist(whereoutput)
    whereoutput='';
end
EVjerseyfile=strcat(whereoutput,EV_JERSEYVOTES_CSV);
if exist(EVjerseyfile,'file')
        delete(EVjerseyfile)
end
for i=num_states:-1:(num_states-display_num+1)
    foo=[num2str(ijersey(i)) ',' statename(ijersey(i)) ',' num2str(jerseyvotes(ijersey(i))) ];
    dlmwrite(EVjerseyfile,foo,'-append','delimiter','')
end
%foo=[num2str(31) ',' statename(31) ',' num2str(jerseyvotes(31)) ];
%dlmwrite('jerseyvotes.csv',foo,'-append','delimiter','')
