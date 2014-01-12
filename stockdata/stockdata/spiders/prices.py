from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from stockdata.items import StockdataItem
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

import json, math, csv, time

stock_prices = {}
TODAYS_DATE = 'Jan 10, 2014'

class PricesSpider(CrawlSpider):
    # Spider defaults
    name = 'prices'
    allowed_domains = ['yahoo.com']
    start_urls = []
    # Open the desired symbols from the symbols file
    symbols_file = open('chosen_stocks.txt','r')
    symbols = symbols_file.readlines()
    for symbol in symbols:
        stock_prices[symbol.replace('\n','')] = []
        start_urls.append("http://finance.yahoo.com/q/hp?s=" + symbol.replace('\n',''))        
    print "Processing",symbols,"..."

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    # Scrapy automatically calls this method, sequentially, for every url in the 'start_urls' array
    def parse(self, response):
        # Parse this page for prices
        self.parse_page(response)
        # Get the link for the next page of prices and traverse
        sel = Selector(response)
        next_pages = sel.xpath('//a[contains(text(),"Next")]/@href').extract()
        # Get the next page of prices
        if len(next_pages) > 0:
            cleaned_url = 'http://finance.yahoo.com' + next_pages[0]
            yield Request(cleaned_url, callback=self.parse_page)

    # Take a response and parse the data part of the stock data dictionary
    def parse_page(self, response):
        sel = Selector(response)
        symbol = sel.xpath('//div[@id="yfi_investing_nav"]/div[@class="hd"]/h2/text()').extract()[0].replace('More On ','')
        print "Parsing",symbol
        tables = sel.xpath('//table[contains(@class, "yfnc_datamodoutline1")]')
        if len(tables) > 0:
            self.get_prices(symbol, tables.xpath('tr/td/table/tr')[1:])

    def get_prices(self, symbol, table):
        prices = []
        for row in table:
            if len(row.xpath('td')) > 3:
                day = row.xpath('td[1]/text()').extract()[0]
                open_price = row.xpath('td[2]/text()').extract()[0]
                close_price = row.xpath('td[7]/text()').extract()[0]
                prices.append((day, open_price, close_price))
        first, _, _ = prices[0]
        prices.reverse()
        if first == TODAYS_DATE:
            stock_prices[symbol] = stock_prices[symbol] + prices
        else:
            stock_prices[symbol] = prices + stock_prices[symbol]

    def spider_closed(self):
        print "spider closed"
        stocks = open('stock_prices_'+time.strftime("%d_%m_%Y")+'.json', 'w')
        stocks.write(json.dumps(stock_prices,sort_keys=True,separators=(',',':')))
        stocks.close()

        

