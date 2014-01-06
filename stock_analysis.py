import json

raw_stocks_file = open('stockdata/stocks.json','r')
stocks = json.loads(raw_stocks_file.readline())
count = 0

for symbol in stocks:
	try:
		low_target = float(stocks[symbol]['analysts'][6])
		curr_price = float(stocks[symbol]['data'][0])
		mean_rec = float(stocks[symbol]['analysts'][0])
		num_brokers = float(stocks[symbol]['analysts'][7])
		mean_target = float(stocks[symbol]['analysts'][4])

		desired_mean_rec = 2
		desired_return = 1.6
		desired_min_brokers = 5

		if low_target > curr_price and \
			mean_rec <= desired_mean_rec and \
			num_brokers >= desired_min_brokers and \
			mean_target / curr_price > desired_return:

			print symbol, stocks[symbol]
			count += 1
	except:
		pass
	# if len(stocks[symbol]['data']) > 0 and len(stocks[symbol]['analysts']) > 0:

print count

