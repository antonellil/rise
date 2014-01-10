import csv, json, argparse

def convert_file(json_file_path):
	json_file = open(json_file_path,'r')
	stock_dictionary = json.loads(json_file.readline())

	print json_file_path.replace('json','csv')

	csv_file = csv.writer(open(json_file_path.replace('json','csv'),'wb+'))

	csv_file.writerow(["Ticker","Price","Market Cap","Trailing P/E","Forward P/E", "PEG Ratio (5 yr expected)", "Price/Book (mrq)","Diluted EPS","Total Debt/Equity (mrq)", "Levered Free Cash Flow (ttm)", "Beta", "52-week Change", " S&P500 52-week change", "50 day moving average", "Short Ratio", "MR This Week","MR Last Week","Change","Mean Target","Median Target","High Target","Low Target","Num Brokers"])

	for stock in stock_dictionary:
		try:
			curr_row = [stock] + stock_dictionary[stock]['data'] + stock_dictionary[stock]['analysts']
			csv_file.writerow(curr_row)
		except:
			pass

argparser = argparse.ArgumentParser()
argparser.add_argument('stock_data', type=str)
args = argparser.parse_args()

convert_file(args.stock_data)


