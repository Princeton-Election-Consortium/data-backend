from datetime import date, timedelta

# merges the two data from different sources, removing entries that are from the same pollster 
# taken at the same time (these are highly likely to be the same poll)
def merge_generic(t1, t2):
    t3 = []
    for row1 in t1:
        has_dup = False
        for row2 in t2:
            if row2['samplesize'] == row1['samplesize']:
            # if row1["pollster"] in row2["pollster"] or row2["pollster"] in row1["pollster"]:
                if row1["startdate"] == row2["startdate"] and row1["enddate"] == row2["enddate"]:
                    has_dup = True
        if not has_dup:
            t3.append(row1)
    return t3 + t2

# Takes in an array of dictionaries containing data formatted with FIELDNAME fields and removes rows
# that are exactly the same
def remove_dups(data):
    s = set()
    new_data = []
    for row in data:
        str_row = [str(e) for e in row.values()]
        rowstring = "".join(str_row)
        if rowstring in s: continue
        s.add(rowstring)
        new_data.append(row)
    return new_data

def merge_senate(t1, t2):
    t3 = []
    for row1 in t1:
        has_dup = False
        for row2 in t2:
            criteria = 0
            if abs((row1['D_support'] - row1['R_support']) - (row2['D_support'] - row2['R_support'])) <= 2:
                criteria += 1
            if row1['pollster'] == row2['pollster']:
                criteria += 1

            deltastart = abs(row1['startdate'] - row2['startdate'])
            deltaend = abs(row1['enddate'] - row2['enddate'])

            if deltastart.days < 2 and deltaend.days < 2:
                criteria += 1

            if row1['samplesize'] == row2['samplesize']:
                criteria += 1

            if row1['State_code'] == row2['State_code'] and criteria >= 2:
                has_dup = True
                break
        if has_dup == False:
            t3.append(row1)
    return t3 + t2

def remove_dups_senate(data):
    s = set()
    new_data = []
    for row in data:
        dminusr = row['D_support'] - row['R_support']
        rowstring = "".join([str(dminusr), str(row['startdate']), str(row['enddate'])])
        if rowstring in s: continue
        s.add(rowstring)
        new_data.append(row)
    return new_data


# detects "rolling average polls" that have overlapping dates and removes them. This cleans up the 
# data slightly for the time series
def remove_overlapping_timeseries(data):
    output = []
    for row in data:
        found_overlap = False
        for row1 in output:
            if row['pollster'] == row1['pollster'] and row['startdate'] <= row1['enddate'] and row1['startdate'] <= row['enddate']:
                found_overlap = True
        if not found_overlap:
            output.append(row)
    return output

# Clean up the polls, following Sam's rules
def clean_polls_sam_rules(polls, day):

    num_recent_polls_to_use = 3
    # -1. Make sure there's something to clean
    if not polls:
        return []

    # 0. Sort the polls by ending date
    polls.sort(key = lambda x: x['enddate'], reverse = True)

    # 1. Drop all polls ending after "today"
    polls = filter(lambda x: x['enddate'] < day, polls)

    # 2. Only use the latest poll from each organization
    pollsters = []
    def seen(pollster):
        if pollster in pollsters:
            return True
        else:
            pollsters.append(pollster)
            return False

    polls = [poll for poll in polls if not seen(poll['pollster'])]

    # If we don't need to eliminate any more polls, return
    if len(polls) < num_recent_polls_to_use:

        return polls

    # 3. Find third oldest mid date of a poll, and include any from this date or newer
    polls.sort(key=lambda x: x['middate'], reverse=True)
    third_oldest_date = polls[num_recent_polls_to_use - 1]['middate']

    # 4. Find N weeks ago, where N is a function of "today"
    if day < date(2018, 8, 1): # Before August 1
        n = timedelta(7 * 6, 0, 0) # 6 weeks
    elif day < date(2018, 9, 1):   # Month of August
        n = timedelta(7 * 4, 0, 0) # 4 weeks
    elif day < date(2018, 10, 1):  # September
        #n = datetime.timedelta(7 * 2, 0, 0) # 2 weeks
	    n = timedelta(28 - (day.day - 1) / 2, 0, 0) # Ease from 28 days to 14 over the course of the month
    else:                                   # October onwards
        n = timedelta(7 * 2, 0, 0) # now also 2 weeks
    n_weeks_ago = day - n

    # 5. Return all polls with a median date of (#3) or newer, or an ending date of (#4) or newer
    return list(filter(lambda x: x['middate'] >= third_oldest_date or x['enddate'] >= n_weeks_ago, polls))

