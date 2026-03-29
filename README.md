# KPT Invoice Scraper & Plotter
*Mostly vibe-coded with Antigravity, but I polished the rough edges manually. For getting insides into your bills I think it's great.*

This repository provides an automated Python workflow to scrape health insurance invoice histories directly from the KPT API and save the individual PDFs locally. It also includes a plotting utility to visualize the total monthly insurance costs in a clean, chronological stacked bar chart.

<img width="4200" height="2400" alt="image" src="https://github.com/user-attachments/assets/e7b4a46d-51a8-42d1-b181-5b6a23edb168" />

## Setup Instructions

1. **Create and Activate a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Before scraping, you need to inject your active session credentials.
1. Copy the provided template to create your live configuration file:
   ```bash
   cp config.py.tmpl config.py
   ```
2. Open `config.py` and paste in your active KPT session cookie string. *(Note: `config.py` is ignored by git, so your secrets won't accidentally be committed to version control).*

## Usage

* **Scraping Invoices (`scrape.py`)**  
  Run the scraper to crawl the API. It loops through all paginated entries, downloads each invoice PDF, and compiles a comprehensive `all.json` database of everything you've paid inside the newly generated `cache/invoices_XX/` directory.

* **Plotting Data (`plot.py`)**  
  Execute `plot.py` to aggregate the JSON data into a clean segmented histogram of your costs. It also saves `monthly_totals.png` directly to your active cache directory.
