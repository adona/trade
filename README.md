# trade
Download US trade data from the [http://tse.export.gov/](http://tse.export.gov/) website.

Usage:

python3 download\_trade\_data.py [-f filename] [-p product_list] product_class year flow datadir cookie

**NOTE:**

Before running this script, you will need to manually generate a valid cookie:

1. Begin capturing HTTP traffic using [Wireshark](https://www.wireshark.org/) or program of choice.
2. In an **incognito** window, load [http://tse.export.gov/](http://tse.export.gov/)
3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade
4. Extract the cookie from the captured HTTP request


Description:

download\_trade\_data downloads a year's worth of US trade data from the [http://tse.export.gov/](http://tse.export.gov/) website.

- product\_class specifies which standard trade products classification system to use: NAICS, HS, or SITC. See what the different classification systems look like [here](http://tse.export.gov/tse/TSEProductPicker.aspx?lblProductClassID=ProductOptions1_lblSelectedProductClass&hdnProductClassID=ProductOptions1_hdnSelectedProductClass&lblProductCodeID=ProductOptions1_lblSelectedProductCode&hdnProductCodeID=ProductOptions1_hdnSelectedProductCode&lblProductNameID=ProductOptions1_lblSelectedProductName&hdnProductNameID=ProductOptions1_hdnSelectedProductName&cellDigitLevel=ProductOptions1_DigitLevelsCell&ChartReport=False&ClassSystemValue=NAICS&ProductCode=.TOTAL&NTD=True).
- flow specifies which direction of trade to download: Import or Export.
- datadir specifies which directory to save the downloaded data in. The data will be saved in both JSON and CSV format in the directory <datadir>/<product_class>/
- cookie provides a valid cookie to use to download the data.

Options:

- -f filename
                 Specify under what filename to save the downloaded data. The default is <product\_class>\_<year>\_<flow>.json/csv.
- -p product\_list
                 Specify the location of the product\_list file. The default is <datadir>/<product\_class>/<product\_class>.txt

Example:

* python3 download\_trade\_data.py SITC 2017 Export ~/data/trade 2yiv2sjj2keob0x54tmhy315

* python3 download\_trade\_data.py -f ~/data/trade/SITC/SITC\_small -p ~/data/trade/SITC/SITC\_small.txt SITC 2017 Export ~/data/trade 2yiv2sjj2keob0x54tmhy315
