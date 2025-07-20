# Web Text Scraper

A powerful Python web scraper that extracts text content from websites, automatically discovers dropdown navigation links, and organizes content in a structured format. Features session management to avoid duplicate downloads and resume interrupted scraping sessions.

## Features

- 🔄 **Session Management**: Tracks visited URLs to avoid duplicates
- 📂 **Smart Content Extraction**: Finds main content areas automatically
- 🎯 **Dropdown Navigation**: Discovers and follows dropdown menus
- 📁 **Organized Storage**: Separates content, metadata, and session data
- ⚡ **Resumable Scraping**: Continue from where you left off
- 🛡️ **Rate Limiting**: Built-in delays to respect server resources
- 🧹 **Clean Text**: Removes HTML tags, scripts, and navigation elements

## Requirements

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- Internet connection

## Quick Setup

### Option 1: Automatic Setup (Recommended)

Run the setup script that handles everything for you:

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. **Clone or download the project files**
2. **Create virtual environment** (recommended):
   ```bash
   python -m venv web_scraper_env
   ```

3. **Activate virtual environment:**
   
   **Windows:**
   ```bash
   web_scraper_env\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source web_scraper_env/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python scraper.py https://example.com
```

### Advanced Usage
```bash
python scraper.py https://example.com [max_pages] [delay_seconds]
```

### Examples
```bash
# Scrape up to 100 pages with 3-second delays (default)
python scraper.py https://docs.python.org

# Scrape up to 50 pages with 2-second delays
python scraper.py https://docs.python.org 50 2

# Works with or without https://
python scraper.py docs.python.org
```

## Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `website_url` | Target website URL (required) | - | `https://example.com` |
| `max_pages` | Maximum pages to scrape | 100 | `50` |
| `delay_seconds` | Delay between requests | 3 | `2` |

## Output Structure

The scraper creates the following folder structure:

```
scraped_content/
├── pages/                    # Text content files
│   ├── Homepage_a1b2c3d4.txt
│   ├── About_Us_e5f6g7h8.txt
│   └── ...
├── metadata/                 # JSON metadata for each page
│   ├── Homepage_a1b2c3d4.txt.json
│   ├── About_Us_e5f6g7h8.txt.json
│   └── ...
└── scraping_session.json     # Session tracking (resume capability)
```

### File Contents

**Text Files (`pages/`):**
```
Title: Page Title Here
URL: https://example.com/page
Scraped: 2024-01-15 14:30:25
================================================================================

Clean text content of the page goes here...
```

**Metadata Files (`metadata/`):**
```json
{
  "title": "Page Title Here",
  "url": "https://example.com/page",
  "timestamp": "2024-01-15 14:30:25",
  "filename": "Page_Title_Here_a1b2c3d4.txt",
  "content_length": 1234
}
```

## Resuming Interrupted Sessions

If scraping is interrupted, simply run the same command again. The scraper will:
- Load the previous session from `scraping_session.json`
- Skip already downloaded pages
- Continue from where it left off

## Troubleshooting

### Common Issues

1. **"Chrome driver not found"**
   - The script automatically downloads ChromeDriver
   - Ensure you have Chrome browser installed

2. **"Permission denied" errors**
   - Run terminal/command prompt as administrator (Windows)
   - Use `sudo` for installation commands (Linux/Mac)

3. **SSL/Certificate errors**
   - Some sites may have SSL issues
   - The scraper includes basic SSL handling

4. **Rate limiting/blocked requests**
   - Increase the delay parameter
   - Some sites may block automated requests

### Performance Tips

- **Large sites**: Start with smaller `max_pages` values (10-20) to test
- **Slow sites**: Increase the `delay` parameter (5-10 seconds)
- **Memory usage**: The scraper processes pages one at a time to minimize memory usage

## Project Files

| File | Description |
|------|-------------|
| `scraper.py` | Main scraping script |
| `requirements.txt` | Python dependencies |
| `setup.sh` | Linux/Mac setup script |
| `setup.bat` | Windows setup script |
| `README.md` | This documentation |

## Legal and Ethical Usage

- **Respect robots.txt**: Check website's robots.txt file
- **Rate limiting**: Don't overwhelm servers with rapid requests
- **Terms of service**: Review website's terms before scraping
- **Copyright**: Respect copyrighted content and fair use
- **Personal use**: This tool is designed for research and personal use

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the console output for specific error messages
3. Ensure all dependencies are properly installed
4. Verify the target website is accessible in your browser

---

**Happy Scraping!** 🚀
