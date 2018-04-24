import xlrd
import csv
import argparse
import textwrap
import re
from itertools import compress

verbose = False

def load_manual_country_mappings(fmap):
    log("Loading country name mapping.. ")
    # Load mapping from excel
    log("Opening the mapping file: " + fmap + "..")
    workbook = xlrd.open_workbook(fmap)
    sheet = workbook.sheets()[0]
    colA, colB, colmap = 0, 1, 2
    countriesA = sheet.col_values(colA)[1:]
    countriesA = [c for c in countriesA if len(c)>0]
    countriesB = sheet.col_values(colB)[1:]
    countriesB = [c for c in countriesB if len(c)>0]
    mapping = sheet.col_values(colmap)[1:]
    mapping = mapping[:min(len(countriesA), len(countriesB))+1]
    # Convert to Python representation
    log("Creating the mapping dictionary and the ignore lists..")
    mapBtoA = {}
    for i,A in enumerate(mapping):
        if len(A)>0:
            mapBtoA[countriesB[i]] = A
    ignoreA = sorted(list(set(countriesA) - set(mapping)))
    ignoreB = sorted(list(set(countriesB) -  set(mapBtoA.keys())))
    log("Mapping successfully created..")
    log("")

    return mapBtoA, ignoreA, ignoreB

def generate_clean_trade_dataset(ftrade, map_trade_to_geoJSON, ignore_trade, ftrade_clean):
    log("Generating the clean dataset.. ")
    
    # Load the data from CSV
    log("Loading the raw dataset from: " + ftrade + "..")
    with open(ftrade, "r") as f:
        r = csv.reader(f)
        data = [row for row in r]

    # Zero-fill missing entries, and convert to int
    log("Converting trade values to int..")
    for row in data[1:]:
        # Zero-fill missing entries
        row[1:] = ['0' if e == '' else e for e in row[1:]]
        # Convert trade values to int 
        row[1:] = map(lambda x: int(x), row[1:])

    # Insert Total Trade column
    log("Inserting total trade column..")
        # Find the columns that represent leaves in the trade taxonomy
    labels = data[0][1:]
    codes = list(map(lambda x: re.match("[0-9]*", x).group(0), labels))
    lleaf = max(map(len, codes))
    isleaf = list(map(lambda x, lleaf=lleaf: len(x) == lleaf, codes))
        # Calculate the total trade for each country (by only summing the leaves)
    data[0].insert(1, "Total Trade")
    for row in data[1:]:
        leaves = list(compress(row[1:], isleaf))
        row.insert(1, sum(leaves))
    
    # Filter out the countries to ignore
    data[1:] = sorted(data[1:], key=lambda x: x[1], reverse=True) # sort descending by Total Trade
    toignore = [[row[0], row[1], i] for i, row in enumerate(data) if row[0] in ignore_trade]
    print("Ignoring the following " + str(len(toignore)) + " territories...")
    print("Country, Total Trade, Rank")
    for row in toignore:
        print(row)
    data = [row for row in data if row[0] not in ignore_trade]

    # Map remaining country names to standard geoGSON names
    log("Mapping remaining countries to gold standard..")
    for row in data[1:]:
        if row[0] in map_trade_to_geoJSON.keys():
            row[0] = map_trade_to_geoJSON[row[0]]
    
    # Sum any duplicate rows (i.e. regions to be merged)
    log("Summing rows corresponding to the same country (i.e. merging territories)..")
    data[1:] = sorted(data[1:], key=lambda x: x[0]) # resort by name
    i = 2
    while i<len(data):
        if data[i][0] == data[i-1][0]:   # duplicate!
            data[i-1][1:] = [x+y for x,y in zip(data[i-1][1:], data[i][1:])]
            del data[i]
        else: 
            i += 1

    # Store to new CSV
    log("Storing clean dataset at: " + ftrade_clean + "..")
    log("")
    with open(ftrade_clean, "w") as f:
        w = csv.writer(f)
        w.writerows(data)

def log(text):
    if verbose:
        print(text)

if __name__ == "__main__":

    # Parse arguments from command-line
    description = """
        Script to clean a US trade dataset for visualization, 
        primarily by mapping the dataset countries to a gold standard list of countries.
        It takes the raw dataset (in CSV format), and a country names mapping file, 
        and outputs the cleaned dataset. 
        For more information see: https://github.com/adona/trade
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent(description)
    )

    parser.add_argument("ftrade", help = "the trade dataset file (CSV)")
    parser.add_argument("fmap", help = """file mapping country names from the trade dataset
        to gold standard names. Example map file here: https://goo.gl/khvBr9. 
        For more information see: https://github.com/adona/trade""")
    parser.add_argument("output_dir", help = "output directory for the cleaned dataset")
    parser.add_argument("-f", "--filename", help = """
        filename under which to store the cleaned data. 
        The default is to add _clean to the ftrade filename.""")

    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    verbose = args.verbose  # store it in global variable for use by the log function

    if not args.filename:
        args.filename = re.search(".*/([^/]*).csv$", args.ftrade).group(1)
        args.filename += "_clean.csv"

    map_trade_to_geoJSON, ignore_geoJSON, ignore_trade = load_manual_country_mappings(args.fmap)
    generate_clean_trade_dataset(args.ftrade, map_trade_to_geoJSON, ignore_trade, args.output_dir + args.filename)

    log("Dataset cleaning succesful. Exiting.")





