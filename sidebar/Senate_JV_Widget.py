
import csv
import os
from decimal import *
from state_code_util import *


def get_candidates(path):
    candidates = {}
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates[row['code']] = {
                'dem' : row['dem'],
                'rep' : row['rep']
            }
    return candidates

# *** note *** relies on Senate_jerseyvotes.m to be maximal voting power 
# sorted in order for table to be like-so
def get_jerseyvotes(path):
    votes = {}

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            votes[row[1]] = {
                'margin' : round(float(row[2]), 1),
                'jersey_votes' : round(float(row[3]), 1),
            }
    return votes


def main():
    # realpath arg had been __file__ serverside
    dir_path = os.path.dirname(os.path.realpath(''))
    
    path = os.path.join(dir_path, './scraping/outputs/2020.Senate.priors.csv')
    names = get_candidates(path)
    #print(names)

    path = os.path.join(dir_path, './matlab/outputs/Senate_jerseyvotes.csv')
    votes = get_jerseyvotes(path)
    #print(votes)

if __name__ == "__main__":
    main()

