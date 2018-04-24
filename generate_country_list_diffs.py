import csv
import json
import xlwt
import argparse
import textwrap
import datetime

verbose = False

def extract_trade_countries(ftrade, fcountries_trade):
    log("Extracting countries from the trade data.. ")
    # Load the data from CSV
    log("Loading the trade data from: " + ftrade + "..")
    with open(ftrade, "r") as f:
        r = csv.reader(f)
        data = [row for row in r]
    #Extract the countries
    log("Extracting the countries..")
    countries = [row[0] for row in data[1:]]
    countries = sorted(countries)
    # Save to txt
    log("Saving the countries to: " + fcountries_trade + "..")
    log("")
    with open(fcountries_trade, "w") as f:
        for country in countries:
            f.write(country + "\n")

def extract_geoJSON_countries(fgeoJSON, fcountries_geoJSON):
    log("Extracting countries from the geoJSON file.. ")
    # Load the data from geoJSON
    log("Loading geoJSON data from: " + fgeoJSON + "..")
    with open(fgeoJSON, "r") as f:
        data = json.loads(f.read())
    # Extract the countries
    log("Extracting the countries..")
    countries = [row["properties"]["name"] for row in data["features"]]
    countries = sorted(countries)
    # Save to txt
    log("Saving the countries to: " + fcountries_geoJSON + "..")
    log("")
    with open(fcountries_geoJSON, "w") as f:
        for country in countries:
            f.write(country + "\n")

def generate_country_list_diffs(fcountriesA, fcountriesB, fdiff, labels = ["A", "B"]):
    log("Generating country list diffs.. ")
    # Load list A
    with open(fcountriesA, "r") as f:
        countriesA = f.readlines()
        countriesA = [country.strip() for country in countriesA]
    # Load list B
    with open(fcountriesB, "r") as f:
        countriesB = f.readlines()
        countriesB = [country.strip() for country in countriesB]

    # Compare
    log("Generating countries in " + labels[0] + " and not in " + labels[1] + "..")
    inAnotB = sorted(list(set(countriesA) - set(countriesB)))
    log("Generating countries in " + labels[1] + " and not in " + labels[0] + "..")
    inBnotA = sorted(list(set(countriesB) - set(countriesA)))
    
    # Store diffs to excel
    log("Generating an Excel workbook with the diffs..")
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet1')
    colA, colB, colmap, colnotes = 0, 1, 2, 3
    sheet.write(0, colA, label = labels[0])
    sheet.write(0, colB, label = labels[1])
    for i, country in enumerate(inAnotB):
        sheet.write(i+1, colA, label=country)
    for i, country in enumerate(inBnotA):
        sheet.write(i+1, colB, label=country)
    sheet.write(0, colmap, label = "Mapping")
    sheet.write(0, colnotes, label = "Notes")
    log("Saving the workbook at: " + fdiff + "..")
    log("")
    workbook.save(fdiff)

def log(text):
    if verbose:
        print(text)

if __name__ == "__main__":

    # Parse arguments from command-line
    description = """
        Script to prepare a US trade dataset (https://github.com/adona/trade) for cleaning
        and visualization. It generates a diff between the list of countries in the trade dataset
        and the gold standard countries in a given geoJSON file.
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent(description)
    )

    parser.add_argument("ftrade", help = "the trade dataset file (CSV)")
    parser.add_argument("fgeoJSON", help = "the gold standard geoJSON file. Example geoJSON file here: https://goo.gl/6kvjSu")
    parser.add_argument("output_dir", help = "the output directory for the country lists and the diff file")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    verbose = args.verbose  # store it in global variable for use by the log function

    fcountries_trade = args.output_dir + "trade_countries.txt"
    fcountries_geoJSON = args.output_dir + "geoJSON_countries.txt"
    fdiff = args.output_dir + "diff_trade_geoJSON.xlsx"

    extract_trade_countries(args.ftrade, fcountries_trade)
    extract_geoJSON_countries(args.fgeoJSON, fcountries_geoJSON)    
    generate_country_list_diffs(fcountries_geoJSON, fcountries_trade, fdiff, ["GeoJSON", "Trade"])

    log("Country list diffs generated successfully. Exiting.")