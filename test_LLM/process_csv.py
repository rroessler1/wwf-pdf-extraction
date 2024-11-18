import pandas as pd
from datetime import datetime
import re

extracted_folder_mapping = {
    'ALDI Flipbook_KW16-2023-DE (20.-26.04)': ('Aldi', 16),
    'ALDI Flipbook_KW17-2023-DE (27. - 03.05.)': ('Aldi', 17),
    'ALDI Flipbook_KW18-2023-FR': ('Aldi', 18),
    'ALDI Flipbook_KW19-2023-DE': ('Aldi', 19),
    'Aldi KW 20': ('Aldi', 20),
    'Coop Aktionen KW 20': ('Coop', 20),
    'COOP AM_20230502_ZZ': ('Coop', 18),
    'COOP AM_AKMA_W19_2023_DE_ZZ--SHORTTERM': ('Coop', 19),
    'Coop Zeitung KW 18': ('Coop', 18),
    'Coop Zeitung KW 19': ('Coop', 19),
    'Coop zeitung KW 20': ('Coop', 20),
    'Denner (KW 17)': ('Denner', 17),
    'Denner (KW 18)': ('Denner', 18),
    'Prospekte 4. Woche (15.05.- 22.05.) KW 20': ('Denner', 20),
    'Denner (KW19)': ('Denner', 19),
    'Lidl KW 20': ('Lidl', 20),
    'LIDL-AKTUELL-KW17-27-4-3-5-06': ('Lidl', 17),
    'LIDL-AKTUELL-KW18-4-5-10-5-04': ('Lidl', 18),
    'LIDL-AKTUELL-KW19-11-5-16-5-02': ('Lidl', 19),
    'LIDL-AKTUELL-KW20-17-5-24-5-06': ('Lidl', 20),
    'Migros Magazin KW 18': ('Migros', 18),
    'Migros-Magazin-17-2023-d-ZH': ('Migros', 17),
    'Migros-Magazin-19-2023-d-ZH': ('Migros', 19),
    'Migros-Magazin-20-2023-d-ZH': ('Migros', 20),
    'Migros-Wochenflyer-17-2023-d-ZH': ('Migros', 17),
    'Migros-Wochenflyer-20-2023-d-ZH': ('Migros', 20),
    'Volg (KW17)': ('Volg', 17),
    'Volg_Wochenaktionen_KW18': ('Volg', 18),
    'Volg_Wochenaktionen_KW20': ('Volg', 20),
    'W17_2023_COOP': ('Coop', 17),
    'Woche 17 Coop Zeitung': ('Coop', 17)
}

ground_truth_to_validation_map = {
    'Produkt': 'product_name',
    'Originalpreis': 'original_price',
    'Rabattpreis': 'discount_price',
    'Prozent Rabatt': 'percentage_discount',
    'Rabatt-Datum': 'discounted_time',
    'Supermarkt': 'supermarket',
    'Sorten': 'category'
}

extracted_to_validation_map = {
    'final_product_name': 'product_name',
    'final_original_price': 'original_price',
    'final_discount_price': 'discount_price',
    'final_percentage_discount': 'percentage_discount',
    'extracted_folder': 'pdf_name',
    'final_category': 'category'
}

def keep_only_first_tab(input_xlsx):
    # Load only the first sheet of the Excel file
    with pd.ExcelFile(input_xlsx) as xlsx:
        first_sheet_name = xlsx.sheet_names[0]  # Get the name of the first sheet
        first_sheet_df = pd.read_excel(xlsx, sheet_name=first_sheet_name)  # Load the first sheet as a DataFrame

    return first_sheet_df

def read_csv(input_csv):
    df = pd.read_csv(input_csv)
    return df

def synchronize_csv(df, name_mapping):

    # Create a new DataFrame with the required English column names
    transformed_df = pd.DataFrame()

    for name_before, name_after in name_mapping.items():
        transformed_df[name_after] = df[name_before].where(df[name_before].notna(), None)

    return transformed_df

def add_supermarket_and_discount_time(df, folder_mapping):
    # Add two new columns using the folder_mapping
    supermarkets = []
    discount_times = []

    for folder in df['pdf_name']:
        if folder in folder_mapping:
            supermarket, discount_time = folder_mapping[folder]
        else:
            supermarket, discount_time = None, None
        supermarkets.append(supermarket)
        discount_times.append(discount_time)

    df['supermarket'] = supermarkets
    df['discount_interval'] = discount_times
    df.drop(columns=['pdf_name'], inplace=True)
    return df

def parse_date(day, month):
    """Helper function to parse day and month into a datetime object."""
    return datetime.strptime(f"{day}.{month}", "%d.%m")

def is_within_interval(start_day, start_month, end_day, end_month, discount_days):
    """Check if the discount interval falls within the mapped interval."""
    start_date = parse_date(start_day, start_month)
    end_date = parse_date(end_day, end_month)
    discount_start = parse_date(discount_days[0], discount_days[1])
    discount_end = parse_date(discount_days[2], discount_days[3])
    return start_date <= discount_start <= end_date and start_date <= discount_end <= end_date

def extract_four_numbers(time_interval):
    numbers = []
    current_number = ""
    
    for char in time_interval:
        if char.isdigit():
            current_number += char
        elif current_number:
            numbers.append(int(current_number))
            current_number = ""
    
    # Append the last number if there is one
    if current_number:
        numbers.append(int(current_number))
    
    # Ensure exactly four numbers are returned
    if len(numbers) == 4:
        return numbers
    else:
        raise ValueError(f"Expected 4 numbers in the input, but got {len(numbers)}: {numbers}")
    
def map_discount_interval(df):
    def get_week_from_date_interval(numbers, supermarket):
        # Mapping rules for each supermarket
        mapping = {
            'Aldi': [(20, 4, 26, 4, 16), (27, 4, 3, 5, 17), (4, 5, 10, 5, 18), (11, 5, 16, 5, 19), (17, 5, 24, 5, 20)],
            'Lidl': [(20, 4, 26, 4, 16), (27, 4, 3, 5, 17), (4, 5, 10, 5, 18), (11, 5, 16, 5, 19), (17, 5, 24, 5, 20)],
            'Coop': [(22, 4, 29, 4, 17), (1, 5, 7, 5, 18), (9, 5, 14, 5, 19), (15, 5, 21, 5, 20)],
            'Denner': [(25, 4, 1, 5, 17), (2, 5, 8, 5, 18), (9, 5, 15, 5, 19), (16, 5, 22, 5, 20)],
            'Migros': [(25, 4, 1, 5, 17), (2, 5, 8, 5, 18), (9, 5, 15, 5, 19), (16, 5, 22, 5, 20)],
            'Volg': [(24, 4, 29, 4, 17), (1, 5, 6, 5, 18), (8, 5, 13, 5, 19), (15, 5, 20, 5, 20)]
        }
        for interval in mapping.get(supermarket, []):
            if is_within_interval(interval[0], interval[1], interval[2], interval[3], numbers):
                return interval[4]
        return None  # Return None if no matching week is found

    discount_intervals = []
    for _, row in df.iterrows():
        if pd.notnull(row['discounted_time']) and pd.notnull(row['supermarket']):
            try:
                # Extract the four numbers from the discount_time column
                numbers = extract_four_numbers(row['discounted_time'])
                # Map the numbers to a week based on the supermarket
                week = get_week_from_date_interval(numbers, row['supermarket'])
                discount_intervals.append(week)
            except ValueError as e:
                print(f"Error processing row: {row['discounted_time']}, {e}")
                discount_intervals.append(None)
        else:
            discount_intervals.append(None)

    df['discount_interval'] = discount_intervals
    return df

def clean_prices(df):
    def extract_price(value):
        """Extract the numeric price from a string."""
        if pd.isnull(value):
            return None
        value = str(value).strip()
        price = []
        started = False
        for char in value:
            if char.isdigit() or (char == '.' and started):
                price.append(char)
                started = True
            elif started:
                break
        return float(''.join(price)) if price else None

    def process_row(row):
        """Process a single row based on the described logic."""
        original_price = extract_price(row['original_price'])
        discounted_price = extract_price(row['discount_price'])
        
        # If discounted_price is null and original_price is not null
        if discounted_price is None and original_price is not None:
            discounted_price = original_price
            original_price = None
        
        # If prices are equal, keep only discounted_price
        if discounted_price == original_price:
            original_price = None
        
        return pd.Series([original_price, discounted_price])

    # Apply processing to each row
    df[['original_price', 'discount_price']] = df.apply(process_row, axis=1)
    return df

def filter_category(df):
    filtered_df = df[df['category'] != "Kein Grillprodukt"]
    return filtered_df

def clean_category(df):
    df['category'] = df['category'].apply(lambda x: re.sub(r'Grillfleisch \((.*?)\)', r'\1', x) if isinstance(x, str) else x)
    return df

def outfile_csv(df, output_file):
    df.to_csv(output_file, index=False, encoding='utf-8')

def process_extracted_csv(input_csv, name_mapping, output_file):
    df = read_csv(input_csv)
    df = synchronize_csv(df, name_mapping)
    df = add_supermarket_and_discount_time(df, extracted_folder_mapping)
    df = filter_category(df)
    df = clean_category(df)
    df = clean_prices(df)
    outfile_csv(df, output_file)

def process_ground_truth_csv(input_csv, name_mapping, output_file):
    df = read_csv(input_csv)
    df = synchronize_csv(df, name_mapping)
    df = map_discount_interval(df)
    outfile_csv(df, output_file)



extracted_csv = 'test_LLM/pdf-files/results.csv'
ground_truth_csv = 'test_LLM/2023_ground_truth.csv'
output_extracted = 'test_LLM/new_extracted.csv'
output_ground_truth = 'test_LLM/new_ground_truth.csv'

process_extracted_csv(extracted_csv, extracted_to_validation_map, output_extracted)
process_ground_truth_csv(ground_truth_csv, ground_truth_to_validation_map, output_ground_truth)

