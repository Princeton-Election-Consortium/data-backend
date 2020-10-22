# redistricting moneyball

### Data Process as of 10/2020

#### process for map data
1. take all_results_10_10_2020.csv
2. manual conversion in excel to all_results_10_10_2020-sorted.csv 
3. manual conversion in excel to all_results_10_10_2020-sorted-updated.csv
4. conversion in `process_results.ipynb` to `processed_data_10_19.csv` AND `processed_data_10_19.json` (might need to install `conda` and build an env using `env.yml` for this)
5. data loaded in `index.html` `main.js`

#### TODO
- specify data format that `main.js` requires
- generate all future data to that spec
- clean `process_results.ipynb` up, make it process directly into `processed_data_10_19.csv`
- remove need for `processed_data_10_19.json`

#### process for summary data
1. copied bipartisan_prob_10_10_2020.csv to redistricting_summaries.csv manually

#### TODO: 
- if needed, make this a runnable process like map data