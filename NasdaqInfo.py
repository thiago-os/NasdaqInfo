import pandas as pd
import requests
import random
import time
from selenium import webdriver

class TickerData:

    @staticmethod
    def get_nasdaq(
            asdataframe: bool = True,
            user_agent_list: list = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            ]
    ):
        """
        Static method that scraps the list of tickers that changed recently published by the Nasdaq and returns
        the result as a dataframe or dictionary. Includes stocks and warrants.

        param asdataframe: True if you want a dataframe. False if you want a dictionary (old tickers are the keys).
        Default is True.
        return: Dataframe indexed by company name or dictionary of old and new ticker symbols (first item is
        'oldTicker': 'newTicker').
        user_agent_list: list of possible user agent headers to use randomly in the request call.
        """
        
        headers = [{'User-Agent': x} for x in user_agent_list]
        url = 'https://api.nasdaq.com/api/quote/list-type-extended/symbolchangehistory'
        header = random.choice(headers)

        str_json = requests.get(url, headers=header).text
        #print(str_json)

        df = pd.read_json(str_json)
        change_dict = {'Name': ('oldTicker', 'newTicker')}
        for row in df.loc['symbolChangeHistoryTable', 'data']['rows']:
            change_dict[row['companyName']] = (row['oldSymbol'], row['newSymbol'])

        if asdataframe:
            # Here is the solution:
            sol = pd.DataFrame.from_dict(change_dict, orient='index')

            # Use first value as header:
            sol.columns = sol.loc[sol.index[0]]
            sol = sol.drop(sol.index[0])
            return sol
        else:
            return dict((x, y) for x, y in change_dict.values())


class DelistWarning(object):
    def __init__(self, df_raw=None, df=None):
        self.df_raw = df_raw
        self.df = df

    @classmethod
    def get_data(
            cls,
            chromedriver_path,
            url='https://listingcenter.nasdaq.com/noncompliantcompanylist.aspx'
    ):
        """
        Returns a DalistWarning object with two attributes: df and df_raw. The main output is df, a pandas
        dataframe with columns symbol, deficiency (i.e., non compliance), market, and (notification) date.
        df is not indexed by symbol (there can be repeated symbols).
        df_raw is the same as df, but symbol_list replaces symbol (because some deficiencies
        relate to many symbols).

        :param chromedriver_path: Path for chromedriver.exe (https://chromedriver.chromium.org/).
        :param url: nasdaq page to be scraped.
        :return: DelistWarning object w/ df and df_raw pandas dataframes as attributes.
        """
        cols = ('symbol_list', 'deficiency', 'market', 'date')

        df = pd.DataFrame(columns=cols)
        driver = webdriver.Chrome(executable_path=chromedriver_path)

        driver.get(url)
        button = driver.find_element_by_class_name("rgExpand")
        button.click()

        # Wait for loading
        while len(driver.find_elements_by_class_name("rgAltRow")) == 0:
            time.sleep(1)

        # finish loading(?)
        time.sleep(2)

        mytable = driver.find_element_by_class_name('rgMasterTable')

        i = 0
        for row in mytable.find_elements_by_class_name("rgAltRow"):
            j = 0
            i += 1
            for cell in row.find_elements_by_css_selector('td'):
                if cell.text.strip():
                    if cols[j] == 'symbol_list':
                        df.loc[i, cols[j]] = cell.text.strip().split('  ')
                    else:
                        df.loc[i, cols[j]] = cell.text.strip()
                    j += 1
        driver.close()

        # Adjust df columns:
        df2 = df.explode('symbol_list').reset_index(drop=True)
        df2 = df2.rename(columns={'symbol_list': 'symbol'})
        df2['date'] = pd.to_datetime(df2['date'])
        df2 = df2.drop_duplicates()
        res = cls(df_raw=df, df=df2)
        return res
