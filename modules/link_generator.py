import re
from urllib.parse import quote
from slugify import slugify
import logging

logger = logging.getLogger(__name__)

class LinkGenerator:
    """Generate clean URLs for streaming services."""
    
    def __init__(self):
        pass
    
    def normalize_website_url(self, website):
        """Normalize and clean website URL."""
        if not website:
            return "#"
        
        # Clean and extract domain from website URL
        website_clean = re.sub(r'^https?://', '', website)
        
        # Remove www
        website_clean = re.sub(r'^www\.', '', website_clean)
        
        # Remove path and query parameters
        website_clean = website_clean.split('/')[0]
        website_clean = website_clean.split('?')[0]
        
        # Handle specific streaming service domains
        domain_mappings = {
            'hbomax.com': 'max.com',
            'disneyplus.com': 'disneyplus.com',
            'netflix.com': 'netflix.com',
            'hulu.com': 'hulu.com',
            'primevideo.com': 'primevideo.com',
            'peacocktv.com': 'peacocktv.com',
            'paramountplus.com': 'paramountplus.com',
            'tv.apple.com': 'tv.apple.com',
            'plus.espn.com': 'plus.espn.com',
            'servustv.com': 'servustv.com'
        }
        
        # Return mapped domain or cleaned version
        for pattern, replacement in domain_mappings.items():
            if pattern in website_clean:
                return f"https://{replacement}"
        
        # Ensure https:// prefix
        if not website_clean.startswith(('http://', 'https://')):
            website_clean = f"https://{website_clean}"
        
        return website_clean
    
    def normalize_channel_name(self, channel):
        """Normalize channel name for consistent formatting."""
        if not channel:
            return "unknown"
        
        # Remove special characters and spaces
        channel_clean = re.sub(r'[^\w\s-]', '', channel)
        channel_clean = re.sub(r'[-\s]+', '-', channel_clean)
        
        # Convert to slug format
        channel_slug = slugify(channel_clean)
        
        # Handle specific channel mappings
        channel_mappings = {
            'hbo-max': 'HBO Max',
            'disney-plus': 'Disney+',
            'disney': 'Disney',
            'netflix': 'Netflix',
            'hulu': 'Hulu',
            'amazon-prime': 'Prime Video',
            'prime-video': 'Prime Video',
            'peacock': 'Peacock',
            'paramount-plus': 'Paramount+',
            'paramount': 'Paramount',
            'apple-tv': 'Apple TV',
            'espn': 'ESPN',
            'espn-plus': 'ESPN+',
            'showtime': 'Showtime',
            'starz': 'Starz',
            'amc': 'AMC',
            'amc-plus': 'AMC+',
            'discovery': 'Discovery',
            'discovery-plus': 'Discovery+',
            'servustv': 'ServusTV',
            'bbc': 'BBC',
            'fox': 'FOX',
            'nbc': 'NBC',
            'abc': 'ABC',
            'cbs': 'CBS'
        }
        
        # Return mapped channel or original
        return channel_mappings.get(channel_slug, channel)


# Example usage function
def test_link_generator():
    """Test the link generator utility."""
    generator = LinkGenerator()
    
    # Test URL normalization
    test_urls = [
        'https://www.netflix.com',
        'http://hbomax.com/watch',
        'disneyplus.com',
        'www.hulu.com/stream'
    ]
    
    print("Testing URL Normalization\n" + "="*50)
    
    for url in test_urls:
        normalized = generator.normalize_website_url(url)
        print(f"{url} -> {normalized}")
    
    print("\n" + "="*50)
    
    # Test channel normalization
    test_channels = ['HBO Max', 'disney+', 'prime-video', 'ESPN+']
    
    print("\nTesting Channel Normalization\n" + "="*50)
    
    for channel in test_channels:
        normalized = generator.normalize_channel_name(channel)
        print(f"{channel} -> {normalized}")
    
    print("\n" + "="*50)
    print("Test complete")


if __name__ == "__main__":
    test_link_generator()