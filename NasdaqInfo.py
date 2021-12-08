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
        import pandas as pd
        import requests
        import random
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
