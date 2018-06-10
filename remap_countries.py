import json
import csv

def generate_unfilled_mapping_file(source_countries, target_countries, mapping_filepath):
    # Extract the un-matched source and target countries
    source_only = sorted(list(set(source_countries) - set(target_countries)))
    target_only = sorted(list(set(target_countries) - set(source_countries)))

    # Create and save the mapping file
    with open(mapping_filepath, "w") as f:
        w = csv.writer(f)
        
        header = ["From", "To", "Options"]
        w.writerow(header)

        nrows = max(len(source_only), len(target_only))
        for i in range(nrows):
            from_entry = source_only[i] if i < len(source_only) else ""
            to_entry = ""
            options_entry = target_only[i] if i < len(target_only) else ""

            w.writerow([from_entry, to_entry, options_entry])

def load_filled_mapping_file(mapping_filepath):
    with open(mapping_filepath, "r") as f:
        r = csv.reader(f)
        next(r) # Skip the header row

        to_rename = {}
        to_delete = []
        for row in r:
            from_entry = row[0]
            to_entry = row[1]
            # options_entry (= row[2]) is discarded

            if to_entry != "%":
                to_rename[from_entry] = to_entry
            else: 
                to_delete.append(from_entry)
    return to_rename, to_delete

####

def prepare_trade_data_manual_mapping(trade_filepath, target_countries_filepath, mapping_filepath):
    # Read in trade data file and extract list of countries
    with open(trade_filepath, "r") as f:
        r = csv.reader(f)
        next(r) # Skip the header row

        trade_countries = []
        for row in r:
            country = row[0]
            trade_countries.append(country)
    trade_countries = sorted(list(set(trade_countries)))

    # Read in the target_countries file and extract list of countries
    with open(target_countries_filepath, "r") as f:
        data = json.loads(f.read())
    target_countries = [country["name"] for country in data["countries"]]

    # Generate the unfilled mapping file
    generate_unfilled_mapping_file(trade_countries, target_countries, mapping_filepath)

def remap_trade_data(original_trade_filepath, mapping_filepath, mapped_trade_filepath):
    # Read in the original trade data
    with open(original_trade_filepath, "r") as f:
        r = csv.reader(f)
        header = next(r)
        data = []
        for row in r:
            data.append(row)

    # Read in the mapping
    to_rename, to_delete = load_filled_mapping_file(mapping_filepath)

    # Apply the mapping
    mapped_data = []
    for record in data: 
        country = record[0]
        # Delete
        if country in to_delete:
            print("Deleting: " + country)
            continue
        # Rename
        if country in to_rename.keys():
            print("Renaming: " + country + "  --->  " + to_rename[country])
            record[0] = to_rename[country]
        mapped_data.append(record)
    
    assert(len(data) - len(to_delete) == len(mapped_data))

    # Re-sort entries by alphabetical order
    mapped_data = sorted(mapped_data, key=lambda x: x[0])

    # Save the remapped trade data to file
    with open(mapped_trade_filepath, "w") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(mapped_data)

####

def prepare_geoJSON_manual_mapping(geoJSON_filepath, target_countries_filepath, mapping_filepath):
    # Read in geoJSON file and extract list of countries
    with open(geoJSON_filepath, "r") as f:
        data = json.loads(f.read())
        
    geoJSON_countries = [feature["properties"]["name"] for feature in data["features"]]
    geoJSON_countries = sorted(list(set(geoJSON_countries)))

    # Read in the target_countries file and extract list of countries
    with open(target_countries_filepath, "r") as f:
        data = json.loads(f.read())
    target_countries = [country["name"] for country in data["countries"]]

    # Generate the unfilled mapping file
    generate_unfilled_mapping_file(geoJSON_countries, target_countries, mapping_filepath)

def remap_geoJSON(original_geoJSON_filepath, mapping_filepath, mapped_geoJSON_filepath):
    # Read in the original geoJSON file
    with open(original_geoJSON_filepath, "r") as f:
        data = json.loads(f.read())
    
    # Read in the mapping
    to_rename, to_delete = load_filled_mapping_file(mapping_filepath)

    # Apply the mapping
    features = data["features"]
    mapped_features = []
    for feature in features: 
        country = feature["properties"]["name"]
        # Delete
        if country in to_delete:
            print("Deleting: " + country)
            continue
        # Rename
        if country in to_rename.keys():
            print("Renaming: " + country + "  --->  " + to_rename[country])
            feature["properties"]["name"] = to_rename[country]
        mapped_features.append(feature)
    
    assert(len(features) - len(to_delete) == len(mapped_features))

    # Re-sort entries by alphabetical order
    mapped_features = sorted(mapped_features, key=lambda x: x["properties"]["name"])
    
    data["features"] = mapped_features

    # Save the remapped geoJSON to file
    with open(mapped_geoJSON_filepath, "w") as f:
        f.write(json.dumps(data, indent=2))

if __name__ == "__main__":
    datadir = "/Users/adona/data/trade/"
    target_countries_filepath = datadir + "mappings/countries_standard.json"
    
    # trade_filepath = datadir + "raw/HS_2017_Import_2018_04_24_1028.csv"
    # mapping_filepath = datadir + "mappings/trade_mapping.csv"
    # mapped_trade_filepath = datadir + "clean/HS_2017_Import_2018_04_24_1028_mapped.csv"
    # # prepare_trade_data_manual_mapping(trade_filepath, target_countries_filepath, mapping_filepath)
    # remap_trade_data(trade_filepath, mapping_filepath, mapped_trade_filepath)    

    geoJSON_filepath = datadir + "geoJSON/centroids.geojson"
    mapping_filepath = datadir + "mappings/centroids_mapping.csv"
    mapped_geoJSON_filepath = datadir + "geoJSON/centroids_mapped.geojson"
    # prepare_geoJSON_manual_mapping(geoJSON_filepath, target_countries_filepath, mapping_filepath)
    remap_geoJSON(geoJSON_filepath, mapping_filepath, mapped_geoJSON_filepath)    

