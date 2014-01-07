import json, ystockquote, datetime

# Parameters are tuples
def filter_stocks(stocks, mean_rec, low_return, median_return, beta, min_brokers):
	chosen_stocks = {}

	min_low_return, max_low_return = low_return
	min_median_return, max_median_return = median_return
	min_mean_rec, max_mean_rec = mean_rec
	min_beta, max_beta = beta

	for symbol in stocks:
		try:
			curr_price = float(stocks[symbol]['data'][0])
			low_return = float(stocks[symbol]['analysts'][6]) / curr_price
			median_return = float(stocks[symbol]['analysts'][4]) / curr_price
			beta = float(stocks[symbol]['data'][1])
			mean_rec = float(stocks[symbol]['analysts'][0])
			num_brokers = float(stocks[symbol]['analysts'][7])
			
			if max_low_return >= low_return >= min_low_return and \
				min_mean_rec <= mean_rec <= max_mean_rec  and \
				num_brokers >= min_brokers and \
				max_median_return >= median_return >= min_median_return and \
				min_beta <= beta <= max_beta:

				chosen_stocks[symbol] = stocks[symbol]
		except:
			pass

	return chosen_stocks

# Calculate stock performance over a period given a symbol and valid previous number of days
# Returns a float between 0.0 and 1.0
def calculate_performance(symbol, past_days):
	try:
		previous_date = str(datetime.date.today()-datetime.timedelta(past_days))
		stock_current_price = ystockquote.get_price(symbol)
		stock_past_price_object = ystockquote.get_historical_prices(symbol, previous_date, previous_date)
		stock_past_price = stock_past_price_object[previous_date]['Close']
		return (float(stock_current_price)/float(stock_past_price)) - 1.0
	except:
		return 0.0

# Calculate historical performances for a list of stocks
# Returns a list of tuples of stock symbol and performance over time period ie. ('AAPL', .3), ('GOOG', -.1)
def historical_performances(stocks, past_days):
	performances = []

	for symbol in stocks:
		print 'Processing', symbol
		performances.append((symbol,calculate_performance(symbol, past_days)))

	return performances

def average_performance(performances):
	total = 0.0

	for symbol, p in performances:
		total += p

	return total/len(performances)

def print_performances(performances):
	for symbol, p in performances:
		print symbol, p

# Determine valid previous date starting with past_days (could be weekend, holiday, etc.)
def valid_past_day(raw_past_days):
	# Using Nasdaq ticker
	past_days = raw_past_days
	previous_date = str(datetime.date.today()-datetime.timedelta(past_days))
	price_obj = ystockquote.get_historical_prices('^IXIC', previous_date, previous_date)

	while price_obj == {}:
		past_days = past_days + 1
		previous_date = str(datetime.date.today()-datetime.timedelta(past_days))
		price_obj = ystockquote.get_historical_prices('^IXIC', previous_date, previous_date)

	return past_days

def main(stocks, raw_past_days):
	# Get valid past days
	past_days = valid_past_day(raw_past_days)
	# Filter stocks parameters: stocks, mean_rec, low_return, median_return, beta, min_brokers
	projected_good_stocks = filter_stocks(stocks, (1.0,2.0), (1.0,20.0), (1.5, 20.0), (1.0, 100.0), 2)
	print 'Number of chosen stocks found:',len(projected_good_stocks)
	# Calculate performances of the stocks
	print 'Calculating chosen performances...'
	print '==============================='
	print 'Chosen performances...'
	print '-------------------------------'
	good_performances = historical_performances(projected_good_stocks, past_days)
	print '==============================='
	print 'Chosen performances:'
	print '-------------------------------'
	print print_performances(good_performances)
	print '==============================='
	print 'Results'
	print '-------------------------------'
	print 'Nasdaq performance:', str(calculate_performance('^IXIC',past_days))
	print 'NYSE performance:', str(calculate_performance('^NYA',past_days))
	print 'Chosen portfolio performance:', str(average_performance(good_performances))


raw_stocks_file = open('stockdata/stocks06-01-2014.json','r')
stocks = json.loads(raw_stocks_file.readline())

main(stocks, 30)




