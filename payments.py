import datetime
import json
import os
from ah_requests import AhRequest
from exceptions import NoAPIKeyPresent
from logger import Logger
LOG = Logger()
ah_request = AhRequest()

CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', None)
if not CURRENCY_API_KEY:
    raise NoAPIKeyPresent("Can't find 'CURRENCY_API_KEY' in the env variables", status_code=500) 
    

# How much is the increase/decrease (in %) from one number(start) 
# to another (end)
def percent_diff(start,end):
    result = 100*(end / start)-100
    return round(result, 3)

# Whats is the amount when increased/decreased by X% (pct)
def pct_change(number, pct):
    result = number*(pct/100)
    return round(result, 3)

def today(d=None):
    today = datetime.date.today()
    if d:
        datum = today + datetime.timedelta(days=d)
        return datum.strftime('%Y-%m-%d')
    else:
        return today.strftime('%Y-%m-%d')

def queryCurrencyApi(pair, date):
    url = "http://www.apilayer.net/api/historical?access_key={}&source={}&currencies={}&date={}".format(CURRENCY_API_KEY, pair[:3], pair[3:],date)
    #LOG.console(url)
    res = ah_request.get(url=url)
    res = res.json()
    return float(res['quotes'][pair])
    

def result(payload):
    todays_date = today()
    data = []
    for t in payload["transactions"]:
        obj = {}
        if 'fixed_rate' in t:
            obj['fixed_rate'] = t['fixed_rate']
        currency_from = t["currency_from"]
        currency_to = t["currency_to"]
        pair = currency_from+currency_to
        obj['direction'] = t['direction']
        obj['pair'] = pair
        if t['start'] <= todays_date:
            obj["project_start_rate"] = queryCurrencyApi(pair=pair, date=t['start'])
        obj['payments'] = []
        for p in t["payments"]:
            if p['date'] <= todays_date:
                rate = queryCurrencyApi(pair=pair, date=p['date'])
                obj["payments"].append(dict(date=p['date'], rate=rate, amount=p['amount']))
        data.append(obj)
    
    for transaction in data:
        for payment in transaction['payments']: 
            if 'fixed_rate' in transaction:
                payment['pct_diff'] = 0
                payment['abs_diff'] = 0
            else:
                payment['pct_diff'] = percent_diff(start=transaction['project_start_rate'], end=payment['rate'])
                payment['abs_diff'] = pct_change(number=payment['amount'], pct=payment['pct_diff'])

    return data   

