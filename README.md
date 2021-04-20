**Bhavcopy**

Pythonic version bhavcopy. Downloads the EOD data from the last downloaded date.
This script pulls the data from NSE site.

IMPORTANT:

Before running this script , create a file called log.txt and save it in the download directory
and write the date from which you want to download EOD data

for eg: if you need data from Nov 10, 2017
        write the date as 2017-11-10 (in yyyy-mm-dd format) 

From that file(log.txt) this script keeps track of the last downloaded date
and when you run this script again it will auto download the EOD, index & Futures data
from that date till today.

Note: NSE doesnt allow scripts to download data for more than 1 year 

**Update on 2021-04-20 : NSE India has changed its webpage and its hard to scrape data from it.**
**This change seems have happened from the start of 2021**




**EOD_charts.py**

This script lets you plot NSE stock prices(India) on the fly in your browser from Yahoo Finance using Dash-Plotly modules.

For other exchange stocks just input the correct extension ,that is available from Yahoo Finance.

No adjustment for the price is needed. This script makes use get_yahoo.py to get price data to plot the graphs.



**get_yahoo.py**

This script is a modified version from
http://blog.bradlucas.com/posts/2017-06-02-new-yahoo-finance-quote-download-url/

You can use this file to download stock prices 
