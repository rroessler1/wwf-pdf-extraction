import pandas as pd

def price_valudator(data):
    data.fillna('1',inplace=True)
    data['discount_price'] = data['discount_price'].astype(float)
    data['percentage_discount'] = data['percentage_discount'].astype(float)
    data['original_price'] = data['original_price'].astype(float)
    
    return ['Passed' if data.discount_price/data.percentage_discount - data.original_price < 0.05 else 'Failed']