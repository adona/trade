# trade
Download US trade data from the http://tse.export.gov/ website.

Usage:
        python3 download_trade_data.py [-f filename] [-p product_list] product_class year flow datadir cookie

Description:
        download_trade_data downloads a year's worth of US trade data from the http://tse.export.gov/ website.
        Product_class specifies which standard trade products classification system to use: NAICS, HS, or SITC.
        Flow specifies which direction of trade to download: Import or Export.
        Datadir specifies which directory to save the downloaded data in. The data will be saved in both JSON and CSV format in the directory <datadir>/<product_class>/
        Cookie provides a valid cookie to use to download the data.

        NOTE: To generate a valid cookie:
                 1. Begin capturing HTTP traffic using Wireshark or program of choice.
                 2. In an incognito window, load http://tse.export.gov/
                 3. Navigate to: National Trade Data -> Global Patterns of U.S. Merchandise Trade
                 4. Extract the cookie from the captured HTTP request

Options:
        -f filename
                 Specify under what filename to save the downloaded data. The default is <product_class>_<year>_<flow>.json/csv.
        -p product_list
                 Specify the location of the product_list file. The default is <datadir>/<product_class>/<product_class>.txt

Example:
        python3 download_trade_data.py SITC 2017 Export ~/data/trade 2yiv2sjj2keob0x54tmhy315
        python3 download_trade_data.py -f ~/data/trade/SITC/SITC_small -p ~/data/trade/SITC/SITC_small.txt SITC 2017 Export ~/data/trade 2yiv2sjj2keob0x54tmhy315
