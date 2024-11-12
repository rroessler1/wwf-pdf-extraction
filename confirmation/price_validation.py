import pandas as pd

def price_valudator(dataset):
    data = dataset.copy(deep=True)

    data.fillna(1)
    
    data['discount_price'] = data['discount_price'].replace('[^\d.]', '', regex=True).apply(lambda x:'1' if x=='' else x).astype(float)
    data['percentage_discount'] = data['percentage_discount'].replace('[^\d.]', '', regex=True).apply(lambda x:'1' if x=='' else x).astype(float)
    data['original_price'] = data['original_price'].replace('[^\d.]', '', regex=True).apply(lambda x:'1' if x=='' else x).astype(float)

    return ['Passed' if data.discount_price[i]/data.percentage_discount[i] - data.original_price[i] < 0.05 else 'Failed' for i in range(data.shape[0]) ]