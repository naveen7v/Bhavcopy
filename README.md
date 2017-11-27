# Bhavcopy
Pythonic version bhavcopy. Downloads the EOD data from the last downloaded date.
This script pulls the data from NSE site.

IMPORTANT:

Before running this script , create a file called log.txt and save it in the download directory
and write the date from which you want to download EOD data

for eg: if you need data from Nov 10, 2017
        write the date as 2017-11-10 (in yyyy-mm-dd format) 

From that file(log.txt) this script keeps track of the last downloaded date
and when you run this script again it will auto download the EOD, index & Futures data.
