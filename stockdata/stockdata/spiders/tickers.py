from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from stockdata.items import StockdataItem
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

import json
import math
import csv
import time

stock_data = {}

class TickersSpider(CrawlSpider):
    name = 'tickers'
    allowed_domains = ['yahoo.com']
    start_urls = []

    # Open the various market CSV files
    nasdaq_tickers = open('nasdaq.csv', 'rb')
    nyse_tickers = open('nyse.csv','rb')

    markets = [nasdaq_tickers,nyse_tickers]

    count = 0

    for market in markets:
        for i,row in enumerate(csv.reader(market, delimiter=',', quotechar='"')):
            count += 1
            if i > 0:
                if '^' not in row[0] and '/' not in row[0]:
                    stock_data[row[0]] = {}
                    start_urls.append("http://finance.yahoo.com/q?s=" + row[0])        

    print count

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    # Scrapy automatically calls this method, sequentially, for every url in the 'start_urls' array
    def parse(self, response):
        # Parse this page for data
        self.parse_stock_data(response)
        # Get the stock symbol for the  analyst opinion page and callback to parse it
        symbol_sel = Selector(response)
        symbol = symbol_sel.xpath('//div[@id="yfi_investing_nav"]/div[@class="hd"]/h2/text()').extract()[0].replace('More On ','')
        cleaned_url = "http://finance.yahoo.com/q/ao?s=" + symbol
        yield Request(cleaned_url, callback=self.parse_stock_analyst_data)

    # Take a response and parse the data part of the stock data dictionary
    def parse_stock_data(self, response):
        sel = Selector(response)

        symbol = sel.xpath('//div[@id="yfi_investing_nav"]/div[@class="hd"]/h2/text()').extract()[0].replace('More On ','')

        if symbol in stock_data:
            price = sel.xpath('//span[@class="time_rtq_ticker"]/span/text()').extract()[0]
            stock_data[symbol]['data'] = [price]
            quote_summary1 = sel.xpath('//div[@id="yfi_quote_summary_data"]/table[@id="table1"]/tr')
            quote_summary2 = sel.xpath('//div[@id="yfi_quote_summary_data"]/table[@id="table2"]/tr')
            self.generate_stock_data(symbol, quote_summary1, quote_summary2)

    def generate_stock_data(self, symbol, quote_summary1, quote_summary2):
        # First Table - Beta
        try:
            stock_data[symbol]['data'].append(quote_summary1[5].xpath('td/text()').extract()[0])
            # Second Table - Volume, 3m Vol, Market cap, P/E, EPS
            stock_data[symbol]['data'].append(quote_summary2[2].xpath('td/span/text()').extract()[0])
            stock_data[symbol]['data'].append(quote_summary2[3].xpath('td/text()').extract()[0])
            stock_data[symbol]['data'].append(quote_summary2[4].xpath('td/span/text()').extract()[0])
            stock_data[symbol]['data'].append(quote_summary2[5].xpath('td/text()').extract()[0])
            stock_data[symbol]['data'].append(quote_summary2[6].xpath('td/text()').extract()[0])
        except:
            stock_data[symbol]['data'] = stock_data[symbol]['data'] + [0]*6
        

    # Take a response from the analyst opinion page and parse the analysts part of the stock data dictionary
    def parse_stock_analyst_data(self,response):
        sel = Selector(response)

        symbol = sel.xpath('//div[@id="yfi_investing_nav"]/div[@class="hd"]/h2/text()').extract()[0].replace('More On ','')

        if symbol in stock_data:
            stock_data[symbol]['analysts'] = []
            tables = sel.xpath('//table[contains(@class, "yfnc_datamodoutline1")]')
            if len(tables) > 1:
                self.generate_stock_analyst_data(symbol, tables[0].xpath('tr'), tables[1].xpath('tr'))

    def generate_stock_analyst_data(self, symbol, recommendation, price_target):
        for table in [recommendation, price_target]:
            for row in table:
                value = row.xpath('td[2]/text()').extract()
                if len(value) > 0:
                    stock_data[symbol]['analysts'].append(value[0])

    def spider_closed(self):
        print "spider closed"
        stocks = open('stocks'+time.strftime("%d-%m-%Y")+'.json', 'w')
        stocks.write(json.dumps(stock_data,sort_keys=True,separators=(',',':')))
        stocks.close()

        

