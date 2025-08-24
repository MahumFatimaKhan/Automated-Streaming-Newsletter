import pandas as pd

# Load the current database
df = pd.read_excel('channel_database.xlsx', sheet_name='Channels')

# Check if PBS already exists
if 'PBS' not in df['Channel'].values:
    # Add PBS channel
    new_row = pd.DataFrame({
        'Channel': ['PBS'],
        'Website': ['pbs.org'],
        'Country': ['US']
    })
    
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Sort by channel name for better organization
    df = df.sort_values('Channel').reset_index(drop=True)
    
    # Save back to Excel
    df.to_excel('channel_database.xlsx', index=False, sheet_name='Channels')
    print("Added PBS channel to database")
    
    # Verify it was added
    pbs_entries = df[df['Channel'].str.contains('PBS', case=False)]
    print("\nPBS-related channels now in database:")
    print(pbs_entries[['Channel', 'Website']].to_string())
else:
    print("PBS already exists in database")