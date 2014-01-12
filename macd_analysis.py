# MACD analysis of buying/selling stocks over given time period for chosen stocks
import json, numpy, math, argparse

# Starting environment variables
COMISSION = 10.00
STARTING_CAPITAL = 2000.0

# Loads the stock data from the chosen stocks file
def load_stocks(stocks_file):
    open_file = open(stocks_file,'r')
    stock_prices = json.loads(open_file.readline())
    return stock_prices

# Returns list of EMAs given list of prices
def emas(prices, period):
    initial_sma = sum(prices[:period])/period
    emas = [initial_sma]*period
    prev_ema = initial_sma
    k = 2.0/(float(period)+1.0)
    for i in range(period,len(prices)):
        ema = prices[i]*k + prev_ema * (1.0-k)
        emas.append(ema)
        prev_ema = ema
    return emas

# Gets the prices from the loaded prices
def get_price_series(stock_prices, symbol):
    closing_prices = []
    opening_prices = []
    dates = []
    for day in stock_prices[symbol]:
        dates.append(day[0])
        opening_prices.append(float(day[1]))
        closing_prices.append(float(day[2]))

    return dates, opening_prices, closing_prices

# Generates the MACD calculation
def calculate_macd_series(prices, slow_period, fast_period, signal_period):
    slow_emas = emas(prices, slow_period)
    fast_emas = emas(prices, fast_period)

    macd = list(numpy.array(fast_emas) - numpy.array(slow_emas))
    raw_signal = emas(macd, signal_period)

    signal = []
    for r in raw_signal:
        signal.append(r-0.1)

    divergence = list(numpy.array(macd) - numpy.array(signal))

    return macd, signal, divergence

# Performs the MACD purchasing right before close of current day
def run_macd(macd, divergence, signal, dates, start_day, closing_prices, threshold):
    intervals = len(dates)

    capital = STARTING_CAPITAL

    if len(macd)==len(divergence)==len(signal)==len(dates):
        print "You start trading on",dates[start_day]," with $",capital," and no holdings:"
        holding = False
        shares = 0

        # Simply look at MACD divergence as signal
        for i in range(start_day,intervals-1):
            if macd[i] < signal[i] and holding and divergence[i] < (-1.0)*threshold:
                print "Sell: ",shares,"shares on",dates[i],"at $",closing_prices[i],"/ share"
                capital = capital - COMISSION + shares*closing_prices[i]
                holding = False
                shares = 0
                print "---------------"
            elif macd[i] >= signal[i] and not holding and divergence[i] > threshold:
                print "FIRE TRADE"
                shares = math.floor(capital / closing_prices[i])
                print "Buy",shares,"shares on",dates[i],"at $",closing_prices[i],"/ share"
                capital = capital - COMISSION - shares*closing_prices[i]
                holding = True

        capital += shares*float(closing_prices[intervals-1])
        roi_macd = (capital / STARTING_CAPITAL) - 1.0
        roi_period = (float(closing_prices[intervals-1])/closing_prices[start_day]) - 1.0
        print "Sell out on",dates[intervals-1]," and have $",capital
        print "ROI MACD:",roi_macd
        print "ROI Period:",roi_period
        return roi_macd, roi_period
    else:
        print 'Error: data length discrepancy'

# Main function
def main(stocks_file, slow_period, fast_period, signal_period, start_day):
    # Load in the stock prices
    stock_prices = load_stocks(stocks_file)
    total_roi_macd = 0
    total_roi_period = 0

    # Iterate throug the stock symbols
    for symbol in stock_prices:
        print 'Running MACD for',symbol,'........'
        # Get the appropriate prices and dates for each stock
        dates, opening_prices, closing_prices = get_price_series(stock_prices,symbol)
        # Get the MACD series with opening prices
        macd, signal, divergence = calculate_macd_series(closing_prices,slow_period, fast_period, signal_period)
        # Perform the MACD
        roi_macd, roi_period = run_macd(macd, divergence, signal, dates, start_day, closing_prices, 0.0)
        total_roi_macd += roi_macd
        total_roi_period += roi_period
        print "==============="

    average_roi_macd = total_roi_macd/len(stock_prices)
    average_roi_period = total_roi_period/len(stock_prices)

    print "Average ROI MACD:",average_roi_macd
    print "Average ROI Period:",average_roi_period

# Get arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('stock_prices', type=str)
argparser.add_argument('slow_period', type=int)
argparser.add_argument('fast_period', type=int)
argparser.add_argument('signal_period', type=int)
args = argparser.parse_args()

# Run the program
main(args.stock_prices, args.slow_period, args.fast_period, args.signal_period, 30)

