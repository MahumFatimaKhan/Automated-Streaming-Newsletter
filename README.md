<<<<<<< HEAD
# Automated-Streaming-Newsletter
=======
# Streaming Newsletter Generator

An automated Flask-based web application that generates personalized streaming newsletters by scraping TV show and movie data, creating AI-generated content and banners, and outputting professional HTML newsletters.

## Features


- 📅 **Date Range Selection**: Choose content for specific date ranges (up to 30 days)
- 🔍 **Automated Web Scraping**: Scrapes TVInsider.com for streaming content
- 🤖 **AI-Powered Content**: Generates taglines and introductions using OpenAI GPT
- 🎨 **AI Banner Generation**: Creates custom banners using Flux API
- 🔗 **Smart Link Generation**: Automatic short links and tracking links
- 📧 **Professional HTML Output**: Responsive, email-ready newsletter templates
- 👀 **Live Preview**: Preview your newsletter before downloading

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium web scraping)
- OpenAI API key
- Flux API key (optional, for banner generation)

## Installation

1. **Clone the repository**
```bash
cd "D:\Newsletter - Streaming"
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example env file
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

Add your API keys:
```env
OPENAI_API_KEY=your-openai-api-key-here
FLUX_API_KEY=your-flux-api-key-here
SECRET_KEY=your-secret-key-here
```

## Usage

1. **Start the Flask application**
```bash
python app.py
```

2. **Open your browser**
Navigate to `http://localhost:5000`

3. **Follow the step-by-step process**:
   - Select date range for content
   - Wait for scraping to complete
   - Choose from 3 AI-generated taglines
   - Select from 3 AI-generated introductions
   - Pick from 6 banner variations
   - Preview and download your newsletter

## Project Structure

```
streaming-newsletter/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create from .env.example)
├── static/                   # Static assets
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── assets/               # Images and templates
├── templates/                # HTML templates
│   └── index.html            # Main interface
├── modules/                  # Core functionality
│   ├── scraper.py            # TVInsider web scraping
│   ├── link_generator.py     # Link generation logic
│   ├── ai_content.py         # AI content generation
│   ├── image_generator.py    # Banner generation
│   └── newsletter_builder.py # HTML newsletter assembly
└── utils/                    # Utility functions
    ├── validators.py         # Input validation
    └── cache.py              # Caching utilities
```

## API Endpoints

- `GET /` - Main application interface
- `POST /api/scrape` - Scrape content for date range
- `POST /api/generate-taglines` - Generate AI taglines
- `POST /api/generate-intros` - Generate AI introductions
- `POST /api/generate-banners` - Generate banner images
- `POST /api/preview` - Generate newsletter preview
- `GET /api/download` - Download newsletter HTML

## Configuration

Edit `config.py` to adjust:

- **Scraping Settings**
  - `SCRAPING_TIMEOUT`: Maximum time for scraping (default: 30s)
  - `HEADLESS_BROWSER`: Run Chrome in headless mode (default: true)

- **Content Generation**
  - `TAGLINE_MIN_LENGTH`: Minimum tagline length (default: 50 chars)
  - `TAGLINE_MAX_LENGTH`: Maximum tagline length (default: 80 chars)
  - `INTRO_MIN_LENGTH`: Minimum introduction length (default: 100 chars)
  - `INTRO_MAX_LENGTH`: Maximum introduction length (default: 200 chars)

- **Image Settings**
  - `BANNER_WIDTH`: Banner width (default: 1200px)
  - `BANNER_HEIGHT`: Banner height (default: 400px)

- **Rate Limiting**
  - `OPENAI_RATE_LIMIT`: Requests per minute (default: 60)
  - `API_RETRY_ATTEMPTS`: Number of retry attempts (default: 3)

## Troubleshooting

### Chrome Driver Setup

The application uses ChromeDriver located in the `chromedriver-win64` folder.

#### ChromeDriver Location
- The ChromeDriver must be placed at: `chromedriver-win64\chromedriver.exe`
- Current version: ChromeDriver 139 (compatible with Chrome 138+)

#### To Update ChromeDriver
1. Check your Chrome version: `chrome://version/`
2. Download matching ChromeDriver from: https://googlechromelabs.github.io/chrome-for-testing/
3. Extract `chromedriver.exe` to the `chromedriver-win64` folder

#### If ChromeDriver Fails
- Ensure Chrome browser is installed
- Set `HEADLESS_BROWSER=false` in `.env` file to see the browser window
- Check that `chromedriver.exe` exists in `chromedriver-win64` folder

### API Key Errors
- Ensure your OpenAI API key starts with `sk-`
- Check your API key has sufficient credits
- Verify the Flux API endpoint is correct

### Scraping Failures
- Check internet connection
- Verify TVInsider.com is accessible
- Try reducing the date range
- Check if Chrome is installed

### Memory Issues
For large date ranges:
- Process in smaller batches
- Increase system memory allocation
- Use headless mode for Chrome

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
```

### Adding New Features

1. **New Scraping Sources**: Add scrapers in `modules/scraper.py`
2. **Custom Templates**: Add HTML templates in `templates/`
3. **New AI Providers**: Extend `modules/ai_content.py`
4. **Additional Banners**: Modify `modules/image_generator.py`

## Security Notes

- Never commit `.env` file with real API keys
- Use environment variables for all sensitive data
- Implement rate limiting for production use
- Sanitize all user inputs
- Use HTTPS in production

## Performance Optimization

- Enable caching for repeated requests
- Use async operations where possible
- Implement database for session storage (production)
- Use CDN for static assets
- Optimize images before serving

## Future Enhancements

- [ ] Template library for different styles
- [ ] Scheduling and automation
- [ ] A/B testing for content
- [ ] Analytics integration
- [ ] Multi-language support
- [ ] Email service provider integration
- [ ] Database storage for sessions
- [ ] User authentication system
- [ ] Batch processing for multiple newsletters
- [ ] Custom branding options

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs in the console
3. Ensure all dependencies are installed
4. Verify API keys are valid

## License

This project is proprietary software. All rights reserved.

## Contributors

- Development Team
- AI Integration Specialists
- UI/UX Designers

---

**Note**: This application requires valid API keys to function. Ensure you have the necessary subscriptions for OpenAI and Flux APIs before use.
>>>>>>> fe6babb (Read Me File)
