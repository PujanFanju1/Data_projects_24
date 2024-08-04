from datetime import datetime
import pandas as pd
import requests

'''
I have kept the extraction and cleaning as different functions for modularization so that each function has a specific job.
It also makes each function reusable- there may be cases in the future where we just want to extract from API or just clean data.
It also makes testing more simple as we can test the extraction and cleaning seperately.
'''

def extracting_api(equity, time_interval,month):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={equity}&interval={time_interval}min&month={month}&outputsize=full&apikey=X8BSVWLS7830G3UI'
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()  # Convert JSON response to Python dictionary or list
    else:
        print('Failed to retrieve data:', response.status_code)

    df = pd.DataFrame(data)
    # df['Equity'] = equity

    return df



def cleaning(df):
    '''
    Input: Raw pandas data frame
    Output: Cleaned pandas data frame

    This function takes in a dataframe from the AlphaVantage website and cleans it.
    '''

    # Reset index and rename the index column to 'datetime'
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'datetime'}, inplace=True)
    
    # Drop 'Meta Data' column if it exists
    df.drop(['Meta Data'], axis=1, inplace=True, errors='ignore')
    
    # Skip the first 6 rows as indicated
    df = df.iloc[6:]

    df['datetime'] = pd.to_datetime(df['datetime'])


    # Split 'datetime' into 'date' and 'time'
    # df[['date', 'time']] = df['datetime'].str.split(' ', expand=True)
    # df.drop('datetime', axis=1, inplace=True)

    # Convert 'Time Series (5min)' column to string
    df['Time Series (5min)'] = df['Time Series (5min)'].astype(str)

    # Split 'Time Series (5min)' into respective columns
    # This is how the 'Time Series (5min)' column currently looks:
    # "{'1. open': '182.3430', '2. high': '182.6470', '3. low': '182.3320', '4. close': '182.5560', '5. volume': '194'}"
    #  We want the extract the numbers only e.g. 182.3430 for each of 'open', 'high', 'low', 'close' and 'volume'.

    # First split into the 5 different columns by ','
    df[['open','high','low','close','volume']] = df['Time Series (5min)'].str.split(',',expand=True)

    # For each column, split by ':' and get the second element as this is where the number is. 
    # Finally, strip away any unncessary characters so we just have the number and convert it to float.
    df['open'] = df['open'].str.split(':').str[1].str.strip().str.strip("'").astype(float)
    df['high'] = df['high'].str.split(':').str[1].str.strip().str.strip("'").astype(float)
    df['low'] = df['low'].str.split(':').str[1].str.strip().str.strip("'").astype(float)
    df['close'] = df['close'].str.split(':').str[1].str.strip().str.strip("'").astype(float)
    df['volume'] = df['volume'].str.split(':').str[1].str.strip().str.strip("'}").astype(float)
    
    df.drop('Time Series (5min)', axis=1, inplace=True)
    
    # Alternative using 'split' instead of regex:
    '''
    # Split 'Time Series (5min)' into respective columns
    # This is how the 'Time Series (5min)' column currently looks:
    # "{'1. open': '182.3430', '2. high': '182.6470', '3. low': '182.3320', '4. close': '182.5560', '5. volume': '194'}"
    #  We want the extract the numbers only e.g. 182.3430 for the 'open' column.
    # \. just means literal .
    # \d means any digit (0-9)
    # ([\d\.]+) takes a group of numbers and . and captures this as a group.
 
    
    df[['open', 'high', 'low', 'close', 'volume']] = df['Time Series (5min)'].str.extract(
        r"'1\. open': '([\d\.]+)'"
        r"'2\. high': '([\d\.]+)'"
        r"'3\. low': '([\d\.]+)'"
        r"'4\. close': '([\d\.]+)'"
        r"'5\. volume': '([\d\.]+)'")

    # Convert columns to appropriate types
    # df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    # df['volume'] = df['volume'].astype(float)
    '''

    # Convert 'date' to datetime
    # df['date'] = pd.to_datetime(df['date'])
    
    # Convert 'time' to time
    # df['time'] = df['time'].apply(lambda x: datetime.strptime(x, "%H:%M:%S").time())

    # Sort by 'date' and 'time'
    # df = df.sort_values(['date', 'time']).reset_index(drop=True)

    df = df.sort_values(['datetime']).reset_index(drop=True)

    return df


