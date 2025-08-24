# Automated-Streaming-Newsletter

> **Streamline your streaming content curation with AI-powered automation**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Maintained](https://img.shields.io/badge/maintained-yes-green.svg)](https://github.com/mahumfatimakhan)

## 📋 Summary

The **Automated Streaming Newsletter** is an innovative Flask-based web application that revolutionizes how streaming content newsletters are created. Developed by **Mahum Fatima Khan**, this tool combines web scraping, AI content generation, and automated design to produce professional, personalized newsletters in minutes instead of hours.

### 🚀 Why It's Efficient

- **⚡ Time-Saving**: Reduces newsletter creation time from hours to minutes through end-to-end automation
- **🤖 AI-Powered**: Leverages OpenAI GPT for intelligent content generation and Flux API for custom banner creation
- **🔄 Batch Processing**: Efficiently scrapes and processes up to 30 days of content in a single operation
- **💾 Smart Caching**: Implements caching mechanisms to minimize API calls and improve response times
- **🎯 One-Click Operation**: From date selection to final download - complete automation with minimal user input
- **📊 Scalable Architecture**: Modular design allows easy expansion and maintenance
- **🔗 Automated Link Generation**: Instantly creates tracking and short links for all content

### 🎯 Key Benefits

1. **Eliminates Manual Work**: No more copying and pasting content from multiple sources
2. **Consistent Quality**: AI ensures professional-quality taglines and introductions every time
3. **Cost-Effective**: Reduces the need for dedicated content writers and designers
4. **Error-Free**: Automated processes eliminate human errors in link generation and formatting
5. **Responsive Design**: Generated newsletters are automatically optimized for all devices
<img width="253" height="648" alt="Screenshot 2025-08-24 at 8 23 57 AM" src="https://github.com/user-attachments/assets/7bf5e276-f758-414b-81b8-822b2ca2a182" />

https://github.com/user-attachments/assets/8c341c04-283b-4f36-9833-1e312d81f9f7



---

## 📖 Project Description

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


## 👩‍💻 Author

**Mahum Fatima Khan**

- GitHub: [@mahumfatimakhan](https://github.com/mahumfatimakhan)
- LinkedIn: [Mahum Fatima Khan](https://www.linkedin.com/in/mahum-fatima-khan-51ab981a8/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for the amazing tools and libraries

---

**Note**: This application requires valid API keys to function. Ensure you have the necessary subscriptions for OpenAI and Flux APIs before use.

---

<p align="center">Made with ❤️ by Mahum Fatima Khan</p>
