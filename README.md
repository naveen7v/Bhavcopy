# Bhavcopy
Pythonic version bhavcopy. Downloads the EOD data from the last downloaded date.

This script pulls the data from NSE site.

Before running this script , create a file called log.txt and save it in the download directory
and write the date from which you want to download EOD data

From that file(log.txt) this script keeps track of the last downloaded date
and when you run this script again it will automatically downloads the EOD, index and Futures data.
