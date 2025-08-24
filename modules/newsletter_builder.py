import logging
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from .channel_manager import ChannelManager

logger = logging.getLogger(__name__)

class NewsletterBuilder:
    """Build HTML newsletter from components."""
    
    def __init__(self):
        self.template = self._load_template()
        self.channel_manager = ChannelManager()
        self.missing_channels = []  # Track channels that need website info
    
    def build(self, banner_url: str, tagline: str, introduction: str, 
              content_items: List[Dict], date_range: Dict) -> str:
        """Build complete newsletter HTML."""
        try:
            # Group content by date
            grouped_content = self._group_by_date(content_items)
            
            # Generate content sections
            content_html = self._generate_content_sections(grouped_content)
            
            # Get month for title
            start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
            month_year = start_date.strftime('%B %Y')
            
            # Replace placeholders in template
            newsletter_html = self.template
            newsletter_html = newsletter_html.replace('{{TITLE}}', f'Streaming Updates for {month_year}')
            newsletter_html = newsletter_html.replace('{{BANNER_URL}}', banner_url)
            newsletter_html = newsletter_html.replace('{{TAGLINE}}', tagline)
            newsletter_html = newsletter_html.replace('{{INTRODUCTION}}', introduction)
            newsletter_html = newsletter_html.replace('{{CONTENT_SECTIONS}}', content_html)
            newsletter_html = newsletter_html.replace('{{CURRENT_YEAR}}', str(datetime.now().year))
            
            return newsletter_html
            
        except Exception as e:
            logger.error(f"Error building newsletter: {str(e)}")
            return self._get_error_template()
    
    def _load_template(self) -> str:
        """Load base HTML template."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        *, body {
            box-sizing: border-box;
        }
        
        @media only screen and (max-width: 600px) {
            .movie-list {
                width: 100% !important;
            }
            .movie-card {
                display: block !important;
            }
            .movie-card img {
                width: 90% !important;
                height: auto !important;
                margin-bottom: 15px !important;
                margin-right: 10px !important;
            }
            .movie-info {
                margin-left: 0 !important;
            }
            .add-to-calendar {
                width: 100% !important;
                font-size: 14px !important;
            }
        }
    </style>
</head>
<body>
    <div class="email-container" style="max-width: 600px; margin: 30px auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);">
        
        <!-- Top Banner Section -->
        <div class="top-banner" style="position: relative; width: 100%; max-width: 600px; height: 0; padding-top: 59.17%; background-image: url('{{BANNER_URL}}'); background-size: cover; background-repeat: no-repeat; background-position: center; margin-bottom: 0px;">
        </div>
        
        <!-- Content Section -->
        <div class="content" style="padding: 25px 20px; text-align: center;">
            <p style="text-align: center; font-size: 16px; font-family: Helvetica, Arial, sans-serif; line-height: 1.8; color: #000; margin-bottom: 20px;">
                {{INTRODUCTION}}
            </p>
            
            {{CONTENT_SECTIONS}}
            
        </div>
        
        <!-- Footer Section -->
        <div class="footer" style="background: linear-gradient(135deg, #001219, #001219); color: #fff; text-align: center; padding: 20px; font-size: 13px;">
            <p style="margin: 20px 0 0; text-align: center; font-size: 14px; font-weight: normal; font-family: Lora, Arial, sans-serif; line-height: 1.5; color: #BEBEBE;">Follow us</p>
            
            <table border="0" cellpadding="0" cellspacing="0" style="max-width: 400px; width: 100%; margin: 23px auto 0;" width="600">
                <tbody>
                    <tr align="center">
                        <td style="margin: 0 9px 0 0; display: inline-block;">
                            <a href="https://www.facebook.com/newsletter" style="color: #fff; font-size: 12px; font-weight: normal; display: block;" target="_blank">
                                <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/facebook.svg" alt="Facebook" style="color: #fff; font-family: Open Sans, sans-serif, Arial, sans-serif; width: 25px; height: 25px; filter: invert(1);">
                            </a>
                        </td>
                        <td style="margin: 0 9px; display: inline-block;">
                            <a href="https://twitter.com/newsletter" style="color: #fff; font-size: 12px; font-weight: normal; display: block;" target="_blank">
                                <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/twitter.svg" alt="Twitter" style="color: #ffffff; font-family: Open Sans, sans-serif, Arial, sans-serif; width: 25px; height: 25px; display: block; filter: invert(1);">
                            </a>
                        </td>
                        <td style="margin: 0 9px; display: inline-block;">
                            <a href="https://www.instagram.com/newsletter/" style="color: #fff; font-size: 12px; font-weight: normal; display: block;" target="_blank">
                                <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/instagram.svg" alt="Instagram" style="color: #fff; font-family: Open Sans, sans-serif, Arial, sans-serif; width: 25px; height: 25px; filter: invert(1);">
                            </a>
                        </td>
                        <td style="margin: 0 9px; display: inline-block;">
                            <a href="https://www.youtube.com/@newsletter" style="color: #fff; font-size: 12px; font-weight: normal; display: block;" target="_blank">
                                <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/youtube.svg" alt="Youtube" style="color: #fff; font-family: Open Sans, sans-serif, Arial, sans-serif; width: 25px; height: 25px; filter: invert(1);">
                            </a>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <table border="0" cellpadding="0" cellspacing="0" style="max-width: 280px; width: 100%; margin: 32px auto 0;" width="600">
                <tbody>
                    <tr>
                        <td style="max-width: 300px; width: 100%; height: 1px; background-color: #BEBEBE"></td>
                    </tr>
                </tbody>
            </table>
            
            <table border="0" cellpadding="0" cellspacing="0" style="max-width: 400px; width: 100%; margin: 16px auto 0; text-align: center; font-weight: normal; font-family: Lora, Arial, sans-serif; line-height: 1.5;" width="600">
                <tbody>
                    <tr>
                        <td style="display: inline-block;">
                            <a href="#" style="text-decoration: none; color: #BEBEBE; font-size: 12px; font-weight: normal;">Live Chat</a>
                            <span style="display: inline-block; color: #BEBEBE; margin: 0 5px">|</span>
                        </td>
                        <td style="display: inline-block;">
                            <a href="#" style="text-decoration: none; color: #BEBEBE; font-size: 12px; font-weight: normal;">Support Center</a>
                            <span style="display: inline-block; color: #BEBEBE; margin: 0 5px">|</span>
                        </td>
                        <td style="display: inline-block;">
                            <a href="#" style="text-decoration: none; color: #BEBEBE; font-size: 12px; font-weight: normal;">Privacy Policy</a>
                            <span style="display: inline-block; color: #BEBEBE; margin: 0 5px">|</span>
                        </td>
                        <td style="display: inline-block; vertical-align: bottom;">
                            <a href="<%unsub%>" style="text-decoration: none; color: #BEBEBE; font-size: 12px; font-weight: normal;">Unsubscribe</a>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <table border="0" cellpadding="0" cellspacing="0" style="max-width: 400px; width: 100%; margin: 16px auto 32px; text-align: center; font-weight: normal; font-family: Lora, Arial, sans-serif; line-height: 1.5;" width="600">
                <tbody>
                    <tr>
                        <td style="display: inline-block;">
                            <p style="color: #BEBEBE; margin: 0; font-size: 12px">
                                © {{CURRENT_YEAR}} Streaming Newsletter - All rights reserved.
                            </p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''
    
    def _group_by_date(self, content_items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group content items by date."""
        grouped = defaultdict(list)
        
        for item in content_items:
            date_str = item.get('date', '')
            if date_str:
                grouped[date_str].append(item)
        
        # Sort by date
        return dict(sorted(grouped.items()))
    
    def _generate_content_sections(self, grouped_content: Dict[str, List[Dict]]) -> str:
        """Generate HTML for all content sections."""
        sections_html = []
        
        for date_str, items in grouped_content.items():
            # Format date header
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d').upper()
            except:
                formatted_date = date_str
            
            # Generate section HTML
            section_html = f'''
            <div class="date-section" style="font-family: 'Helvetica Neue', Arial, sans-serif;">
                <h3 style="margin: 0; color: #3B108E; font-size: 20px; font-family: Helvetica, Arial, sans-serif, Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 1px; position: relative; display: inline-block; padding-bottom: 5px;">
                    {formatted_date}
                </h3>
                <table class="movie-list" border="0" cellspacing="0" cellpadding="10" width="100%" style="background-color: #fff; border-radius: 8px; padding: 15px; padding-left: 0px; padding-right: 0px;">
                    <tbody>
                        {self._generate_items_html(items)}
                    </tbody>
                </table>
            </div>'''
            
            sections_html.append(section_html)
        
        return '\n'.join(sections_html)
    
    def _generate_items_html(self, items: List[Dict]) -> str:
        """Generate HTML for individual content items."""
        items_html = []
        
        for item in items:
            # Extract item data with defaults
            name = item.get('name', 'Untitled')
            description = item.get('description', 'Check out this amazing content available for streaming.')
            channel = item.get('channel', 'Streaming')
            channel_image = item.get('channel_image', '')
            show_image = item.get('show_image', 'https://via.placeholder.com/180x120')
            
            # Get direct website URL for the channel
            website_url, missing_channel = self.channel_manager.get_channel_website(channel)
            if website_url:
                watch_now_link = website_url
            else:
                # Track missing channel for later prompting
                if missing_channel and missing_channel not in self.missing_channels:
                    self.missing_channels.append(missing_channel)
                # Fallback to a default link if channel not found
                logger.warning(f"No website URL for channel '{channel}', using fallback")
                watch_now_link = '#'
            
            # Truncate description if too long
            if len(description) > 200:
                description = description[:197] + '...'
            
            # Generate item HTML
            item_html = f'''
            <tr style="background-color: #f3f1ff; border-radius: 8px; overflow: hidden;">
                <td class="movie-card" style="background-color: #f3f1ff; overflow: hidden; display: flex; align-items: center; transition: transform 0.3s, box-shadow 0.3s;">
                    <img src="{show_image}" alt="{name}" style="width: 180px; height: 120px; border-radius: 8px; align-items: center; object-fit: cover; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                    <div class="movie-info" style="margin-left: 15px; margin-right: 15px; text-align: left;">
                        <strong style="font-family: Helvetica, Arial, sans-serif, Tahoma, Geneva, Verdana, sans-serif; font-size: 18px; color: #333;">
                            {name}
                        </strong>
                        <p style="text-align: left; font-size: 14px; font-family: Helvetica, Arial, sans-serif; line-height: 1.5; color: #333; text-align: justify; margin-bottom: 20px;">
                            {description}
                        </p>
                        <div style="display: flex;">
                            {self._generate_channel_html(channel, channel_image)}
                        </div>
                    </div>
                </td>
            </tr>
            <tr style="height: 15px; background: #f3f1ff; transition: transform 0.3s, box-shadow 0.3s;">
                <td>
                    <a href="{watch_now_link}" class="add-to-calendar" style="font-family: Helvetica, Arial, sans-serif, Tahoma, Geneva, Verdana, sans-serif; display: block; width: 100%; padding: 14px 20px; background-color: #6d3db9; color: white; text-decoration: none; text-align: center; font-size: 16px; font-weight: bold; border-radius: 30px; margin-top: 10px; box-sizing: border-box; transition: background 0.3s ease, transform 0.3s ease;">
                        Watch Now
                    </a>
                </td>
            </tr>
            <tr style="height: 15px;"></tr>'''
            
            items_html.append(item_html)
        
        return '\n'.join(items_html)
    
    def _generate_channel_html(self, channel: str, channel_image: str) -> str:
        """Generate HTML for channel display."""
        if channel_image:
            return f'''
            <img src="{channel_image}" alt="{channel} Logo" style="max-width: 50px; height: auto; margin-right: 10px; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); vertical-align: middle;">
            <span style="font-family: Helvetica, Arial, sans-serif; font-size: 14px; color: #555; line-height: 1; margin-top: 8px">
                Available on: {channel}
            </span>'''
        else:
            return f'''
            <span style="font-family: Helvetica, Arial, sans-serif; font-size: 14px; color: #555; line-height: 1; margin-top: 8px">
                Available on: {channel}
            </span>'''
    
    def get_missing_channels(self) -> List[str]:
        """Get list of channels that need website information."""
        return self.missing_channels
    
    def add_channel_website(self, channel: str, website: str, country: str = 'US') -> bool:
        """Add website information for a channel."""
        success = self.channel_manager.add_channel_to_database(channel, website, country)
        if success and channel in self.missing_channels:
            self.missing_channels.remove(channel)
        return success
    
    def _get_error_template(self) -> str:
        """Return error template HTML."""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <div style="text-align: center; padding: 50px;">
                <h1>Newsletter Generation Error</h1>
                <p>An error occurred while generating your newsletter. Please try again.</p>
            </div>
        </body>
        </html>'''