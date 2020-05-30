function outputstring=statename2(foo3,foo2)
statelist=foo2;
%statelist=['AL AK AZ AR CA CO CT DC DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY M1 M2 N1 N2 N3 '];

if bitand(foo3>=1,foo3<=(length(statelist)/3))

    ifoo=1+3*(foo3-1);

    outputstring=statelist(ifoo:ifoo+1);

else

    outputstring='XX';

end

clear statelist foo3 ifoo

end

