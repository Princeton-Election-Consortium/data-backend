import pandas as pd 
import geopandas as gpd
import csv
from pathlib import Path

from collections import OrderedDict

data_dir = Path.cwd() / "data" 
out_dir = Path.cwd() / "out-files"

# Util method to come between state formats 
# returnType must be either 'full' 'two_digit' or 'FIPS'
def get_state_code(input, returnType = 'FIPS'):
    if (returnType != 'full' and returnType != 'two_digit' and returnType != 'FIPS'):
        raise ValueError("returnType must be either 'full' 'two_digit' or 'FIPS'")

    code_hash = {
        'AL': {'full': 'Alabama', 'two_digit': 'AL', 'FIPS': 1},
        'AK': {'full': 'Alaska', 'two_digit': 'AK', 'FIPS': 2},
        'AZ': {'full': 'Arizona', 'two_digit': 'AZ', 'FIPS': 4},
        'AR': {'full': 'Arkansas', 'two_digit': 'AR', 'FIPS': 5},
        'CA': {'full': 'California', 'two_digit': 'CA', 'FIPS': 6},
        'CO': {'full': 'Colorado', 'two_digit': 'CO', 'FIPS': 8},
        'CT': {'full': 'Connecticut', 'two_digit': 'CT', 'FIPS': 9},
        'DE': {'full': 'Delaware', 'two_digit': 'DE', 'FIPS': 10},
        'DC': {'full': 'District of Columbia', 'two_digit': 'DC', 'FIPS': 11},
        'FL': {'full': 'Florida', 'two_digit': 'FL', 'FIPS': 12},
        'GA': {'full': 'Georgia', 'two_digit': 'GA', 'FIPS': 13},
        'HI': {'full': 'Hawaii', 'two_digit': 'HI', 'FIPS': 15},
        'ID': {'full': 'Idaho', 'two_digit': 'ID', 'FIPS': 16},
        'IL': {'full': 'Illinois', 'two_digit': 'IL', 'FIPS': 17},
        'IN': {'full': 'Indiana', 'two_digit': 'IN', 'FIPS': 18},
        'IA': {'full': 'Iowa', 'two_digit': 'IA', 'FIPS': 19},
        'KS': {'full': 'Kansas', 'two_digit': 'KS', 'FIPS': 20},
        'KY': {'full': 'Kentucky', 'two_digit': 'KY', 'FIPS': 21},
        'LA': {'full': 'Louisiana', 'two_digit': 'LA', 'FIPS': 22},
        'ME': {'full': 'Maine', 'two_digit': 'ME', 'FIPS': 23},
        'MD': {'full': 'Maryland', 'two_digit': 'MD', 'FIPS': 24},
        'MA': {'full': 'Massachusetts', 'two_digit': 'MA', 'FIPS': 25},
        'MI': {'full': 'Michigan', 'two_digit': 'MI', 'FIPS': 26},
        'MN': {'full': 'Minnesota', 'two_digit': 'MN', 'FIPS': 27},
        'MS': {'full': 'Mississippi', 'two_digit': 'MS', 'FIPS': 28},
        'MO': {'full': 'Missouri', 'two_digit': 'MO', 'FIPS': 29},
        'MT': {'full': 'Montana', 'two_digit': 'MT', 'FIPS': 30},
        'NE': {'full': 'Nebraska', 'two_digit': 'NE', 'FIPS': 31},
        'NV': {'full': 'Nevada', 'two_digit': 'NV', 'FIPS': 32},
        'NH': {'full': 'New Hampshire', 'two_digit': 'NH', 'FIPS': 33},
        'NJ': {'full': 'New Jersey', 'two_digit': 'NJ', 'FIPS': 34},
        'NM': {'full': 'New Mexico', 'two_digit': 'NM', 'FIPS': 35},
        'NY': {'full': 'New York', 'two_digit': 'NY', 'FIPS': 36},
        'NC': {'full': 'North Carolina', 'two_digit': 'NC', 'FIPS': 37},
        'ND': {'full': 'North Dakota', 'two_digit': 'ND', 'FIPS': 38},
        'OH': {'full': 'Ohio', 'two_digit': 'OH', 'FIPS': 39},
        'OK': {'full': 'Oklahoma', 'two_digit': 'OK', 'FIPS': 40},
        'OR': {'full': 'Oregon', 'two_digit': 'OR', 'FIPS': 41},
        'PA': {'full': 'Pennsylvania', 'two_digit': 'PA', 'FIPS': 42},
        'RI': {'full': 'Rhode Island', 'two_digit': 'RI', 'FIPS': 44},
        'SC': {'full': 'South Carolina', 'two_digit': 'SC', 'FIPS': 45},
        'SD': {'full': 'South Dakota', 'two_digit': 'SD', 'FIPS': 46},
        'TN': {'full': 'Tennessee', 'two_digit': 'TN', 'FIPS': 47},
        'TX': {'full': 'Texas', 'two_digit': 'TX', 'FIPS': 48},
        'UT': {'full': 'Utah', 'two_digit': 'UT', 'FIPS': 49},
        'VT': {'full': 'Vermont', 'two_digit': 'VT', 'FIPS': 50},
        'VA': {'full': 'Virginia', 'two_digit': 'VA', 'FIPS': 51},
        'WA': {'full': 'Washington', 'two_digit': 'WA', 'FIPS': 53},
        'WV': {'full': 'West Virginia', 'two_digit': 'WV', 'FIPS': 54},
        'WI': {'full': 'Wisconsin', 'two_digit': 'WI', 'FIPS': 55},
        'WY': {'full': 'Wyoming', 'two_digit': 'WY', 'FIPS': 56},
        'PR': {'full': 'Puerto Rico', 'two_digit': 'PR', 'FIPS': 72}
    }
    for row in code_hash:
        for value in code_hash[row]:
            if code_hash[row][value] == input:
                return code_hash[row][returnType]
    return None



# converts district code from the money ball csv to a GEOID
# ex. "CT-HD-59" --> '9059'
# ex. "MN-HD-13A" --> '2713A'
def getGEOID(district_str, leading_zero = False):
    state, chamber, dist_num = district_str.split('-')
    GEOID = str(get_state_code(state)) 
    if leading_zero and len(GEOID) < 2: 
        GEOID= '0' + GEOID
    while len(dist_num) <3: 
        dist_num = '0' + dist_num
    GEOID =  GEOID + dist_num
    return GEOID


# extracts the chamber type from the district code in the money ball csv
# ex. "CT-HD-59" --> 'HD'
def getChamber(district_str):
    state, chamber, dist_num = district_str.split('-')
    return chamber

# extracts the district name.  Used for the non-numerical Massachussets 
# districts in place of GEOID matching
def getName(district_str):
    state, chamber, dist_str = district_str.split('-')
    if len(dist_str) < 4 : return ''
    return dist_str

#################################################
#  PROCESS + ADD FIELDS TO MONEYBALL MODEL CSV  #
#################################################
def process_combine_data(outname):
    model_df = pd.read_csv(data_dir / 'moneyball-output_8_9_2020.csv')
    cand_df = pd.read_csv(data_dir / 'moneyball-latest-candidates.csv')
    ma_geoids = pd.read_csv(data_dir / 'MA_GEOIDS.csv')
    model_df = model_df[['state', 'district', 'favored', 'confidence', 'anti_gerrymandering_party', 'abs_power']]
    max_vp = model_df['abs_power'].max()
    model_df['abs_power'] = model_df.apply(lambda x: x['abs_power'] / max_vp * 100, axis=1)
    model_df = model_df.rename({'abs_power': 'redistricting_voter_power'}, axis='columns')
    cand_df = cand_df[['district', 'dem_nominee', 'rep_nominee', 'incumbent']]
    merged_df = pd.merge(model_df, cand_df, how='left', on='district')
    merged_df['geoid'] = merged_df.apply(lambda x: ma_geoids[ma_geoids.district == x.district].iloc[0]['geoid'] \
            if x.state == 'MA' \
            else getGEOID(x['district'], leading_zero = True), \
            axis=1)
    merged_df['chamber'] = merged_df.apply(lambda x: getChamber(x['district']), axis=1)
    merged_df.replace({'dem_nominee': {'FALSE': '', 'False': ''}, 'rep_nominee': {'FALSE': '', 'False': ''}}, inplace  = True)
    merged_df = merged_df[['state','district','favored','confidence','rep_nominee','dem_nominee','incumbent', \
               'redistricting_voter_power','anti_gerrymandering_party','geoid','chamber']]
    merged_df.to_csv(data_dir / outname, index=False, float_format='%.16f')


#################################################
#          CREATE MONEYBALL GEOJSON's           #
#################################################

# read in moneyball data
df = pd.read_csv(data_dir / 'processed_data_8_11.csv')

# segment to upper and lower chamber
upper_df = df[df['chamber'] == 'SD']
lower_df = df[df['chamber'] == 'HD']

# read in shapefiles 
upper_shp = gpd.read_file(data_dir / 'UPPER_cb_2019_us_sldu_500k/cb_2019_us_sldu_500k.shp')
lower_shp = gpd.read_file(data_dir / 'LOWER_cb_2019_us_sldl_500k/cb_2019_us_sldl_500k.shp')

# read in north carolinas updated district geometry
nc_upper_shp = gpd.read_file(data_dir / 'NC_State_Senate_2020/Senate Consensus Nonpartisan Map v3.shp')
nc_lower_shp = gpd.read_file(data_dir / 'NC_State_House_2020/HB 1020 H Red Comm CSBK-25.shp')
# normalize coordinate system of NC data for integration to census data
nc_upper_shp = nc_upper_shp.to_crs(upper_shp.crs)
nc_lower_shp = nc_lower_shp.to_crs(lower_shp.crs)

#### replace nc geometry into census shapefile ####

# get GEOID columns for merge
nc_lower_shp['GEOID'] = nc_lower_shp['DISTRICT'].apply(lambda x:\
                                            '37' + str(x).zfill(3))
nc_upper_shp['GEOID'] = nc_upper_shp['DISTRICT'].apply(lambda x:\
                                            '37' + str(x).zfill(3))

# merge
merged_upper_shp = pd.merge(upper_shp, nc_upper_shp, how='left', on='GEOID', suffixes=['', '_y'])
merged_lower_shp = pd.merge(lower_shp, nc_lower_shp, how='left', on='GEOID', suffixes=['', '_y'])

# merge in geometries to the proper column
merged_upper_shp['geometry'] = merged_upper_shp.apply(lambda x:\
                        x['geometry_y'] if x['STATEFP'] == '37'\
                                        else x['geometry'], \
                                        axis = 1)
merged_lower_shp['geometry'] = merged_lower_shp.apply(lambda x:\
                        x['geometry_y'] if x['STATEFP'] == '37'\
                                        else x['geometry'], \
                                        axis = 1)

upper_shp = merged_upper_shp.drop(columns='geometry_y')
lower_shp = merged_lower_shp.drop(columns='geometry_y')


# Pandas lambda helper function
# Locates fields from df_columns[] in df corresponding to the GEOID 
# of the given geopandas row and returns them for lambda insertion.
# If there is no GEOID match, returns the value from default_values[]
def pandas_lambda_geolocate(row, df, df_columns, default_values):
    vals = []
    geomatch = df[df['geoid'] == row['GEOID']]
    if len(geomatch.index) < 1:
        #print (f"No match found for GEOID: {row['GEOID']}")
        return pd.Series(default_values)
    elif len(geomatch.index) > 1:
        print(f"More than one match found for GEOID: {row['GEOID']}")
    geomatch = geomatch.iloc[0]
    
    for i in range(0, len(df_columns)):
        vals.append(geomatch[df_columns[i]])

    return pd.Series(vals)

# Concatenates the fields "confidence" and "favored" into a 'likely' string
def get_lean(row, df):
    geomatch = df[df['geoid'] == row['GEOID']]
    if len(geomatch.index) < 1:
        return 'no data'
    elif len(geomatch.index) > 1:
        print(f"More than one match found for GEOID: {row['GEOID']}")
    geomatch = geomatch.iloc[0]
    confidence = geomatch['confidence']
    favored = geomatch['favored']
    if confidence == 'Toss-Up': return confidence
    return confidence + " " + favored

# helper method parsing districts with characters
def toInt(foo):
    try:
        int(foo)
    except ValueError:
        return foo
    return int(foo)

# returns district from GEOID
def get_district(GEOID, chamber):
    GEOID_str = str(GEOID)
    end_state = 2 if len(GEOID_str) == 5 else 1
    two_letter = get_state_code(int(GEOID_str[0:end_state]), 'two_digit')
    district = two_letter + '-' + chamber + '-' + str(toInt(GEOID_str[end_state:]))
    return district

# returns full state name from GEOID
def get_full_state(GEOID):
    GEOID_str = str(GEOID)
    end_state = 2 if len(GEOID_str) == 5 else 1
    full = get_state_code(int(GEOID_str[0:end_state]), 'full')
    return full

# returns two letter state abbreviation from GEOID
def get_postal(GEOID):
    GEOID_str = str(GEOID)
    end_state = 2 if len(GEOID_str) == 5 else 1
    two_letter = get_state_code(int(GEOID_str[0:end_state]), 'two_digit')
    return two_letter


# add data columns from model to geojson 
df_columns = ['district', 'rep_nominee', 'dem_nominee', 'incumbent', 'anti_gerrymandering_party', 'redistricting_voter_power']
default_values = ['',       '',           '',           '',          '',                            0]

upper_shp[['DISTRICT', 'NOM_R', 'NOM_D', 'INCUMBENT','ANTI_GERRY_PARTY', 'VOTER_POWER']] = upper_shp.apply(
    lambda row: pandas_lambda_geolocate(row, upper_df, df_columns, default_values), axis = 1)
upper_shp['LEAN'] = upper_shp.apply(lambda row: get_lean(row, upper_df), axis = 1)

lower_shp[['DISTRICT', 'NOM_R', 'NOM_D', 'INCUMBENT','ANTI_GERRY_PARTY', 'VOTER_POWER']] = lower_shp.apply(
    lambda row: pandas_lambda_geolocate(row, lower_df, df_columns, default_values), axis = 1)
lower_shp['LEAN'] = lower_shp.apply(lambda row: get_lean(row, lower_df), axis = 1)

# add district fields to shapes not in the model
lower_shp['DISTRICT'] = lower_shp.apply(lambda row: get_district(row['GEOID'], 'HD') if row['DISTRICT'] == '' 
                        else row['DISTRICT'], axis=1)
upper_shp['DISTRICT'] = upper_shp.apply(lambda row: get_district(row['GEOID'], 'SD') if row['DISTRICT'] == '' 
                        else row['DISTRICT'], axis=1)

# eliminate unneeded columns and order 
upper_shp = upper_shp[['STATEFP', 'GEOID', 'DISTRICT', 'NOM_R', 'NOM_D', 'INCUMBENT','ANTI_GERRY_PARTY', 'LEAN', 'VOTER_POWER', 'geometry']]	
lower_shp = lower_shp[['STATEFP', 'GEOID', 'DISTRICT', 'NOM_R', 'NOM_D', 'INCUMBENT','ANTI_GERRY_PARTY', 'LEAN', 'VOTER_POWER', 'geometry']]

# add full state names and 2 letter state abbreviations to all shapes
upper_shp['FULL'] = upper_shp.apply(lambda row: get_full_state(row['GEOID']), axis=1)
upper_shp['POSTAL'] = upper_shp.apply(lambda row: get_postal(row['GEOID']), axis=1)
lower_shp['FULL'] = lower_shp.apply(lambda row: get_full_state(row['GEOID']), axis=1)
lower_shp['POSTAL'] = lower_shp.apply(lambda row: get_postal(row['GEOID']), axis=1)


# replace 'FALSE' with blank candidate fields  ('TBA' is the other option)
upper_shp['NOM_R'].replace({'FALSE': ''}, inplace =True)
upper_shp['NOM_D'].replace({'FALSE': ''}, inplace =True)
lower_shp['NOM_R'].replace({'FALSE': ''}, inplace =True)
lower_shp['NOM_D'].replace({'FALSE': ''}, inplace =True)

upper_nonzero_rows = len(upper_shp[upper_shp['VOTER_POWER'] != 0].index)
lower_nonzero_rows = len(lower_shp[lower_shp['VOTER_POWER'] != 0].index)

print(f"nonzero rows upper: {upper_nonzero_rows}  lower: {lower_nonzero_rows}")

# save to GeoJSON format
upper_shp.to_file(out_dir / "upper_state_moneyball.geojson", driver="GeoJSON")
lower_shp.to_file(out_dir / "lower_state_moneyball.geojson", driver="GeoJSON")