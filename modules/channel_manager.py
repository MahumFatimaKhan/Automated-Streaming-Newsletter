import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class ChannelManager:
    """Manage channel database and website links."""
    
    def __init__(self, database_path='channel_database.xlsx'):
        """Initialize with channel database."""
        self.database_path = database_path
        self.channels_df = self._load_database()
        
    def _load_database(self):
        """Load channel database from Excel file."""
        try:
            if os.path.exists(self.database_path):
                df = pd.read_excel(self.database_path, sheet_name='Channels')
                # Convert channel names to lowercase for case-insensitive matching
                df['Channel_Lower'] = df['Channel'].str.lower()
                logger.info(f"Loaded {len(df)} channels from database")
                return df
            else:
                logger.warning(f"Channel database not found at {self.database_path}")
                # Create empty DataFrame with required columns
                return pd.DataFrame(columns=['Channel', 'Website', 'Country', 'Channel_Lower'])
        except Exception as e:
            logger.error(f"Error loading channel database: {str(e)}")
            return pd.DataFrame(columns=['Channel', 'Website', 'Country', 'Channel_Lower'])
    
    def _save_database(self):
        """Save updated channel database to Excel file."""
        try:
            # Remove the temporary lowercase column before saving
            save_df = self.channels_df.drop(columns=['Channel_Lower'], errors='ignore')
            save_df.to_excel(self.database_path, index=False, sheet_name='Channels')
            logger.info(f"Updated channel database saved to {self.database_path}")
        except Exception as e:
            logger.error(f"Error saving channel database: {str(e)}")
    
    def get_channel_website(self, channel_name):
        """Get website URL for a channel."""
        # Clean and normalize channel name
        channel_clean = channel_name.strip().lower()
        
        # Only look for exact match - no partial matching to avoid wrong channels
        match = self.channels_df[self.channels_df['Channel_Lower'] == channel_clean]
        
        if not match.empty:
            website = match.iloc[0]['Website']
            channel_display = match.iloc[0]['Channel']
            
            if website and website != 'N/A':
                # Ensure it has https:// prefix
                if not website.startswith(('http://', 'https://')):
                    website = f"https://{website}"
                
                logger.debug(f"Using direct website URL for {channel_display}: {website}")
                return website, None
            else:
                logger.warning(f"Channel '{channel_name}' has no website defined")
                return None, channel_display
        
        # No match found - channel needs to be added
        logger.info(f"Channel '{channel_name}' not found in database - needs to be added")
        return None, channel_name
    
    def add_channel_to_database(self, channel_name, website, country='US'):
        """Add a new channel to the database."""
        try:
            # Check if channel already exists
            channel_lower = channel_name.strip().lower()
            if not self.channels_df[self.channels_df['Channel_Lower'] == channel_lower].empty:
                # Update existing channel
                self.channels_df.loc[self.channels_df['Channel_Lower'] == channel_lower, 'Website'] = website
                self.channels_df.loc[self.channels_df['Channel_Lower'] == channel_lower, 'Country'] = country
                logger.info(f"Updated channel '{channel_name}' with website '{website}'")
            else:
                # Add new channel
                new_row = pd.DataFrame({
                    'Channel': [channel_name],
                    'Website': [website],
                    'Country': [country],
                    'Channel_Lower': [channel_lower]
                })
                self.channels_df = pd.concat([self.channels_df, new_row], ignore_index=True)
                logger.info(f"Added new channel '{channel_name}' with website '{website}'")
            
            # Save updated database
            self._save_database()
            return True
            
        except Exception as e:
            logger.error(f"Error adding channel to database: {str(e)}")
            return False
    
    def get_all_channels(self):
        """Get list of all channels in database."""
        return self.channels_df['Channel'].tolist()
    
    def search_channel(self, query):
        """Search for channels matching a query."""
        query_lower = query.lower()
        matches = self.channels_df[
            self.channels_df['Channel_Lower'].str.contains(query_lower, na=False)
        ]
        return matches['Channel'].tolist()


# Example usage function
def test_channel_manager():
    """Test the channel manager functionality."""
    manager = ChannelManager()
    
    # Test with known channels
    test_channels = ['A&E', 'Lifetime', 'HBO', 'Netflix']
    
    print("Testing Channel Website Retrieval\n" + "="*50)
    
    for channel in test_channels:
        website, missing = manager.get_channel_website(channel)
        if website:
            print(f"\n{channel}:")
            print(f"Website URL: {website}")
        else:
            print(f"\n{channel}: Missing website - needs to be added to database")
    
    print("\n" + "="*50)
    print("Test complete")


if __name__ == "__main__":
    test_channel_manager()