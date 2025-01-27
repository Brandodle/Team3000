import pandas as pd
import string

# Function to clean and preprocess text
def clean_text(text):
    """Remove punctuation, extra spaces, and lowercase the text."""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = ' '.join(text.split())  # Remove extra spaces
    return text

# Function to validate the data
def validate_data(df):
    # Initialize the validation log with the appropriate columns
    validation_log = []

    # 1. Validate for missing values in 'Text' column
    missing_values = df[df['Text'].isna()]
    if not missing_values.empty:
        missing_value_errors = missing_values.apply(lambda row: {
            'Error Type': 'Missing Value',
            'Description': f"Missing value found in 'Text' column",
            'Row Number': row.name + 2  # Add 2 to row number (Excel row 1 is header)
        }, axis=1)
        validation_log.extend(missing_value_errors)

    # 2. Validate for duplicates (exact duplicates in 'Text' column)
    duplicates = df[df.duplicated(subset=['Text'], keep=False)]
    if not duplicates.empty:
        duplicate_errors = duplicates.apply(lambda row: {
            'Error Type': 'Duplicate Entry',
            'Description': f"Duplicate entry found in 'Text' column: {row['Text']}",
            'Row Number': row.name + 2  # Add 2 to row number (Excel row 1 is header)
        }, axis=1)
        validation_log.extend(duplicate_errors)

    # 3. Validate for subset duplicates (i.e., one text is a subset of another)
    cleaned_texts = df['Text'].apply(clean_text).values

    for i in range(len(cleaned_texts)):
        for j in range(i + 1, len(cleaned_texts)):
            text_i = cleaned_texts[i]
            text_j = cleaned_texts[j]
            
            # Check if one text is a subset of another
            if text_i in text_j or text_j in text_i:
                validation_log.append({
                    'Error Type': 'Subset Duplicate',
                    'Description': f"Text in row {i+2} is a subset of text in row {j+2}" if text_i in text_j else f"Text in row {j+2} is a subset of text in row {i+2}",
                    'Row Number': f"{i+2}, {j+2}"  # Add 2 to row number (Excel row 1 is header)
                })

    # Convert the list of validation errors to a DataFrame
    validation_log_df = pd.DataFrame(validation_log, columns=["Error Type", "Description", "Row Number"])
    return validation_log_df

# Function to combine text based on the first column
def combine_text_based_on_column1(df):
    # Validate the data
    validation_log_df = validate_data(df)
    if not validation_log_df.empty:
        print("Validation Errors Found:")
        print(validation_log_df)
    
    # Group by the first column and concatenate the 'Text' (second column)
    df_combined = df.groupby('Column1')['Text'].apply(lambda x: ' '.join(x)).reset_index()
    return df_combined

# Example usage
data = {
    'Column1': ['1.pdf', '1.pdf'],
    'Text': [
        "Pristina Airport – Possible administrative irregularity regarding tender procedures involving Vendor 1 and Vendor 2 Allegation",
        "Investigative details In his/her interviews conducted on 31st August and 14th September 2004, Vendor 1 and Vendor 2 Representative admitted that the fact that both Vendor 1 and Vendor 2 took part together in three Airport tenders put other competitors at a disadvantage, but alleged both companies have never exchanged information with regard to the price offers."
    ]
}

df = pd.DataFrame(data)

# Call the function to combine text based on the first column
df_combined = combine_text_based_on_column1(df)

# Display the result
print(df_combined)
