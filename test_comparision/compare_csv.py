import pandas as pd

def compare_and_save_mismatches(ground_truth_path, extracted_path, output_path):
    # Load the CSV files into dataframes
    ground_truth_df = pd.read_csv(ground_truth_path)
    extracted_df = pd.read_csv(extracted_path)
    
    # Ensure both dataframes have the required columns
    required_columns = ["product_name", "original_price", "discount_price", "percentage_discount", "Category"]
    for col in required_columns:
        if col not in ground_truth_df.columns or col not in extracted_df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Merge dataframes on the "product_name" column to align matching products
    comparison_df = pd.merge(ground_truth_df, extracted_df, on="product_name", suffixes=('_ground_truth', '_extracted'))
    
    # Check for mismatches in the specified columns
    mismatches = []
    for _, row in comparison_df.iterrows():
        discrepancies = {}
        error_types = []

        for col in ["original_price", "discount_price", "percentage_discount", "Category"]:
            gt_col = f"{col}_ground_truth"
            ext_col = f"{col}_extracted"

            # Check for mismatch cases
            if pd.notna(row[gt_col]) and pd.notna(row[ext_col]) and row[gt_col] != row[ext_col]:
                discrepancies[col] = {"ground_truth": row[gt_col], "extracted": row[ext_col]}
                error_types.append(f"Wrong {col}")
            elif pd.notna(row[gt_col]) and pd.isna(row[ext_col]):  # Ground truth is not NaN but extracted is NaN
                discrepancies[col] = {"ground_truth": row[gt_col], "extracted": row[ext_col]}
                error_types.append(f"Missing {col}")
            elif pd.isna(row[gt_col]) and pd.notna(row[ext_col]):  # Ground truth is NaN but extracted is not NaN
                discrepancies[col] = {"ground_truth": row[gt_col], "extracted": row[ext_col]}
                error_types.append(f"Redundant {col}")
        
        if discrepancies:  # Only add rows with discrepancies
            mismatch_entry = {"product_name": row["product_name"]}
            
            # Add ground_truth and extracted values for each discrepancy found
            for col in ["original_price", "discount_price", "percentage_discount", "Category"]:
                if col in discrepancies:
                    mismatch_entry[f"{col}_ground_truth"] = discrepancies[col]["ground_truth"]
                    mismatch_entry[f"{col}_extracted"] = discrepancies[col]["extracted"]
                else:
                    mismatch_entry[f"{col}_ground_truth"] = None
                    mismatch_entry[f"{col}_extracted"] = None
            
            # Join all error types for this row as a single string in "error_type"
            mismatch_entry["error_type"] = "; ".join(error_types)
            mismatches.append(mismatch_entry)
    
    # Convert mismatches to a DataFrame for easy readability
    mismatch_df = pd.DataFrame(mismatches)
    
    # Save mismatches as a CSV file (only mismatched rows)
    mismatch_df.to_csv(output_path, index=False)


ground_truth_path = 'test_comparision/ground_truth_messy.csv'
extracted_path = 'test_comparision/extracted_messy.csv'
output_path = 'test_comparision/mismatch_report.csv'  

compare_and_save_mismatches(ground_truth_path, extracted_path, output_path)
