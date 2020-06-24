
def get_formatted_state(state_name, inverse=False, url_format=False, electoral_district = False):
    states_hash = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District Of Columbia': 'DC',
        'Federated States Of Micronesia': 'FM',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Marshall Islands': 'MH',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Palau': 'PW',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',

        # weird ones here
        "National" : "USA",
        "Maine CD-1" : "ME-1",
        "Maine CD-2" : "ME-2",
        "Maine CD-1" : "M1",
        "Maine CD-2" : "M2",
        "Nebraska CD-1": "N1",
        "Nebraska CD-2": "N2",
        "Nebraska CD-3": "N3",
    }

    if (electoral_district == True):
        state = 'invalid input'
        converts = {
            # "M1" : "ME CD1",
            # "M2" : "ME CD2",
            # "N1" : "NE CD1",
            # "N2" : "NE CD2",
            # "N3" : "NE CD3",
            "M1" : "ME-1",
            "M2" : "ME-2",
            "N1" : "NE-1",
            "N2" : "NE-2",
            "N3" : "NE-3",
        }
        if state_name in converts:
            return converts[state_name]
        return state

    elif (url_format == True):
        state = 'invalid input'
        for key, value in states_hash.items() :
            if value == state_name:
                state = key
                break
        return state.replace(" ", "-").lower()
  
    elif(inverse == True):
        state = 'invalid input'
        for key, value in states_hash.items() :
            if value == state_name:
                state = key
                break
        return state

    return states_hash[state_name]