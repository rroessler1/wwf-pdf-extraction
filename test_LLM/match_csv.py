import pandas as pd
from scipy.spatial.distance import cosine
import json

with open('test_LLM/similarity_dict.json', 'r', encoding='utf-8') as f:
    similarity_dict = json.load(f)

# Helper function to clean product names
def clean_product_name(name):
    if not name or isinstance(name, float):
        return 'No name'
    # List of words to remove from product names
    stopwords = ['Coop', 'Lidl', 'Aldi', 'Migros', 'Volg', 'Denner']
    # name = name.lower()  # Convert to lowercase
    cleaned_name = []
    
    # Iterate through each character in the string
    for char in name:
        # Keep the character if it's a letter or a space, otherwise replace with space
        if char.isalpha() or char.isspace():
            cleaned_name.append(char)
        else:
            cleaned_name.append(' ')
    
    # Join the list into a string and remove extra spaces
    cleaned_name = ''.join(cleaned_name).strip()
    
    # Remove stopwords from the list of words
    words = cleaned_name.split()
    words = [word.lower() for word in words if word not in stopwords]
    
    return ' '.join(words)

def compute_discount_rate(original_price, discount_price):
    if not original_price or not discount_price:
        return -1
    return 1 - discount_price / original_price

# Helper function to compute Jaccard similarity
def jaccard_similarity(str1, str2):
    words1 = set(str1.split())
    words2 = set(str2.split())
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union != 0 else 0


def match_product_names(ground_truth_df, extracted_df, threshold=0.9):
    def compute_jaccard_score(str1, str2):
        """Helper function to compute Jaccard similarity."""
        set1, set2 = set(str1.split()), set(str2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union != 0 else 0

    df3_data = []

    for _, t1_row in ground_truth_df.iterrows():
        t1_name = t1_row["product_name"]
        t1_supermarket = t1_row["supermarket"]
        t1_discount_interval = t1_row.get("discount_interval", None)
        t1_original_price = t1_row["original_price"]
        t1_discount_price = t1_row["discount_price"]

        # Filter candidates from extracted_df based on supermarket and discount interval
        candidates = extracted_df[
            (extracted_df["supermarket"] == t1_supermarket)
            & ((extracted_df["discount_interval"] == t1_discount_interval) | extracted_df["discount_interval"].isnull())
        ]

        # Step 1: Check for exact name match
        exact_name_matched = candidates[candidates["product_name"] == t1_name]

        if not exact_name_matched.empty:
            # Use the exact name match as the match
            best_match = exact_name_matched.iloc[0]  # Taking the first match if multiple exist
        else:
            # Step 2: Look for candidates with the same original_price or discount_price
            price_matched = candidates[
                ((candidates["original_price"].notnull()) & (t1_original_price is not None) & (candidates["original_price"] == t1_original_price))
        | ((candidates["discount_price"].notnull()) & (t1_discount_price is not None) & (candidates["discount_price"] == t1_discount_price))
            ]

            best_match = None
            # highest_jaccard = 0
            # highest_similarity = 0

            if not price_matched.empty:
                # Step 1: Check Jaccard or similarity_dict for price-matched candidates
                for _, t2_row in price_matched.iterrows():
                    t2_name = t2_row["product_name"]
                    jaccard_score = compute_jaccard_score(t1_name, t2_name)

                    # Check Jaccard or if in similarity_dict
                    if (
                        jaccard_score > 0
                        or t2_name in similarity_dict.get(t1_name, {})
                    ):
                        best_match = t2_row
                        break  # Found a match, stop checking further
            else:
                # Step 2: General candidates based on Jaccard and similarity_dict
                potential_matches = []
                for _, t2_row in candidates.iterrows():
                    t2_name = t2_row["product_name"]
                    jaccard_score = compute_jaccard_score(t1_name, t2_name)
                    similarity_score = similarity_dict.get(t1_name, {}).get(t2_name, 0)

                    # Add to potential matches if meets criteria
                    if jaccard_score > 0 or similarity_score >= threshold:
                        potential_matches.append(
                            (t2_row, jaccard_score, similarity_score)
                        )

                if potential_matches:
                    # Sort matches by Jaccard > 0 (first priority) and highest similarity
                    potential_matches.sort(
                        key=lambda x: (x[1] > 0, x[1], x[2]), reverse=True
                    )
                    best_match = potential_matches[0][0]  # Select the best candidate

        # Add the best match to df3_data if found
        if best_match is not None:
            df3_data.append(
                {
                    "product_name": t1_name,
                    "supermarket": t1_supermarket,
                    "original_price": t1_original_price,
                    "discount_price": t1_discount_price,
                    "category": t1_row["category"],
                    'discount_rate': compute_discount_rate(t1_row['original_price'], t1_row['discount_price']),
                    "week": t1_discount_interval,
                    "match_product_name": best_match["product_name"],
                    "match_supermarket": best_match["supermarket"],
                    "match_original_price": best_match["original_price"],
                    "match_discount_price": best_match["discount_price"],
                    "match_category": best_match["category"],
                    'match_discount_rate': compute_discount_rate(best_match['original_price'], best_match['discount_price']),
                    "match_week": best_match["discount_interval"]
                }
            )

    # Create DataFrame from matches
    df3 = pd.DataFrame(df3_data)
    return df3

# Example usage:
new_ground_truth = pd.read_csv('test_LLM/new_ground_truth.csv')
new_extracted = pd.read_csv('test_LLM/new_extracted.csv')

df3 = match_product_names(new_ground_truth, new_extracted, 0.7)

# Output the result to a CSV file
df3.to_csv('test_LLM/matched_products_with_algo.csv', index=False, encoding='utf-8')
