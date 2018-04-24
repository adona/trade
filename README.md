# trade

Analyze US trade data from the [http://tse.export.gov/](http://tse.export.gov/) website.

The website provides trade data: 
* between US and every other country
* by year
* by import / export
* for product categories according to 3 standard taxonomies: NAICS, HS, and SITC  (see details [here](http://tse.export.gov/tse/TSEProductPicker.aspx?lblProductClassID=ProductOptions1_lblSelectedProductClass&hdnProductClassID=ProductOptions1_hdnSelectedProductClass&lblProductCodeID=ProductOptions1_lblSelectedProductCode&hdnProductCodeID=ProductOptions1_hdnSelectedProductCode&lblProductNameID=ProductOptions1_lblSelectedProductName&hdnProductNameID=ProductOptions1_hdnSelectedProductName&cellDigitLevel=ProductOptions1_DigitLevelsCell&ChartReport=False&ClassSystemValue=NAICS&ProductCode=.TOTAL&NTD=True))

### 1. Download the data

Use the *download\_trade\_data.py* script to bulk download one year of trade data, for all countries, for a list of product categories. 

#### Preliminary setup
To install all required pacakages run: 
pip3 install -r requirements.txt

Before running the script you will also need to manually generate a valid cookie:

1. Begin capturing HTTP traffic using [Wireshark](https://www.wireshark.org/) or program of choice.
2. In an **incognito** window, load [http://tse.export.gov/](http://tse.export.gov/)
3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade
4. Extract the cookie from the captured HTTP request.
(NOTE: The cookie should look something like: 'ASP.NET_SessionId=20pjd3a31dqjh05rytoziouv'.
You will only need the part after the =sign, in this example: 20pjd3a31dqjh05rytoziouv)


#### Usage:
python3 download_trade_data.py [-h] [-f FILENAME] [-v]                              products year {Import,Export} datadir cookie
##### Required arguments:
* **products** - file specifying: 1) a trade products classification system to use (NAICS, HS, or SITC - see details [here](http://tse.export.gov/tse/TSEProductPicker.aspx?lblProductClassID=ProductOptions1_lblSelectedProductClass&hdnProductClassID=ProductOptions1_hdnSelectedProductClass&lblProductCodeID=ProductOptions1_lblSelectedProductCode&hdnProductCodeID=ProductOptions1_hdnSelectedProductCode&lblProductNameID=ProductOptions1_lblSelectedProductName&hdnProductNameID=ProductOptions1_hdnSelectedProductName&cellDigitLevel=ProductOptions1_DigitLevelsCell&ChartReport=False&ClassSystemValue=NAICS&ProductCode=.TOTAL&NTD=True)), and 2) a list of product classes under that system for which to download data. Example files with complete lists of product classes for each classification system can be found here: https://goo.gl/c9m5H9
* **year** - year to download data for (between 2002-2017)
* **{Import,Export}** - direction of trade: Import or Export
* **datadir** - destination directory for downloaded data
* **cookie** - a manually-generated valid cookie (see instructions above)



##### Optional parameters:
* **-h, --help** - show this help message and exit
* **-f FILENAME, --filename FILENAME** - filename (without extension) under which to store the downloaded data. The default is <product\_class>\_<year>\_<flow>\_<timestamp> (e.g. SITC_2017_Import_2018_04_13_0000.json/csv)
* **-v, --verbose**

##### Example Uses:

* python3 download_trade_data.py ~/data/trade/config/HS.txt 2017 Import ~/data/trade/raw [cookie]

### 2. Clean the data

The main task in cleaning the data for visualization is to standardize the list of countries in the dataset to a gold standard list of countries, typically from a geoJSON (currently using [this one](https://drive.google.com/open?id=1bcp681Trrs_uIJjm4W1KjTW-Ogbuejp9)). 

To do this you will have to create a spreadshseet encoding the country names mapping (or use the preexisting one [here](https://drive.google.com/open?id=1tZdoOvJNV8mdfJr0Ar-4wrAkvBTPf5jN)), and then run the *clean_trade_dataset.py* script.

#### Usage:
python3 clean_trade_dataset.py [-h] [-f FILENAME] [-v] ftrade fmap output_dir

##### Required arguments:
* **ftrade** - the trade dataset file (in CSV format)
* **fmap** - file mapping country names from the trade dataset to gold standard names. Example map file here: https://goo.gl/khvBr9.
* **output_dir** - output directory for the cleaned dataset


##### Optional parameters:
* **-h, --help** - show this help message and exit
* **-f FILENAME, --filename FILENAME** - filename under which to store the cleaned data. The default is to add *_clean* to the ftrade filename.
* **-v, --verbose**

##### Example Uses:

* python3 clean_trade_dataset.py ~/data/trade/raw/HS_2017_Import_2018_04_24_1028.csv ~/data/trade/countries/map_trade_geoJSON.xlsx ~/data/trade/clean/

#### Using a custom country names mapping:
One reason you might want to use a different country names mapping from the one [provided](https://goo.gl/khvBr9) is to use a different geoJSON as the basis for future visualization.

The easiest way to do that is to:
1. Use the *generate_country_list_diffs.py* script to generate a skelleton spreadhseet for the country names mapping.
The spreadsheet will have three columns: (A) the unampped geoJSON countries, (B) the unmapped trade dataset countries, and \(C\) an empty *mapping* column. (see exampe [here](https://drive.google.com/open?id=1yxCdQSfe3rgjM7EErk82V3yXl19ISfEZ))
NOTE: Run python3 generate_country_list_diffs.py -h to see the script's Usage.

2. *Manually* complete the mapping column above, providing for each country name in column (B) (the trade dataset) a mapping from column (A) (the geoJSON). 
NOTE: You can leave a mapping entry free to remove that country from the cleaned trade dataset. You can also map multiple trade dataset countries to the same geoJSON name to merge those entries (i.e. sum their trade values) in the cleaned dataset. In [this example](https://drive.google.com/file/d/1tZdoOvJNV8mdfJr0Ar-4wrAkvBTPf5jN/view) we have merged *West Bank* and *Gaza Strip* into *Palestine*, as well as folded the trade with *Hong Kong* into the *China* counts.