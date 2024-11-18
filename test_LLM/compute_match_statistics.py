import pandas as pd

def compute_match_percentages(match_product_csv_path):
    # Load the match_product_csv into a DataFrame
    df = pd.read_csv(match_product_csv_path)
    
    # Initialize results dictionary
    results = {}
    
    # Define conditions
    conditions = {
        # Modify to count when both values are null as a match
        "original_price_match": (
            (df["original_price"] == df["match_original_price"]) | 
            (df["original_price"].isna() & df["match_original_price"].isna())
        ),
        # Modify to count when both values are null as a match
        "discount_price_match": (
            (df["discount_price"].isna() & df["match_discount_price"].isna()) |
            (df["discount_price"] == df["match_discount_price"]) 
            
        ),
        # Ensure discount rate is not null and equal
        "discount_rate_match": (
            (df["discount_rate"].isna() & df["match_discount_rate"].isna()) |
            (df["discount_rate"].notnull() 
            & df["match_discount_rate"].notnull() 
            & (abs(df["discount_rate"] - df["match_discount_rate"]) <= 0.05))
        ),
        # Both original price and discount price need to match
        "price_and_discount_match": (
            ((df["original_price"] == df["match_original_price"]) | 
             (df["original_price"].isna() & df["match_original_price"].isna())) &
            ((df["discount_price"] == df["match_discount_price"]) | 
             (df["discount_price"].isna() & df["match_discount_price"].isna()))
        ),
        # Category match
        "category_match": (df["category"] == df["match_category"]),
    }
    
    # Compute percentages for the whole table
    total_rows = len(df)
    overall_percentages = {
        condition: (condition_filter.sum() / total_rows) * 100
        for condition, condition_filter in conditions.items()
    }
    results["overall"] = overall_percentages
    
    # Compute percentages for each supermarket
    supermarkets = df["supermarket"].unique()
    results["by_supermarket"] = {}
    
    for supermarket in supermarkets:
        supermarket_df = df[df["supermarket"] == supermarket]
        supermarket_total_rows = len(supermarket_df)
        
        percentages = {
            condition: (condition_filter[supermarket_df.index].sum() / supermarket_total_rows) * 100
            for condition, condition_filter in conditions.items()
        }
        results["by_supermarket"][supermarket] = percentages
    
    # Convert results to DataFrame for readability
    overall_df = pd.DataFrame.from_dict(overall_percentages, orient="index", columns=["Percentage"])
    overall_df.index.name = "Condition"
    
    by_supermarket_df = pd.DataFrame.from_dict(results["by_supermarket"], orient="index")
    by_supermarket_df.index.name = "Supermarket"
    
    return overall_df, by_supermarket_df

# Example Usage
match_product_csv_path = 'test_LLM/matched_products_with_algo.csv'
overall_df, by_supermarket_df = compute_match_percentages(match_product_csv_path)

print("Overall Percentages:")
print(overall_df)

print("\nPercentages by Supermarket:")
print(by_supermarket_df)

# Save the overall percentages DataFrame to a CSV file
overall_df.to_csv('test_LLM/overall_percentages.csv', index=False)

# Save the by supermarket percentages DataFrame to a CSV file
by_supermarket_df.to_csv('test_LLM/by_supermarket_percentages.csv', index=False)
