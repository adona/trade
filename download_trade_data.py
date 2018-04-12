import sys
import requests
from bs4 import BeautifulSoup
import json
import csv
import re 
from pprint import pprint

base_url = "http://tse.export.gov/"
f_choice_fresh = "choice_fresh.html"
cookie = "" # Set below, in code

def get_viewstate():
    # Extract the __VIEWSTATE and __VIEWSTATEGENERATOR
    with open(f_choice_fresh, "r") as html:
        soup = BeautifulSoup(html, 'html.parser')
        viewstate = soup.find(id = "__VIEWSTATE")["value"]
        generator = soup.find(id = "__VIEWSTATEGENERATOR")["value"]
    return viewstate, generator

def map_year(year):
    # Mapping years to internal representation on the http://tse.export.gov/ website.
    return year - 1348

def to_int(x):
    return int(x.replace(",", ""))

def get_product_list(fname):
    with open(fname, "r") as f:
        rows = f.readlines()
    prods = []
    for row in rows:
        prod = row.strip()
        prod = prod.split(" - ")
        prod = {"code": prod[0], "name": prod[1]}
        prods.append(prod)
    return prods

def download_product_data(pclass, prod, years, flow):
    # Send in the POSTback request — to update the cookie with our choices
    url = "tse/TSEOptions.aspx?ReportID=1&Referrer=TSEReports.aspx&DataSource=NTD"
    viewstate, generator = get_viewstate()

    headers = {"Cookie": "ASP.NET_SessionId="+cookie, 
            "Referer": base_url+url}
    form_data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": generator,
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
    requests.post(base_url+url, headers=headers, data=form_data)

    # Finally, request the MapDisplay page directly, 
    # and check that you got the right data!
    url = "tse/MapDisplay.aspx"
    headers = {"Cookie": "ASP.NET_SessionId="+cookie}
    r = requests.get(base_url+url, headers=headers)

    return r.text

def extract_product_data(page):
    # NOTE: This function assumes that it was called on a page corresponding to only
    # one year of data. If a page has multiple years, it will only extract the first year.

    data = []
    soup = BeautifulSoup(page, 'html.parser')
    rows = soup.find(id = "ScrollableTable1_tblScrollData").find_all("tr")
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
    return data

def get_all_data(pclass, product_list, year, flow):
    meta = {
        "pclass": pclass,
        "flow": flow, 
        "year": year,
        "product_list": product_list
    }

    # Load the product list
    prods = get_product_list(product_list)

    # Download and extract the data
    data = []
    print("Downloading " + str(len(prods)) + " data pages:")
    for prod in prods:
        print("Downloading: " + prod["code"] + " - " + prod["name"] + "...")
        page = download_product_data(pclass, prod, {"from": year, "to": year}, flow)
        prod_data = extract_product_data(page)
        data.append({
            "prod": prod,
            "values": prod_data
        })

    return {"meta": meta, "data": data}

def save_data_as_json(data, fname):
    print("Saving data as JSON at: " + fname)
    with open(fname, "w") as f:
        f.write(json.dumps(data, indent=2))

def get_all_countries(data):
    all_countries = set()
    for row in data["data"]:
        countries = set([entry["country"] for entry in row["values"]])
        all_countries = all_countries|countries
    return sorted(list(all_countries))

def reshape_data_for_csv(data):
    # Reshape data to match CSV format: each row is a country, each column is a product

    countries = get_all_countries(data)
    rdata = {}
    for country in countries:
        rdata[country] = {}
    for row in data["data"]:
        prod = row["prod"]["code"] + " - " + row["prod"]["name"]
        for value in row["values"]:
            rdata[value["country"]][prod] = value["value"]
    
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

        # fieldnames = ["code", "name"] + get_all_countries(data)
        # writer = csv.DictWriter(f, fieldnames=fieldnames)
        # writer.writeheader()
        # for row in data["data"]:
        #     writer.writerow(to_csv_row(row))

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

    if(len(sys.argv) == 1 or (len(sys.argv)==2 and sys.argv[1] == "help")):
        # Show the usage
        print()
        print("Analyze US trade data from the http://tse.export.gov/ website.")
        print("For more information see: https://github.com/adona/trade")
        print()
        print("Usage:")
        print("\tpython3 " + sys.argv[0] + " [-f filename] [-p product_list] product_class year flow datadir cookie")
        print()
        print("Required parameters:")
        print("\tproduct_class - specifies which standard trade products classification system to use: NAICS, HS, or SITC.")
        print("\tflow - specifies the direction of trade: Import or Export.")
        print("\tdatadir - specifies the destination directory for the downloaded data. The data will be saved in both JSON and CSV formats." )
        print("\tcookie - a valid cookie manually generated using the 'preliminary setup' instructions below.")
        print()
        print("Optional parameters:")
        print("\t-f filename - filename (without extension) under which to store the downloaded data. The default is <product_class>_<year>_<flow> (e.g. SITC_2017_Import.json/csv)")
        print("\t-p product_list - file specifying which product categories to download. By default, the script expects a file named <datadir>/<product_class>.txt.")
        print()
        print("Preliminary setup:")
        print("\t Before running the script, you will need to manually generate a valid cookie:")
        print("\t\t 1. Begin capturing HTTP traffic using Wireshark or program of choice.")
        print("\t\t 2. In an incognito window, load http://tse.export.gov/")
        print("\t\t 3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade.")
        print("\t\t 4. Extract the cookie from the captured HTTP request.")
        print()
        print("Example Uses:")
        print("\tpython3 " + sys.argv[0] + " -f ~/data/trade/SITC_2017_Export_small -p ~/data/trade/SITC_small.txt SITC 2017 Export ~/data/trade [cookie]")
        print("\tpython3 " + sys.argv[0] + " SITC 2017 Export ~/data/trade [cookie]")
        print("\tpython3 " + sys.argv[0] + " help")
        print()
        print()
    else: 
        try: 
            # Read parameters from command line
            params = sys.argv[1:]

            filename = ""
            product_list = ""
            
            if(params[0] == "-f"):
                filename = params[1]
                params = params[2:]
            
            if(params[0] == "-p"):
                product_list = params[1]
                params = params[2:]
            
            pclass = params[0]
            year = int(params[1])
            flow = params[2]
            datadir = params[3]
            cookie = params[4]

            if(filename == ""):
                filename = datadir + "/" + pclass + "_" + str(year) + "_" + flow
            if(product_list == ""):
                product_list = datadir + "/" + pclass + ".txt"
        

            # print("Product class: " + pclass)
            # print("Product list: " + product_list)
            # print("Year: " + str(year))
            # print("Flow: " + flow)
            # print("Datadir: " + datadir)
            # print("Filename: " + filename + ".json/csv")
            # print("Cookie: " + cookie)
            # print()

        except: 
            print("Error parsing your command-line parameters. Please run: " + sys.argv[0] + " help to see the usage.")
            print()
            sys.exit()

        # Download the data
        data = get_all_data(pclass, product_list, year, flow)

        # Save it both as JSON and CSV
        save_data_as_json(data, filename+".json")
        save_data_as_csv(data, filename+".csv")



