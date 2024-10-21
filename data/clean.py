import pandas as pd

# Load the CSV files
drugs_descriptions = pd.read_csv("data/drugs_desc.csv")
drugs_side_effects = pd.read_csv("data/drugs_subs_sides.csv")

# Merge the DataFrames
merged_df = pd.merge(
    drugs_descriptions,
    drugs_side_effects,
    left_on="drug_name",  # Adjust as necessary
    right_on="name",      # Adjust as necessary
    how="outer"
)

# Melt the DataFrame to combine side effects into one column
melted_df = merged_df.melt(
    id_vars=['drug_name', 'medical_condition', 'medical_condition_description', 'activity', 'rx_otc', 'pregnancy_category', 'csa', 'alcohol', 'rating', 'no_of_reviews', 'medical_condition_url', 'drug_link', 'id', 'name', 'substitute0', 'substitute1', 'substitute2', 'substitute3', 'substitute4'],
    value_vars=[f'sideEffect{i}' for i in range(42)],  # Adjust as necessary
    var_name='side_effect_num',
    value_name='side_effect'
)

# Drop rows where side_effect is NaN
melted_df = melted_df.dropna(subset=['side_effect'])

# Check data types
print(melted_df.dtypes)

# Group and Combine Side Effects
try:
    combined_df = (
        melted_df.groupby(['drug_name', 'medical_condition', 'medical_condition_description', 'activity', 'rx_otc', 'pregnancy_category', 'csa', 'alcohol', 'rating', 'no_of_reviews', 'medical_condition_url', 'drug_link', 'id', 'name', 'substitute0', 'substitute1', 'substitute2', 'substitute3', 'substitute4'])
        .agg({
            'side_effect': lambda x: ', '.join(x.unique())
        })
        .reset_index()
    )
    
    # Rename the combined column if necessary
    combined_df.rename(columns={'side_effect': 'combined_side_effects'}, inplace=True)

    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv("data/combined_drugs_data.csv", index=False)

except Exception as e:
    print(f"Error during aggregation: {e}")

# Display the final DataFrame
print(combined_df)
