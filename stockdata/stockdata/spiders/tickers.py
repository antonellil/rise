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
                    start_urls.append("http://finance.yahoo.com/q/ks?s=" + row[0])        

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
            tables = sel.xpath('//table[contains(@class, "yfnc_datamodoutline1")]')
            # Get desired tables
            if len(tables) > 0:
                stock_data[symbol]['data'] = [price]
                val_measures = tables[0].xpath('tr/td/table/tr')
                income_statement = tables[4].xpath('tr/td/table/tr')
                balance_sheet = tables[5].xpath('tr/td/table/tr')
                cash_flow = tables[6].xpath('tr/td/table/tr')
                price_history = tables[7].xpath('tr/td/table/tr')
                share_stats = tables[8].xpath('tr/td/table/tr')
                self.generate_stock_data(symbol, val_measures, income_statement, balance_sheet, cash_flow, price_history, share_stats)

    def generate_stock_data(self, symbol, val_measures, income_statement, balance_sheet, cash_flow, price_history, share_stats):
        try:
            # val_measures - Market Cap, Trailing P/E, Forward P/E, PEG, P/B
            stock_data[symbol]['data'].append(val_measures[0].xpath('td[2]/span/text()').extract()[0])
            stock_data[symbol]['data'].append(val_measures[2].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(val_measures[3].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(val_measures[4].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(val_measures[6].xpath('td[2]/text()').extract()[0])
            # income_statement - Total D/E
            stock_data[symbol]['data'].append(income_statement[7].xpath('td[2]/text()').extract()[0])
            # balance_sheet - Total D/E
            stock_data[symbol]['data'].append(balance_sheet[4].xpath('td[2]/text()').extract()[0])
            # cash_flow - Free Cash Flow
            stock_data[symbol]['data'].append(cash_flow[2].xpath('td[2]/text()').extract()[0])
            # price_history - Beta, 52-week minus S&P 52-week, 50-day moving
            stock_data[symbol]['data'].append(price_history[1].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(price_history[2].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(price_history[3].xpath('td[2]/text()').extract()[0])
            stock_data[symbol]['data'].append(price_history[6].xpath('td[2]/text()').extract()[0])
            # share_stats - Short Ratio
            stock_data[symbol]['data'].append(share_stats[8].xpath('td[2]/text()').extract()[0])
        except:
            pass
        
    def parse_hp_stock_data(self, response):
        sel = Selector(response)
        symbol = sel.xpath('//div[@id="yfi_investing_nav"]/div[@class="hd"]/h2/text()').extract()[0].replace('More On ','')
        try:
            table = sel.xpath('//table[contains(@class, "yfnc_datamodoutline1")]')[0]
            hp = table.xpath('tr/td/table/tr[20]/td[5]/text()').extract()[0]
            if symbol in stock_data:
                if 'data' in stock_data[symbol]:
                    stock_data[symbol]['data'].insert(0,hp)
                else:
                    stock_data[symbol]['data'] = [hp]
            else:
                stock_data[symbol]['data'] = [hp]
        except:
            stock_data[symbol]['data'].append(0)
            print symbol, 'No HP Data'
    

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
        this_mr = recommendation[0].xpath('td[2]/text()').extract()
        last_mr = recommendation[1].xpath('td[2]/text()').extract()
        try:
            stock_data[symbol]['analysts'].append(this_mr[0])
            stock_data[symbol]['analysts'].append(last_mr[0])
            stock_data[symbol]['analysts'].append(float(this_mr[0])-float(last_mr[0]))
        except:
            stock_data[symbol]['analysts'] = ['N/A','N/A','N/A']

        for row in price_target:
            value = row.xpath('td[2]/text()').extract()
            if len(value) > 0:
                stock_data[symbol]['analysts'].append(value[0])

    def spider_closed(self):
        print "spider closed"
        stocks = open('stocks'+time.strftime("%d-%m-%Y-%H-%M-%S")+'.json', 'w')
        stocks.write(json.dumps(stock_data,sort_keys=True,separators=(',',':')))
        stocks.close()

        

