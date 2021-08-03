import data_support as ds
import data_analysis as da
import datetime
import pytz

HOMEPAGE_STOCKS = ['AAPL', 'GE', 'NKE', 'TSLA', 'TMUS', 'GOOG', 'AMZN', 'SBUX', 'FB', 'MSFT']
HOMEPAGE_NEWS_SIZE = 10
STOCK_NEWS_SIZE = 5
DEFAULT_HISTORIC_RANGE = 0
DEFAULT_HISTORICAL_TIMESPAN = 'day'
DEAFULT_MAIN_CHART_TIMESPAN = '1Min'
DEAFULT_ANALYSIS_CHART_TIMESPAN = 'day'
OVERVIEW_DATA_KEYS = ['MarketCapitalization', 'EBITDA', 'PERatio', 
'BookValue', 'DividendPerShare', 'DividendYield', 'EPS', 'QuarterlyEarningsGrowthYOY', 
'QuarterlyRevenueGrowthYOY', 'TrailingPE', 'ForwardPE',
'52WeekHigh', '52WeekLow','50DayMovingAverage','ForwardAnnualDividendRate',
'ForwardAnnualDividendYield']
NY = 'America/New_York'



def symbol_in_db(symbol):
    return ds.query_db(symbol)

def stock_info(symbol):
    '''returns price and percent change compared to yesterday's closing price, to display on stock's page'''
    data = ds.get_last_price({'symbol':symbol})
    current = data['Last Price']
    last_trading_day = data['Timestamp']
    datetime_object = datetime.datetime.fromtimestamp(last_trading_day)
    if datetime_object.weekday() == 0:
        start = str((datetime_object - datetime.timedelta(days=3)).date())+'T09:00:00-05:00'
        end = str((datetime_object - datetime.timedelta(days=3)).date())+'T16:00:00-05:00'
    else:
        start = str((datetime_object - datetime.timedelta(days=1)).date())+'T09:00:00-05:00'
        end = str((datetime_object - datetime.timedelta(days=1)).date())+'T16:00:00-05:00'
    previous_day_request = {
        'symbol':symbol,
        'timespan':'day',
        'from':start,
        'to':end,
        'limit':'1'
    }
    previous = ds.get_historical(previous_day_request)
    previous = previous[-1]['Close']
    change = round(current - previous, 3)
    percent_change = da.percent_change(current, previous)
    percent_change = round(percent_change, 3)

    return current, change, percent_change

def news_page():
    '''
    news
    '''
    news_request = {
        'size':HOMEPAGE_NEWS_SIZE
    }
    data = ds.get_general_news(news_request)
    datadict = {
        'records':data,
        'colnames':data[0]['data'].keys()
    }

    return datadict

def top_stocks_page():
    data = []
    for symbol in HOMEPAGE_STOCKS:
        last_price, change, percent_change = stock_info(symbol)

        datadict = {
        'name':symbol,
        'price':last_price,
        'change':change,
        'percent change':percent_change,
        }
        data.append(datadict)

    now = datetime.datetime.now()
    dt_string = now.strftime("%B %d %H:%M")+ ' EST'

    datadict = {
        'records':data,
        'colnames':data[0].keys(),
        'time':dt_string
    }

    return datadict

def stock_overview_page(symbol, timespan):
    print('timespan', timespan)
    '''
    latest price, latest % change, last retrieved time, exchange, overviewdata
    minute data for the day for chart
    news
    '''
    last_price, change, percent_change = stock_info(symbol)

    today = datetime.datetime.today()
    timezone = pytz.timezone(NY)
    today = today.astimezone(timezone)
    end = today.isoformat()

    if timespan == 'day':
        chart_timespan = '1Min'
        start = ''

        if today.weekday() == 6:
            friday = (today - datetime.timedelta(days=2)).date()
            start = str(friday)+'T09:30:00-05:00'
        elif today.weekday() == 0:
            friday = (today - datetime.timedelta(days=3)).date()
            start = str(friday)+'T09:30:00-05:00'
        else:
            day_before = (today - datetime.timedelta(days=1)).date()
            start = str(day_before)+'T09:30:00-05:00'

    elif timespan == 'month':
        chart_timespan = 'day'
        month = today.month - 1
        start = today.replace(month=month)
        start = start.isoformat()
    elif timespan == 'year':
        chart_timespan = 'day'
        month = today.year - 1
        start = today.replace(year=month)
        start = start.isoformat()

    historical_req  = {
        'symbol':symbol,
        'timespan':chart_timespan,
        'from':start,
        'to':end
    }
            
    historical_data = ds.get_historical(historical_req)

    historical_data_1 = {
        'labels': [ d['Date'] for d in historical_data],
        'values': [ d['Close'] for d in historical_data]
    }

    overview_data = ds.get_company_overview({'symbol':symbol})

    company_name = overview_data['Name']
    company_news_req = { 
        'symbol':company_name,
        'size':STOCK_NEWS_SIZE
    }

    data = ds.get_company_news(company_news_req)

    news = {
        'records':data,
        'colnames':data[0]['data'].keys()
    }


    overview_data_1 = {
        'Market Cap ':overview_data['MarketCapitalization'], 
        'EBITDA':overview_data['EBITDA'], 
        'PE Ratio':overview_data['PERatio'], 
        'Book Value':overview_data['BookValue'], 
        'Dividend Per Share':overview_data['DividendPerShare'], 
        'Dividend Yield':overview_data['DividendYield'], 
        'EPS':overview_data['EPS'], 
        'Quarterly Earnings GrowthYOY':overview_data['QuarterlyEarningsGrowthYOY'], 
        'Quarterly Revenue Growth YOY':overview_data['QuarterlyRevenueGrowthYOY'], 
        'Trailing PE':overview_data['TrailingPE'], 
        'Forward PE':overview_data['ForwardPE'],
        '52 Week High':overview_data['52WeekHigh'], 
        '52 Week Low':overview_data['52WeekLow'],
        '50 Day Moving Average':overview_data['50DayMovingAverage'],
        'Forward Annual Dividend Rate':overview_data['ForwardAnnualDividendRate'],
        'Forward Annual Dividend Yield':overview_data['ForwardAnnualDividendYield']
    }


    for key, value in overview_data_1.items():
        if value == 'None':
            overview_data_1[key] = 'N/A'

    now = datetime.datetime.now()
    dt_string = now.strftime("%B %d %H:%M")+ ' EST'

    datadict = {
        'name':symbol,
        'price':last_price,
        'change':change,
        'percent change':percent_change,
        'last retrieved time':dt_string ,
        'news':news,
        'chart_data':historical_data_1,
        'overview_data':overview_data_1
    }

    labels = historical_data_1['labels']
    values = historical_data_1['values']
    return datadict, labels, values, company_name

def stock_historic_page(stock, timerange=None):

    if timerange == None:
        today = datetime.datetime.today()
        timezone = pytz.timezone(NY)
        today = today.astimezone(timezone)
        end = today.isoformat()
        month = today.month - 1
        start = today.replace(month=month)
        start = str(start.date())+'T09:30:00-05:00'
    else:
        start = timerange['start']
        end = timerange['end']

    historical_req  = {
        'symbol':stock,
        'timespan':DEFAULT_HISTORICAL_TIMESPAN,
        'from':start,
        'to':end
    }
    data = ds.get_historical(historical_req)

    datadict = {
        'records':data[::-1],
        'colnames':data[0].keys()
    }

    return datadict

def stock_analysis_page(stock, timespan):

    today = datetime.datetime.today()
    timezone = pytz.timezone(NY)
    today = today.astimezone(timezone)
    end = today.isoformat()

    if timespan == 'day':
        chart_timespan = '1Min'
        start = ''

        if today.weekday() == 6:
            friday = (today - datetime.timedelta(days=2)).date()
            start = str(friday)+'T09:30:00-05:00'
        elif today.weekday() == 0:
            friday = (today - datetime.timedelta(days=3)).date()
            start = str(friday)+'T09:30:00-05:00'
        else:
            day_before = (today - datetime.timedelta(days=1)).date()
            start = str(day_before)+'T09:30:00-05:00'

    elif timespan == 'month':
        chart_timespan = 'day'
        month = today.month - 1
        start = today.replace(month=month)
        start = start.isoformat()
    elif timespan == 'year':
        chart_timespan = 'day'
        month = today.year - 1
        start = today.replace(year=month)
        start = start.isoformat()

    historical_req  = {
        'symbol':stock,
        'timespan':chart_timespan,
        'from':start,
        'to':end
    }

    historical_data = ds.get_historical_2(historical_req)

    length = len(historical_data)
    first_date = historical_data[0]['Date']
    return first_date, length, historical_data

