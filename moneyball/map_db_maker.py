import shapefile
from collections import OrderedDict
import pandas as pd 
import csv
import geopandas as gpd

# Util method to come between state formats 
# ******* update to include every input and output case *********
def get_state_code(input, FIPS=True, TwoDigit=False, Full=False):
    if (FIPS + TwoDigit + Full != 1):
        raise ValueError("Exactly one format argument must be True. Default = FIPS")

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

    if FIPS:
        return code_hash[input]['FIPS']
    
    return None


# Util method to quickly make changes to the hash dict in get_state_code
def make_dict():
    terms = OrderedDict({})
    with open("./FIPS.csv", 'r') as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            if i >0:
                print( f"\'{row[3]}\': " +  "{" + f"\'full\': \'{row[1]}\', 'two_digit': '{row[3]}\', 'FIPS': {row[0]}" + "},")
            i+=1
    return terms 


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


# processes the raw moneyball data to a pandas readable csv with added fields
# for now: GEOID and chamber type (Upper vs Lower)
def process_moneyball_data(inPath, outPath):
    df = pd.read_csv(inPath)

    lambdafunc = lambda x: pd.Series(
        [getGEOID(x['district']),
        getChamber(x['district'])]
    )
    df [['GEOID', 'chamber']] = df.apply(lambdafunc, axis = 1)

    df.to_csv(outPath, index=False, float_format='%.16f')

def shapefile_union(in_shapefile_path, in_df, out_path):
    r = shapefile.Reader(in_shapefile_path)

    w = shapefile.Writer(out_path)
    w.fields = r.fields[1:] # skip first deletion field

    w.field('VOTER_POWER', 'N', decimal=30)

    print(r.fields)
    print(w.fields)

    # adding existing Shape objects
    for shaperec in r.iterShapeRecords():
        # print(shaperec )
        # print(type(shaperec) )
        voterpower = 0
        dct = shaperec.record.as_dict()
        GEOID = dct['GEOID']
        geomatchs = in_df[in_df['GEOID'] == GEOID]
        if len(geomatchs.index) > 0:
            voterpower = geomatchs.iloc[0]['VOTER_POWER']

        w.record(*shaperec.record + [voterpower])
        w.shape(shaperec.shape)

    w.close()    

### UPPER = senate  LOWER = house
def join_data():
    # read in moneyball data
    df = pd.read_csv('./processed_data.csv')

    # segment to upper and lower chamber
    upper_df = df[df['chamber'] == 'SD']
    lower_df = df[df['chamber'] == 'HD']

    # build UPPER shapefile 
    shapefile_union('./raw/UPPER_cb_2019_us_sldu_500k/cb_2019_us_sldu_500k.shp', upper_df, './output/state_moneyball_upper')
    # build LOWER shapefile 
    shapefile_union('./raw/LOWER_cb_2019_us_sldl_500k/cb_2019_us_sldl_500k.shp', lower_df, './output/state_moneyball_lower')


# debugging method to read the output shape file before zipping and mapboxing
def test_result(path):
    r = shapefile.Reader(path)
    print(r.fields)

    for shaperec in r.iterShapeRecords():
        print(*shaperec.record)


def to_geoJSON(inPath, outPath):
    shp = gpd.read_file(inPath)
    shp.to_file(outPath, driver="GeoJSON")

def oldmain():

    r = shapefile.Reader('./raw/UPPER_cb_2019_us_sldu_500k/cb_2019_us_sldu_500k.shp')

    w = shapefile.Writer('graph/processed_data')
    w.fields = r.fields[1:] # skip first deletion field
    w.field('Voter_Power', 'N', decimal=30)

    print(r.fields)
    print(w.fields)

    # adding existing Shape objects
    for shaperec in r.iterShapeRecords():
        # print(shaperec )
        # print(type(shaperec) )
        dct = shaperec.record.as_dict()
        print(dct)

        w.record(*shaperec.record + [100])
        w.shape(shaperec.shape)

    w.close()


#join_data()
#test_result('./output/state_moneyball_upper.shp')
to_geoJSON('./output/state_moneyball_upper.shp', './output/state_moneyball_upper.geojson')
to_geoJSON('./output/state_moneyball_lower.shp', './output/state_moneyball_lower.geojson')



