import pandas as pd
from collections import Counter
import random

from settings.settings import NUMBER_OF_CHATGPT_VALIDATIONS, EXTRACTED_DATA_COLUMNS


def determine_final_column_and_confidence(row:pd.Series, column_name:str) -> (str, float):
    # Get all validation values in a list
    validation_columns = [f'validated{i + 1}_{column_name}' for i in range(NUMBER_OF_CHATGPT_VALIDATIONS)]
    validation_values = [row[col] for col in validation_columns]

    # Count occurrences of each value
    counts = Counter(validation_values)     # TODO handle NaN values better
    most_common_value, max_count = counts.most_common(1)[0]

    # Check if there is a tie
    tied_values = [val for val, count in counts.items() if count == max_count]

    if len(tied_values) == 1:
        final_value = most_common_value
    else:
        # Tie exists, check extracted_original_price
        if row[f'extracted_{column_name}'] in tied_values:
            final_value = row[f'extracted_{column_name}']
        else:
            final_value = random.choice(tied_values)  # Choose randomly if no match

    # Calculate confidence
    confidence = counts[final_value] / NUMBER_OF_CHATGPT_VALIDATIONS

    return final_value, confidence

def compare_validation(data: pd.DataFrame) -> None:
    """
    compares the values between the extraction and all validation steps
    :param data: dataframe with extracted data and validation data
    :return: None, since the original dataframe is edited
    """
    for column in EXTRACTED_DATA_COLUMNS:
        data[[f'final_{column}', f'confidence_{column}']] = data.apply(
            lambda row: pd.Series(determine_final_column_and_confidence(row, column)),
            axis=1
        )