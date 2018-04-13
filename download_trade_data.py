import sys
import requests
from bs4 import BeautifulSoup
import json
import csv
import re 
import argparse
import textwrap
from pprint import pprint
from datetime import datetime

BASE_URL = "http://tse.export.gov/"
F_CHOICE_FRESH = "choice_fresh.html" # TODO Explain
verbose = False

def download_all_data(products, year, flow, cookie):
    # Load the website state
    viewstate, generator = load_viewstate()
    state = {"cookie": cookie,
        "viewstate": viewstate, 
        "generator": generator}

    # Load the product list
    pclass, prods = load_product_list(products)

    # Download and extract the data
    data = []
    log("\nStarting data download..")
    print("Downloading " + str(len(prods)) + " data pages:")
    for prod in prods:
        page = download_product_data(pclass, prod, {"from": year, "to": year}, flow, state)
        prod_data = extract_product_data(page)
        data.append({
            "prod": prod,
            "values": prod_data
        })
    log("Data download and extraction completed.\n")

    # Add the meta-information to the data
    meta = {
        "pclass": pclass,
        "products": products,
        "year": year,
        "flow": flow, 
    }

    return {"meta": meta, "data": data}

def load_product_list(fname): 
    log("Loading the product list..")
    with open(fname, "r") as f:
        rows = f.readlines()
    
    pclass = rows[0].strip()
    prods = []
    for row in rows[1:]:
        prod = row.strip()
        prod = prod.split(" - ")
        prod = {"code": prod[0], "name": prod[1]}
        prods.append(prod)

    log("Product list loaded.")
    return pclass, prods

def download_product_data(pclass, prod, years, flow, state):
    print("Downloading: " + prod["code"] + " - " + prod["name"] + "...")

    # Send in the POSTback request — to update the cookie with our choices
    url = "tse/TSEOptions.aspx?ReportID=1&Referrer=TSEReports.aspx&DataSource=NTD"

    headers = {"Cookie": "ASP.NET_SessionId="+state["cookie"], 
            "Referer": BASE_URL+url}
    form_data = {
        "__VIEWSTATE": state["viewstate"],
        "__VIEWSTATEGENERATOR": state["generator"],
        "ProductOptions1$radioProductFlowType": flow,
        "ProductOptions1$radioDataFlowType": "TotExpGenImp",
        "ProductOptions1$hdnSelectedProductClass": pclass,
        "ProductOptions1$hdnSelectedProductCode": prod["code"],
        "ProductOptions1$hdnSelectedProductName": prod["code"]+"--"+prod["name"],
        "ProductOptions1$radioDigitLevel": "Level3",
        "TimePeriodOptions_TSEOnly$lstTSEOnlyAnnualTotalsFrom": map_year(years["from"]),
        "TimePeriodOptions_TSEOnly$lstTSEOnlyAnnualTotalsTo": map_year(years["to"]),
        "TimePeriodOptions_TSEOnly$hdnQuarterlyCurrYear": "2017",
        "TimePeriodOptions_TSEOnly$hdnQuarterlyCurrQuarter": "4",
        "TimePeriodOptions_TSEOnly$lstTSEOnlyQuarterlyYTD": "1",
        "TimePeriodOptions_TSEOnly$lstTSEOnlyAdditionalDataComputations": "Dollar Change",
        "TimePeriodOptions_TSEOnly$lstTSEOnlyAdditionalDataFrom": "665",
        "TimePeriodOptions_TSEOnly$lstTSEOnlyAdditionalDataTo": "669",
        "TimePeriodOptions_TSEOnly$hdnSelectedColsForTable": 
            str(years["to"]-years["from"])+"[-]"+str(years["to"])+"[-]"+str(years["to"]),
        "MapOptions1$lstMapInterval": str(years["to"]),
        "MapOptions1$lstDisplayStyle": "1",
        "MapOptions1$hdnColorsListASP": "#135292,#4075A9,#6D97BF,#9BB9D6,#DFEDF8",
        "MapOptions1$lstNumOfRanges": "5",
        "hdnCustomRangeMin1": "", 
        "hdnCustomRangeMax1": "", 
        "hdnCustomRangeMin2": "", 
        "hdnCustomRangeMax2": "", 
        "hdnCustomRangeMin3": "", 
        "hdnCustomRangeMax3": "", 
        "hdnCustomRangeMin4": "", 
        "hdnCustomRangeMax4": "", 
        "hdnCustomRangeMin5": "", 
        "hdnCustomRangeMax5": "", 
        "hdnCustomRangeMin6": "", 
        "hdnCustomRangeMax6": "", 
        "hdnCustomRangeMin7": "", 
        "hdnCustomRangeMax7": "", 
        "hdnCustomRangeMin8": "", 
        "hdnCustomRangeMax8": "", 
        "hdnCustomRangeMin9": "", 
        "hdnCustomRangeMax9": "", 
        "hdnCustomRangeMin10": "", 
        "hdnCustomRangeMax10": "", 
        "MapOptions1$hdnSubmitCustomRanges": "", 
        "MapOptions1$MapRanges": "1",
        "btnGo": "Go"
    }
    log("Posting form data..")
    requests.post(BASE_URL+url, headers=headers, data=form_data)

    # Finally, request the MapDisplay page directly, 
    # and check that you got the right data!
    url = "tse/MapDisplay.aspx"
    headers = {"Cookie": "ASP.NET_SessionId="+state["cookie"]}
    log("Requesting the MapDisplay.aspx page..")
    r = requests.get(BASE_URL+url, headers=headers)

    if("Detection Screen" in r.text):
        msg = ("The page was not downloaded correctly "
            "most likely because of a stale cookie. Please re-generate your cookie "
            "and try again!")
        raise RuntimeError(msg)

    log("Product data download completed.")
    return r.text

def extract_product_data(page):
    # NOTE: This function assumes that it was called on a page corresponding to only
    # one year of data. If a page has multiple years, it will only extract the first year.

    log("Extracting data from page..")
    data = []
    soup = BeautifulSoup(page, 'html.parser')
    log("Finding table rows..")
    rows = soup.find(id = "ScrollableTable1_tblScrollData").find_all("tr")

    log("Table rows found.")
    if len(rows)>0: 
        rows.pop(0); rows.pop(0)    # Remove the table header and the "World" row
        for row in rows:
            tds = row.find_all("td")
            country = tds[1].text
            value = to_int(tds[2].text)
            data.append({
                "country": country, 
                "value": value
            })
    log("Data extracted successfully.\n")
    return data

def save_data_as_json(data, fname):
    print("Saving data as JSON at: " + fname)
    with open(fname, "w") as f:
        f.write(json.dumps(data, indent=2))
    log("JSON file saved.\n")

def reshape_data_for_csv(data):
    # Reshape data to match CSV format: each row is a country, each column is a product

    log("Reshaping data to match CSV format..")
    countries = extract_all_countries(data)
    rdata = {}
    for country in countries:
        rdata[country] = {}
    for row in data["data"]:
        prod = row["prod"]["code"] + " - " + row["prod"]["name"]
        for value in row["values"]:
            rdata[value["country"]][prod] = value["value"]
    log("Data reshape complete.")

    return rdata, countries

def save_data_as_csv(data, fname):
    print("Saving data as CSV at: " + fname)
    with open(fname, "w", newline="") as f:
        fieldnames = ["country"] + [row["prod"]["code"] + " - " + row["prod"]["name"] for row in data["data"]]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()        
        rdata, countries = reshape_data_for_csv(data)
        for country in countries: 
            csv_row = rdata[country]
            csv_row["country"] = country
            writer.writerow(csv_row)
    log("CSV file saved.\n")


# Helper functions

def log(text):
    if verbose:
        print(text)

def load_viewstate():
    # Extract the __VIEWSTATE and __VIEWSTATEGENERATOR
    log("Loading __VIEWSTATE and __VIEWSTATEGENERATOR..")
    with open(F_CHOICE_FRESH, "r") as html:
        soup = BeautifulSoup(html, 'html.parser')
        viewstate = soup.find(id = "__VIEWSTATE")["value"]
        generator = soup.find(id = "__VIEWSTATEGENERATOR")["value"]
    log("Viewstate loaded.")
    return viewstate, generator

def map_year(year):
    # Mapping years to internal representation on the http://tse.export.gov/ website.
    return year - 1348

def to_int(x):
    return int(x.replace(",", ""))

def extract_all_countries(data):
    log("Extracting all countries..")
    all_countries = set()
    for row in data["data"]:
        countries = set([entry["country"] for entry in row["values"]])
        all_countries = all_countries|countries
    log("Countries extracted successfully.")
    return sorted(list(all_countries))

# Test functions

def test_dowload(pclass, prod, years, flow, rows):
    # Download the page
    title = str(years["to"]) + " " + flow + "s of " + pclass + " " + prod["code"]+"--"+prod["name"]
    print("Downloading: " + title + "...")
    page = download_product_data(pclass, prod, years, flow)
    
    # Sanity check the reponse
    assert(re.search(title, page))
    for row in rows:
        print("Testing: " + row["country"] + " - " + row["value"]  + "...")
        assert(re.search(row["country"], page))
        assert(re.search(row["value"], page))
    assert(re.search("Made up country", page) is None)
    print("Success!")

    return page

def test_extract(page, rows):
    # Extract the data
    data = extract_product_data(page)

    # Sanity check the result
    print("Testing extraction...")
    for row in rows:
        # Find the country
        sel = [d for d in data if d["country"] == row["country"]]
        assert(len(sel) == 1)
        # Check the value
        assert(sel[0]["value"] == to_int(row["value"]))
    print("Success!")

    return data
 
def test():
    # # TEST #1: Download
    pclass = "SITC"
    prod = {"code": "634", "name": "Veneers, Plywood and Particle Board"}
    years = {"from": 2013, "to": 2015}
    flow = "Import"
    rows = [{"country": "Canada", "value": "1,971,176,182"},
            {"country": "Romania", "value": "6,306,401"},
            {"country": "Pakistan", "value": "3,275"}]
    test_dowload(pclass, prod, years, flow, rows)

    # TEST #2: Download and extract
    pclass = "SITC"
    prod = {"code": "684", "name": "Aluminum"}
    years = {"from": 2017, "to": 2017}
    flow = "Export"
    rows = [{"country": "Mexico", "value": "3,044,002,443"},
            {"country": "Liechtenstein", "value": "2,505"},
            {"country": "Zambia", "value": "0"}]
    page = test_dowload(pclass, prod, years, flow, rows)
    test_extract(page, rows)

if __name__ == "__main__":
    # Parse arguments from command-line
    description = """
        Analyze US trade data from the http://tse.export.gov/ website.
        For more information see: https://github.com/adona/trade"""

    epilog = """
        Generating a valid cookie
        -------------------------
        Before running the script, you will need to manually generate a valid cookie:
            1. Begin capturing HTTP traffic using Wireshark or program of choice.
            2. In an incognito window, load http://tse.export.gov/
            3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade.
            4. Extract the cookie from the captured HTTP request. 
               The cookie should look something like: 'ASP.NET_SessionId=20pjd3a31dqjh05rytoziouv'.
               You will only need the part after the =sign: 20pjd3a31dqjh05rytoziouv"""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = textwrap.dedent(description),
        epilog = textwrap.dedent(epilog)
    )
    parser.add_argument("products", help = """
        file specifying: 1) a trade products classification system to use (NAICS, HS, or SITC),and 
        2) a list of product classes under that system for which to download data.
        Example files with complete lists of product classes for each classification system 
        can be found here: https://goo.gl/c9m5H9
    """)
    parser.add_argument("year", help = "year to download data for (between 2002-2017)", type = int)
    parser.add_argument("flow", help = "direction of trade: Import or Export", choices=["Import", "Export"])
    parser.add_argument("datadir", help = "destination directory for downloaded data")
    parser.add_argument("-f", "--filename", help = """
        filename (without extension) under which to store the downloaded data. 
        The default is <product_class>_<year>_<flow>_<timestamp> 
        (e.g. SITC_2017_Import_2018_04_13_0000.json/csv)
    """)
    parser.add_argument("cookie", help = "a manually-generated valid cookie (see instructions below)")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()
    verbose = args.verbose  # store it in global variable for use by the log function

    # Download the data
    data = download_all_data(args.products, args.year, args.flow, args.cookie)

    # Save it both as JSON and CSV
    if not args.filename:
        args.filename = args.datadir + "/" + data["meta"]["pclass"] + "_" + str(args.year) + "_" + args.flow + "_"
        args.filename += datetime.utcnow().strftime("%Y_%m_%d_%H%M")

    save_data_as_json(data, args.filename + ".json")
    save_data_as_csv(data, args.filename + ".csv")

    log("Data successfully downloaded, extracted, and stored. Goodbye and thanks for all the fish!")



