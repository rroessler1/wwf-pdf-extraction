import pandas as pd

def price_valudator(data):
    data.fillna('1',inplace=True)
    return ['Passed' if data.discount_price/data.percentage_discount== data.original_price else 'Failed']