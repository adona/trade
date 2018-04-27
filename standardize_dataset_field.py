import json
import csv 

def generate_diff_file(valuesA, valuesB, diff_file):
    # valuesA = gold standard/ground truth
    # valuesB = values to standardize

    # Compute the differences
    inAnotB = sorted(list(set(valuesA) - set(valuesB)))
    inBnotA = sorted(list(set(valuesB) - set(valuesA)))
    assert(len(valuesA) - len(inAnotB) == len(valuesB) - len(inBnotA))

    # Pad the shorter list with ""s
    nrows = max(len(inAnotB), len(inBnotA))
    if (len(inAnotB) < nrows):
        inAnotB += [""] * (nrows - len(inAnotB))
    elif (len(inBnotA) < nrows):
        inBnotA += [""] * (nrows - len(inBnotA))

    # Prepare the CSV data structure
    header = ["Ground Truth", "To Map", "Map To", "Notes"]
    CSV_data = []
    for i in range(nrows):
        CSV_data.append([inAnotB[i], inBnotA[i], "", ""])

    # Save to file
    with open(diff_file, "w") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(CSV_data)

def load_mapping(mapping_file):
    with open(mapping_file, "r") as f:
        r = csv.reader(f)
        data = [row for row in r]
        data = data[1:] # Skip the header (["Ground Truth", "To Map", "Map To", "Notes"])
                        
    
    to_map = [row[1] for row in data if row[1] != ""]
    n_to_map = len(to_map)
    map_to = [row[2] for row in data[:n_to_map]]

    to_rename = {}
    to_delete = []
    for i in range(n_to_map):
        if map_to[i] == "":
            to_delete.append(to_map[i])
        else: 
            to_rename[to_map[i]] = map_to[i]
    assert(len(to_rename) + len(to_delete) == len(to_map))
    
    return to_rename, to_delete

def standardize_field(data, get_field, set_field, to_rename, to_delete):
    
    # Delete
    ndata_begin = len(data)
    for i in range(len(data)-1, -1, -1):
        if get_field(data[i]) in to_delete:
            del data[i]
    assert(len(data) == ndata_begin - len(to_delete))

    # Rename
    ndata_begin = len(data)
    for row in data:
        if get_field(row) in to_rename.keys():
            set_field(row, to_rename[get_field(row)])
    assert(len(data) == ndata_begin)
        
    return data

####

def load_standard_countries(filename):
    with open(filename, "r") as f:
        data = json.loads(f.read())
    data = data["countries"]
    countries = [row["country"] for row in data]
    countries = sorted(countries)
    assert(len(countries) == 197)
    return countries

def load_countries_from_geoJSON(filename):
    with open(filename, "r") as f:
        data = json.loads(f.read())
    data = data["features"]
    countries = [row["properties"]["name"] for row in data]
    countries = sorted(list(set(countries)))
    return countries

def get_country_geoJSON(row):
    return row["properties"]["name"]

def set_country_geoJSON(row, country):
    row["properties"]["name"] = country

def generate_diff_geoJSON(f_countries_standard, f_geoJSON_to_clean, f_diff):
    standard = load_standard_countries(f_countries_standard)
    toclean = load_countries_from_geoJSON(f_geoJSON_to_clean)
    generate_diff_file(standard, toclean, f_diff)

def standardize_geoJSON(f_geoJSON_to_clean, f_mapping, f_cleaned_geoJSON):
    with open(f_geoJSON_to_clean, "r") as f:
        data = json.loads(f.read())

    to_rename, to_delete = load_mapping(f_mapping)
    data["features"] = standardize_field(data["features"], 
        get_country_geoJSON, set_country_geoJSON, 
        to_rename, to_delete)
    data["features"] = sorted(data["features"], key=get_country_geoJSON)

    with open(f_cleaned_geoJSON, "w") as f:
        f.write(json.dumps(data, indent=2))

def load_countries_trade(filename):
    with open(filename, "r") as f:
        r = csv.reader(f)
        data = [row for row in r]
    countries = [row[0] for row in data[1:]]
    countries = sorted(list(set(countries)))
    return countries

def get_country_trade(row):
    return row[0]

def set_country_trade(row, country):
    row[0] = country

def generate_diff_trade(f_countries_standard, f_trade, f_diff):
    standard = load_standard_countries(f_countries_standard)
    toclean = load_countries_trade(f_trade)
    generate_diff_file(standard, toclean, f_diff)

def standardize_trade(f_trade, f_mapping, f_trade_clean):
    with open(f_trade, "r") as f:
        r = csv.reader(f)
        data = [row for row in r]

    to_rename, to_delete = load_mapping(f_mapping)
    data[1:] = standardize_field(data[1:], 
        get_country_trade, set_country_trade, 
        to_rename, to_delete)
    data[1:] = sorted(data[1:], key=get_country_trade)

    with open(f_trade_clean, "w") as f:
        r = csv.writer(f)
        r.writerows(data)


if __name__ == "__main__":
    datadir = "/Users/adona/data/trade/"
    f_countries_standard = datadir + "geoJSON/countries_standard.json"

    # Example #1: Cleaning a geoJSON file:
    f_geoJSON_to_clean = datadir + "geoJSON/countries.geojson"
    f_diff = datadir + "geoJSON/diffs/diff_countries_geoJSON.csv"
    f_mapping = datadir + "geoJSON/diffs/mapping_countries_geoJSON.csv"
    f_cleaned_geoJSON = datadir + "geoJSON/countries_cleaned.geojson"

    # NOTE: There is a manual step between the two stages below, will need to split
    # into different scripts. (currently just manually commenting in/out which one 
    # I want to run during testing)
    generate_diff_geoJSON(f_countries_standard, f_geoJSON_to_clean, f_diff)
    # standardize_geoJSON(f_geoJSON_to_clean, f_mapping, f_cleaned_geoJSON)

    # Example #2: Cleaning the trade dataset:
    # f_trade = datadir + "raw/HS_2017_Import_2018_04_24_1028.csv"
    # f_diff = datadir + "geoJSON/diffs/diff_trade.csv"
    # f_mapping = datadir + "geoJSON/diffs/mapping_trade.csv"
    # f_trade_clean = datadir + "clean/HS_2017_Import_2018_04_24_1028_clean.csv"

    # generate_diff_trade(f_countries_standard, f_trade, f_diff)
    # standardize_trade(f_trade, f_mapping, f_trade_clean)