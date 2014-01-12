# Future Analysis Program
# Takes a folder of stock data files, a start date, and an end date
# lpa22
import json, math, argparse, datetime

# folder_path = path to stock data folder
# start_date = 'month/day/year'
# end_date = 'month/day/year'
# Output: tuple of the stock_data date-indexed dictionary and list of dates in range
def init(folder_path, start_date, end_date):
	stock_data = {}
	date_range = []

	start = datetime.datetime.strptime(start_date, '%m/%d/%y')
	end = datetime.datetime.strptime(end_date, '%m/%d/%y')

	while start <= end:
		date_range.append(start.strftime('%m/%d/%y'))
		data_file = open(folder_path+'/stock_data_'+start.strftime('%d_%m_%y'),'r')
		stock_data[start.strftime('%m/%d/%y')] = json.loads(data_file.readline())
		start = start + datetime.timedelta(days=1)

	return stock_data, date_range

# stock_data = date-indexed stock dictionary
# start_date = 'month/day/year'
# Other parameters are filters for selecting stocks
def filter_stocks(stock_data, start_date, mean_rec, low_return, median_return, min_brokers):
	chosen_stocks = []

	min_low_return, max_low_return = low_return
	min_median_return, max_median_return = median_return
	min_mean_rec, max_mean_rec = mean_rec
	min_mr_change, max_mr_change = mr_change

	for symbol in stocks[start_date]:
		try:
			curr_price = float(stocks[symbol]['data'][0])
			low_return = float(stocks[symbol]['analysts'][6]) / curr_price
			median_return = float(stocks[symbol]['analysts'][4]) / curr_price
			mean_rec = float(stocks[symbol]['analysts'][0])
			num_brokers = float(stocks[symbol]['analysts'][7])

			if max_low_return >= low_return >= min_low_return and \
				min_mean_rec <= mean_rec <= max_mean_rec  and \
				num_brokers >= min_brokers and \
				max_median_return >= median_return >= min_median_return:

				chosen_stocks.append(symbol)
		except:
			pass

	return chosen_stocks

# stock_data = date-indexed stock dictionary
# chosen_stocks = list of symbols
# start_date = 'month/day/year'
# end_date = 'month/day/year'
def calculate_performance(stock_data, chosen_stocks, start_date, end_date):
	performances = []

	for symbol in chosen_stocks:
		try:
			start_price = float(stock_data[start_date][symbol]['data'][0])
			end_price = float(stock_data[end_date][symbol]['data'][0])
			performance = start_price/end_price - 1.0
			performances.append((symbol,performance))
		except:
			print "Error calculating performance of,"symbol

	return performances

# stock_data = date-indexed stock dictionary
# chosen_stocks = list of symbols
# raw_date_range = list of dates in desired range
def calculate_daily_changes(stock_data, chosen_stocks, raw_date_range):
	date_range = raw_date_range
	previous_date = date_range.pop(0)
	end_date = date_range.pop()
	daily_changes = {}

	for symbol in chosen_stocks:
		daily_changes[symbol] = {previous_date:True, end_date:True}

	for date in date_range:
		for symbol in chosen_stocks:
			# Pull previous and current mr and mean target values
			previous_mr = float(stock_data[previous_date][symbol]['analysts'][0])
			previous_mean_target = float(stock_data[previous_date][symbol]['analysts'][3])
			current_mr = float(stock_data[date][symbol]['analysts'][0])
			current_mean_target = float(stock_data[date][symbol]['analysts'][3])
			# Determine if a change occured on this date
			if current_mr != previous_mr or current_mean_target != previous_mean_target:
				daily_changes[stock][date] = True

		previous_date = date

	return daily_changes

# stock_data = date-indexed stock dictionary
# chosen_stocks = list of symbols
# daily_changes = dictionary of the daily changes returned by the calculate function
# Output: prints for each stock the mr and mean target on changes in the date_range
def analyze_daily_changes(stock_data, chosen_stocks, date_range, daily_changes):
	for symbol in chosen_stocks:
		print 'Processing',symbol,'...'

		for date in date_range:
			if date in daily_changes[symbol]:
				price = stock_data[date][symbol]['data'][0]
				mr = stock_data[date][symbol]['analysts'][0]
				mean_target = stock_data[date][symbol]['analysts'][3]
				print price, mr, mean_target

def main(folder_path, start_date, end_date):
	# Creates the date-indexed stock data dictionary
	print 'Initializing data...'
	stock_data, date_range = init(folder_path, start_date, end_date)
	# Specify filter parameters below for starting date
	mean_rec = (1.0,2.0)
	low_return = (1.0,100.0)
	median_return = (1.5,100.0)
	min_brokers = 3
	# Filter to chosen stocks with parameters above
	print 'Choosing stocks...'
	chosen_stocks = filter_stocks(stock_data, start_date, mean_rec,low_return, median_return, min_brokers)
	# Calculate performance over the time period for the chosen stocks
	print 'Calculating chosen stock performance...'
	chosen_performances = calculate_performance(stock_data, chosen_stocks, start_date, end_date)
	# Determine daily changes in mr and mean target for chosen stocks
	print 'Calculating daily stock changes...'
	daily_changes = calculate_daily_changes(stock_data, chosen_stocks, date_range)
	# Analyze the dailychanges of the chosen stocks
	print 'Analyzing daily stock changes...'
	analyze_daily_changes(stock_data, chosen_stocks, date_range, daily_changes)

main('stock_data_jsons','1/10/14','2/5/14')

