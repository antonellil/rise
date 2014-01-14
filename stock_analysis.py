import json, ystockquote, datetime, urllib2, argparse
from BeautifulSoup import BeautifulSoup

# Parameters are tuples
def filter_stocks(stocks, mean_rec, low_return, median_return, min_brokers, mr_change):
	chosen_stocks = {}

	min_low_return, max_low_return = low_return
	min_median_return, max_median_return = median_return
	min_mean_rec, max_mean_rec = mean_rec
	min_mr_change, max_mr_change = mr_change

	for symbol in stocks:
		try:
			curr_price = float(stocks[symbol]['data'][0])
			low_return = float(stocks[symbol]['analysts'][6]) / curr_price
			median_return = float(stocks[symbol]['analysts'][4]) / curr_price
			mean_rec = float(stocks[symbol]['analysts'][0])
			num_brokers = float(stocks[symbol]['analysts'][7])
			mrchange=float(stocks[symbol]['analysts'][2])

			if max_low_return >= low_return >= min_low_return and \
				min_mean_rec <= mean_rec <= max_mean_rec  and \
				num_brokers >= min_brokers and \
				max_median_return >= median_return >= min_median_return and \
				min_mr_change <= mrchange <= max_mr_change:
		
				chosen_stocks[symbol] = stocks[symbol]
		except:
			pass

	return chosen_stocks

def get_price(soup, past_days):
	found_price = False
	start = past_days
	price = 0

	try:
		while not found_price:
			if len(soup.find("table",{'class':'yfnc_datamodoutline1'}).find('tr').findAll('tr')[start].findAll('td')) > 3:
				price = soup.find("table",{'class':'yfnc_datamodoutline1'}).find('tr').findAll('tr')[start].findAll('td')[4].text
				found_price = True
			start += 1
		return price.replace(',','')
	except:
		return 0.0

# Calculate stock performance over a period given a symbol and valid previous number of business days
# Returns a float between 0.0 and 1.0
def calculate_performance(symbol, past_days):
	request = urllib2.Request("http://finance.yahoo.com/q/hp?s="+symbol)
	response = urllib2.urlopen(request)
	soup = BeautifulSoup(response.read())
	todays_price = get_price(soup, 1)
	last_price = get_price(soup,past_days)
	if todays_price == 0.0 or last_price == 0.0:
		return False
	else:
		return (float(todays_price)/float(last_price)) - 1.0

# Calculate historical performances for a list of stocks
# Returns a list of tuples of stock symbol and performance over time period ie. ('AAPL', .3), ('GOOG', -.1)
def historical_performances(stocks, past_days):
	performances = []

	for symbol in stocks:
		print 'Processing', symbol
		performance = calculate_performance(symbol, past_days)
		if performance != False:
			performances.append((symbol,performance))

	return performances

def average_performance(performances):
	total = 0.0

	for symbol, p in performances:
		total += p

	return total/len(performances)

def print_performances(performances):
	for symbol, p in performances:
		print symbol, p

def output_to_file(projected_good_stocks):
	symbol_file = open('stockdata/chosen_stocks.txt','w')
	for stock in projected_good_stocks:
		symbol_file.write(stock+'\n')
	symbol_file.close()

def main(stocks, past_days):
	# Filter stocks parameters: stocks, mean_rec, lowtar/curprice, mediantar/curprice, min_brokers, mrchange
	projected_good_stocks = filter_stocks(stocks, (1.0,2.0), (1.0,100.0),(1.0,100.0), 10.0,(-5.0,-0.1))
	output_to_file(projected_good_stocks)

	# Calculate performances of the stocks
	print 'Number of chosen stocks found:',len(projected_good_stocks)
	print 'Calculating chosen performances...'
	print '==============================='
	print 'Chosen performances...'
	print '-------------------------------'
	good_performances = historical_performances(projected_good_stocks, past_days)
	print 'Number of stocks processed correctly:',len(good_performances)
	print '==============================='
	print 'Chosen performances:'
	print '-------------------------------'
	print print_performances(good_performances)
	print '==============================='
	print 'Results'
	print '-------------------------------'
	print 'Nasdaq:', str(calculate_performance('^IXIC',past_days))
	print 'NYSE:', str(calculate_performance('^NYA',past_days))
	print 'S&P 500 performance:', str(calculate_performance('^GSPC',past_days))
	print 'Chosen portfolio performance:', str(average_performance(good_performances))


# Get arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('stock_data', type=str)
args = argparser.parse_args()

# Run the program
raw_stocks_file = open(args.stock_data,'r')
stocks = json.loads(raw_stocks_file.readline())

main(stocks, 15)




