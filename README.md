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