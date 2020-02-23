import requests

# helper that takes in a url and filename and downloads the content of that url to a file names
# outfilename
def download_file(url, outfilename):
    # read in the csv file with the data
    r = requests.get(url, stream=True)
    with open(outfilename, "wb") as fd: 
        for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

# Take an iterable and enumerate it, but use 1-indexing
# This makes MATLAB happy
def one_indexed_enumerate(d):
    for num, item in enumerate(d):
        yield (num + 1, item)

