import pandas as pd
import os

# Channel data with website links
channel_data = {
    'Channel': [
        'A&E', 'ABC', 'Acorn', 'Adult Swim', 'ALLBLK', 'AMC', 'BET', 'BET+', 
        'Bravo', 'BritBox', 'CBS', 'CNN', 'Comedy Central', 'Discovery Channel',
        'Disney Channel', 'Disney Junior', 'Disney+', 'E!', 'Food Network', 'FOX',
        'Freeform', 'FX', 'FXX', 'FYI', 'GAC Family', 'Hallmark Channel', 'HBO',
        'HGTV', 'History', 'Hulu', 'Investigation Discovery', 'Lifetime',
        'LMN - Lifetime Movies Network', 'Magnolia Network', 'Max', 'MGM+', 'MTV',
        'Nat Geo', 'Nat Geo Wild', 'NBC', 'Netflix', 'OWN', 'Oxygen', 'Paramount+',
        'PBS', 'PBS Kids', 'Peacock', 'Prime Video', 'RFD-TV', 'Shudder', 'Starz',
        'Sundance Channel', 'TBS', 'The CW', 'TLC', 'Tubi', 'USA Network', 'We TV'
    ],
    'Website': [
        'aetv.com', 'abc.com', 'acorn.tv', 'adultswim.com', 'allblk.tv', 'amc.com',
        'bet.com', 'bet.com', 'bravotv.com', 'britbox.com', 'cbs.com', 'cnn.com',
        'cc.com', 'discovery.com', 'disneyplus.com', 'N/A', 'disneyplus.com',
        'eonline.com', 'foodnetwork.com', 'fox.com', 'freeform.com', 'N/A', 'N/A',
        'fyi.tv', 'gactv.com', 'hallmarkchannel.com', 'hbo.com', 'hgtv.com',
        'history.com', 'hulu.com', 'investigationdiscovery.com', 'mylifetime.com',
        'mylifetime.com', 'magnolia.com', 'max.com', 'mgmplus.com', 'mtv.com',
        'nationalgeographic.com', 'natgeotv.com', 'nbc.com', 'netflix.com',
        'oprah.com', 'oxygen.com', 'paramountplus.com', 'pbs.org', 'pbskids.org',
        'peacocktv.com', 'primevideo.com', 'rfdtv.com', 'shudder.com', 'starz.com',
        'sundancetv.com', 'tbs.com', 'cwtv.com', 'tlc.com', 'tubi.tv',
        'usanetwork.com', 'wetv.com'
    ],
    'Country': [
        'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US',
        'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US',
        'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US',
        'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US',
        'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US', 'US'
    ]
}

# Create DataFrame
df = pd.DataFrame(channel_data)

# Save to Excel file
excel_path = 'channel_database.xlsx'
df.to_excel(excel_path, index=False, sheet_name='Channels')

print(f"Channel database created successfully: {excel_path}")
print(f"Total channels: {len(df)}")
print("\nFirst 10 channels:")
print(df.head(10).to_string())