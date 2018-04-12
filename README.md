# trade

Analyze US trade data from the [http://tse.export.gov/](http://tse.export.gov/) website.

The website provides trade data: 
* between US and every other country
* by year
* by import / export
* for product categories according to 3 standard taxonomies: NAICS, HS, and SITC  (see details [here](http://tse.export.gov/tse/TSEProductPicker.aspx?lblProductClassID=ProductOptions1_lblSelectedProductClass&hdnProductClassID=ProductOptions1_hdnSelectedProductClass&lblProductCodeID=ProductOptions1_lblSelectedProductCode&hdnProductCodeID=ProductOptions1_hdnSelectedProductCode&lblProductNameID=ProductOptions1_lblSelectedProductName&hdnProductNameID=ProductOptions1_hdnSelectedProductName&cellDigitLevel=ProductOptions1_DigitLevelsCell&ChartReport=False&ClassSystemValue=NAICS&ProductCode=.TOTAL&NTD=True))

### Download the data

Use the *download\_trade\_data.py* script to bulk download one year of trade data, for all countries, for a list of product categories. 

#### Preliminary setup
Before running the script, you will need to manually generate a valid cookie:

1. Begin capturing HTTP traffic using [Wireshark](https://www.wireshark.org/) or program of choice.
2. In an **incognito** window, load [http://tse.export.gov/](http://tse.export.gov/)
3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade
4. Extract the cookie from the captured HTTP request

#### Usage:
python3 download\_trade\_data.py [-f filename] [-p product_list] product_class year flow datadir cookie

##### Required parameters:
- *product\_class* specifies which standard trade products classification system to use: NAICS, HS, or SITC (see details [here](http://tse.export.gov/tse/TSEProductPicker.aspx?lblProductClassID=ProductOptions1_lblSelectedProductClass&hdnProductClassID=ProductOptions1_hdnSelectedProductClass&lblProductCodeID=ProductOptions1_lblSelectedProductCode&hdnProductCodeID=ProductOptions1_hdnSelectedProductCode&lblProductNameID=ProductOptions1_lblSelectedProductName&hdnProductNameID=ProductOptions1_hdnSelectedProductName&cellDigitLevel=ProductOptions1_DigitLevelsCell&ChartReport=False&ClassSystemValue=NAICS&ProductCode=.TOTAL&NTD=True)).
- *flow* specifies the direction of trade: *Import* or *Export*.
- *datadir* specifies the destination directory for the downloaded data (e.g. the [Google Drive data/trade folder](https://drive.google.com/drive/folders/1iql0yrj4TrLKjKyHv9O17KRoQIhyuJP4?usp=sharing)). The data will be saved in both JSON and CSV formats.
- *cookie* a valid cookie manually generated using the instructions above.

##### Optional parameters:

- *-f filename*
                filename (without extension) under which to store the downloaded data. The default is <*product\_class*>\_\<*year*\>\_\<*flow*\> (e.g. *SITC_2017_Import.json/csv*)
- *-p product\_list*
				file specifying which product categories to download. By default, the script expects a file named \<*datadir*\>/*<product\_class>.txt*. 
				**NOTE:** The [Google Drive trade folder](https://drive.google.com/drive/folders/1iql0yrj4TrLKjKyHv9O17KRoQIhyuJP4?usp=sharing) contains complete *product_list* files for each taxonomy (e.g. [SITC.txt](https://drive.google.com/file/d/18-VxAKJzB_Eru1lRse84hLijlaDQVqFY/view?usp=sharing)) as well as a small sub-list for testing purposes ([SITC_small.txt](https://drive.google.com/file/d/15R5UqULzlm8gyV7EghzeXOVQLlneRxOQ/view?usp=sharing)). 

##### Example Uses:

* python3 download\_trade\_data.py -f ~/data/trade/SITC\_2017\_Export\_small -p ~/data/trade/SITC\_small.txt SITC 2017 Export ~/data/trade [cookie]

* python3 download\_trade\_data.py SITC 2017 Export ~/data/trade [cookie]

* python3 download\_trade\_data.py help

### [In progress] Visualize the data
