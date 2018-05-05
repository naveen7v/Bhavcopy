'''
This script is a modified version from
http://blog.bradlucas.com/posts/2017-06-02-new-yahoo-finance-quote-download-url/

The start date is from 2008-01-01
'''

import re, sys, time, requests,pandas as pd
from io import StringIO


def split_crumb_store(v):
    return v.split(':')[2].strip('"')


def find_crumb_store(lines):
    # Looking for
    # ,"CrumbStore":{"crumb":"9q.A4D1c.b9
    for l in lines:
        if re.findall(r'CrumbStore', l):
            return l
    print("Did not find CrumbStore")


def get_page_data(symbol):
    url = "https://finance.yahoo.com/quote/%s/?p=%s" % (symbol, symbol)
    r = requests.get(url)
    cookie = {'B': r.cookies['B']}
    lines = r.content.decode('unicode-escape').strip(). replace('}', '\n')
    return cookie, lines.split('\n')


def get_cookie_crumb(symbol):
    cookie, lines = get_page_data(symbol)
    crumb = split_crumb_store(find_crumb_store(lines))
    return cookie, crumb


def get_data(symbol, start_date, end_date, cookie, crumb):
    url = "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&crumb=%s" % (symbol, start_date, end_date, crumb)
    p=requests.get(url, cookies=cookie).text
    a=pd.read_csv(StringIO(p),skiprows=range(1),names =['Date','Open','High','Low','Close','Adj Close','Volume'])
    return a

def download_quotes(symbol,write_to_file=False):
    start_date = 1199145600 # human readable date is 2008-01-01
    end_date = int(time.time())
    cookie, crumb = get_cookie_crumb(symbol)
    a = get_data(symbol, start_date, end_date, cookie, crumb)
    if write_to_file:    
        a.to_csv(symbol+'.csv', mode='a', header=False,index=False)
    else:
        a['DateTime']=pd.to_datetime(a.Date)#.dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.strftime('%Y-%m-%d %H:%M:%S')
        a=a[['DateTime','Open','High','Low','Close','Adj Close','Volume']]
        return a


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("\nUsage: get-yahoo-quotes.py SYMBOL\n\n")
    else:
        for i in range(1, len(sys.argv)):
            symbol = sys.argv[i]
            print("--------------------------------------------------")
            print("Downloading %s to %s.csv" % (symbol, symbol))
            download_quotes(symbol,write_to_file=True)
            print("--------------------------------------------------")
