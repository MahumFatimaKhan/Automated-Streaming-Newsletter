from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from flask_caching import Cache
from config import Config
import os
import logging
from datetime import datetime

# Import modules (to be created)
from modules.scraper import TVInsiderScraper
from modules.link_generator import LinkGenerator
from modules.ai_content import AIContentGenerator
from modules.image_generator import ImageGenerator
from modules.newsletter_builder import NewsletterBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Validate configuration
config_errors = Config.validate()
if config_errors:
    logger.warning(f"Configuration warnings: {', '.join(config_errors)}")

# Initialize extensions
CORS(app)
cache = Cache(app)

# Create necessary directories
os.makedirs(Config.TEMP_FOLDER, exist_ok=True)
os.makedirs(Config.ASSETS_FOLDER, exist_ok=True)
os.makedirs(os.path.join(Config.STATIC_FOLDER, 'css'), exist_ok=True)
os.makedirs(os.path.join(Config.STATIC_FOLDER, 'js'), exist_ok=True)
os.makedirs(os.path.join(Config.STATIC_FOLDER, 'banners'), exist_ok=True)
os.makedirs(os.path.join(Config.STATIC_FOLDER, 'fonts'), exist_ok=True)

# Initialize service modules
scraper = TVInsiderScraper()
link_generator = LinkGenerator()
ai_generator = AIContentGenerator(Config.OPENAI_API_KEY)
image_generator = ImageGenerator(Config.FLUX_API_KEY, Config.FLUX_API_URL)
newsletter_builder = NewsletterBuilder()

# Session storage (in production, use Redis or database)
sessions = {}

@app.route('/')
def index():
    """Main application interface."""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape_content():
    """Scrape TVInsider for content within date range."""
    try:
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Start and end dates are required'}), 400
        
        # Validate date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if (end - start).days > 30:
            return jsonify({'error': 'Date range cannot exceed 30 days'}), 400
        
        if start > end:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        # Perform scraping
        logger.info(f"Starting scrape for {start_date} to {end_date}")
        
        try:
            results = scraper.scrape_date_range(start_date, end_date)
        except Exception as scrape_error:
            logger.error(f"Scraping failed: {str(scrape_error)}")
            error_message = str(scrape_error)
            
            # Provide helpful error messages
            if "cannot connect" in error_message.lower() or "connection" in error_message.lower():
                return jsonify({
                    'error': 'Connection Error: Unable to reach TVInsider.com. Please check your internet connection and try again.'
                }), 500
            elif "chrome" in error_message.lower():
                return jsonify({
                    'error': 'Chrome Browser Error: Please ensure Google Chrome is installed on your system. If the issue persists, try setting HEADLESS_BROWSER=false in your .env file.'
                }), 500
            else:
                return jsonify({'error': f'Scraping failed: {error_message}'}), 500
        
        # Normalize website URLs for scraped content
        for item in results:
            website = item.get('website', '')
            if website:
                item['website_url'] = link_generator.normalize_website_url(website)
            else:
                item['website_url'] = '#'
        
        # Store in session
        session_id = request.headers.get('X-Session-Id', 'default')
        sessions[session_id] = {
            'scraped_data': results,
            'date_range': {'start': start_date, 'end': end_date}
        }
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        error_message = str(e)
        
        # Check for timeout errors
        if 'timeout' in error_message.lower() or 'timed out' in error_message.lower():
            return jsonify({
                'error': 'timeout',
                'message': 'The website took too long to respond. This might be due to slow internet or high website traffic. Please try again or select a different date range.',
                'user_message': 'Request timed out. Please try again or select different dates.'
            }), 504  # Gateway Timeout
        
        return jsonify({'error': error_message}), 500

@app.route('/api/select-content', methods=['POST'])
def select_content():
    """Save selected content items for newsletter."""
    try:
        data = request.json
        session_id = request.headers.get('X-Session-Id', 'default')
        
        if session_id not in sessions:
            return jsonify({'error': 'No session data found'}), 400
        
        selected_ids = data.get('selected_items', [])
        session_data = sessions[session_id]
        
        # Filter scraped data to only include selected items
        all_items = session_data.get('scraped_data', [])
        selected_items = [item for i, item in enumerate(all_items) if str(i) in selected_ids]
        
        session_data['selected_content'] = selected_items
        
        return jsonify({
            'success': True,
            'selected_count': len(selected_items)
        })
        
    except Exception as e:
        logger.error(f"Content selection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-taglines', methods=['POST'])
def generate_taglines():
    """Generate AI tagline options."""
    try:
        # Handle both empty and non-empty request body
        data = request.json if request.json else {}
        session_id = request.headers.get('X-Session-Id', 'default')
        
        logger.info(f"Generating taglines for session: {session_id}")
        
        if session_id not in sessions:
            logger.error(f"Session {session_id} not found in sessions")
            return jsonify({'error': 'No session data found. Please scrape content first.'}), 400
        
        session_data = sessions[session_id]
        # Use selected content if available, otherwise use all scraped data
        content_to_use = session_data.get('selected_content', session_data.get('scraped_data', []))
        
        if not content_to_use:
            logger.error("No content available for tagline generation")
            return jsonify({'error': 'No content available. Please scrape content first.'}), 400
        
        context = {
            'date_range': session_data.get('date_range', {}),
            'content_count': len(content_to_use),
            'highlights': [item.get('name', '') for item in content_to_use[:5] if item.get('name')]
        }
        
        logger.info(f"Generating taglines with context: {context}")
        
        taglines = ai_generator.generate_taglines(context, count=3)
        
        session_data['taglines'] = taglines
        
        logger.info(f"Successfully generated {len(taglines)} taglines")
        
        return jsonify({
            'success': True,
            'taglines': taglines
        })
        
    except Exception as e:
        logger.error(f"Tagline generation error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Failed to generate taglines: {str(e)}'}), 500

@app.route('/api/generate-intros', methods=['POST'])
def generate_intros():
    """Generate AI introduction options."""
    try:
        data = request.json
        session_id = request.headers.get('X-Session-Id', 'default')
        
        if session_id not in sessions:
            return jsonify({'error': 'No session data found'}), 400
        
        session_data = sessions[session_id]
        selected_tagline = data.get('selected_tagline', '')
        
        context = {
            'tagline': selected_tagline,
            'date_range': session_data['date_range'],
            'content': session_data['scraped_data'][:10]
        }
        
        intros = ai_generator.generate_introductions(context, count=3)
        
        session_data['intros'] = intros
        session_data['selected_tagline'] = selected_tagline
        
        return jsonify({
            'success': True,
            'introductions': intros
        })
        
    except Exception as e:
        logger.error(f"Introduction generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-banners', methods=['POST'])
def generate_banners():
    """Generate banner images with AI."""
    try:
        data = request.json
        session_id = request.headers.get('X-Session-Id', 'default')
        
        if session_id not in sessions:
            return jsonify({'error': 'No session data found'}), 400
        
        session_data = sessions[session_id]
        selected_intro = data.get('selected_intro', '')
        
        # Generate banner variations
        banners = image_generator.generate_banners(
            tagline=session_data.get('selected_tagline', ''),
            theme_context=session_data['scraped_data'][:5]
        )
        
        session_data['banners'] = banners
        session_data['selected_intro'] = selected_intro
        
        return jsonify({
            'success': True,
            'banners': banners
        })
        
    except Exception as e:
        logger.error(f"Banner generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview', methods=['POST'])
def preview_newsletter():
    """Generate newsletter preview."""
    try:
        data = request.json
        session_id = request.headers.get('X-Session-Id', 'default')
        
        if session_id not in sessions:
            return jsonify({'error': 'No session data found'}), 400
        
        session_data = sessions[session_id]
        selected_banner = data.get('selected_banner', '')
        
        # Use selected content if available, otherwise use all scraped data
        content_to_use = session_data.get('selected_content', session_data.get('scraped_data', []))
        
        # Build newsletter HTML
        newsletter_html = newsletter_builder.build(
            banner_url=selected_banner,
            tagline=session_data.get('selected_tagline', ''),
            introduction=session_data.get('selected_intro', ''),
            content_items=content_to_use,
            date_range=session_data['date_range']
        )
        
        # Check for missing channels
        missing_channels = newsletter_builder.get_missing_channels()
        
        session_data['newsletter_html'] = newsletter_html
        session_data['selected_banner'] = selected_banner
        session_data['missing_channels'] = missing_channels
        
        return jsonify({
            'success': True,
            'html': newsletter_html,
            'missing_channels': missing_channels
        })
        
    except Exception as e:
        logger.error(f"Preview generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-channel-website', methods=['POST'])
def add_channel_website():
    """Add website information for a missing channel."""
    try:
        data = request.json
        channel = data.get('channel')
        website = data.get('website')
        country = data.get('country', 'US')
        
        if not channel or not website:
            return jsonify({'error': 'Channel and website are required'}), 400
        
        # Add to database
        success = newsletter_builder.add_channel_website(channel, website, country)
        
        if success:
            logger.info(f"Added website '{website}' for channel '{channel}'")
            return jsonify({
                'success': True,
                'message': f'Website added for {channel}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add channel website'
            }), 500
            
    except Exception as e:
        logger.error(f"Error adding channel website: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET', 'POST'])
def download_newsletter():
    """Download the generated newsletter as HTML file."""
    try:
        # Accept both GET and POST methods
        session_id = request.headers.get('X-Session-Id', 'default')
        
        logger.info(f"Download request received for session: {session_id}")
        logger.info(f"Current sessions: {list(sessions.keys())}")
        
        if session_id not in sessions:
            logger.error(f"Session {session_id} not found in sessions")
            return jsonify({
                'error': 'No session data found. Please regenerate the newsletter preview.',
                'details': 'Session may have expired. Try generating the preview again.'
            }), 400
        
        session_data = sessions[session_id]
        
        if 'newsletter_html' not in session_data:
            logger.error(f"Newsletter HTML not found in session {session_id}")
            return jsonify({
                'error': 'Newsletter not generated yet. Please complete the preview step first.',
                'details': 'Click "Preview Newsletter" before downloading.'
            }), 400
        
        # Save to temp file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"newsletter_{timestamp}.html"
        filepath = os.path.join(Config.TEMP_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(session_data['newsletter_html'])
        
        logger.info(f"Newsletter saved to {filepath} for download")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='text/html'
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=5000)