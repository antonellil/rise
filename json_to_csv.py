import csv, json

json_file = open('stockdata/stocks05-01-2014.json','r')
stock_dictionary = json.loads(json_file.readline())

print stock_dictionary

csv_file = csv.writer(open("stocks05-01-2014.csv",'wb+'))

csv_file.writerow(["Stock","Price","Beta","Volume","Avg 3 Month Vol","Market Cap","P/E","EPS","MR This Week","MR Last Week","Change","Mean Target","Median Target","High Target","Low Target","Num Brokers"])

for stock in stock_dictionary:
	try:
		curr_row = [stock] + stock_dictionary[stock]['data'] + stock_dictionary[stock]['analysts']
		csv_file.writerow(curr_row)
	except:
		pass
