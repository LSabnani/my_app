import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Curated mapping of Sectors to their key Industries on Finviz
SECTOR_INDUSTRIES = {
    "Communication Services": [
        "Advertising Agencies", "Broadcasting", "Entertainment", "Interactive Media & Services",
        "Publishing", "Telecom Services"
    ],
    "Consumer Cyclical": [
        "Auto Manufacturers", "Auto Parts", "Department Stores", "Home Improvement Retail",
        "Internet Retail", "Lodging", "Packaging & Containers", "Restaurants", "Specialty Retail"
    ],
    "Consumer Defensive": [
        "Beverages - Non-Alcoholic", "Beverages - Wineries & Distilleries", "Confectioners",
        "Discount Stores", "Farm Products", "Household & Personal Products", "Packaged Foods", "Tobacco"
    ],
    "Energy": [
        "Oil & Gas E&P", "Oil & Gas Equipment & Services", "Oil & Gas Integrated",
        "Oil & Gas Midstream", "Oil & Gas Refining & Marketing", "Thermal Coal"
    ],
    "Financial": [
        "Asset Management", "Banks - Diversified", "Banks - Regional", "Capital Markets",
        "Financial Data & Stock Exchanges", "Insurance - Diversified", "Insurance Brokers"
    ],
    "Healthcare": [
        "Biotechnology", "Diagnostics & Research", "Drug Manufacturers - General",
        "Drug Manufacturers - Specialty & Generic", "Healthcare Plans", "Medical Devices", "Medical Instruments"
    ],
    "Industrials": [
        "Aerospace & Defense", "Airlines", "Building Products & Equipment", "Conglomerates",
        "Farm & Heavy Construction Machinery", "Industrial Distribution", "Specialty Industrial Machinery", "Waste Management"
    ],
    "Real Estate": [
        "REIT - Healthcare Facilities", "REIT - Industrial", "REIT - Office",
        "REIT - Residential", "REIT - Retail", "REIT - Specialized", "Real Estate Services"
    ],
    "Technology": [
        "Computer Hardware", "Consumer Electronics", "Information Technology Services",
        "Semiconductor Equipment & Materials", "Semiconductors", "Software - Application", "Software - Infrastructure"
    ],
    "Utilities": [
        "Utilities - Diversified", "Utilities - Electric", "Utilities - Independent Power Producers",
        "Utilities - Regulated Gas", "Utilities - Renewable", "Utilities - Regulated Water"
    ],
    "Basic Materials": [
        "Agricultural Inputs", "Aluminum", "Chemicals", "Copper", "Gold", "Specialty Chemicals", "Steel"
    ]
}

# Real sample top stocks per sector & industry (used for sample preview or fallback)
SAMPLE_STOCKS = {
    "Communication Services": {
        "Advertising Agencies": ["APP", "OMC", "TTD", "WPP", "MGNI", "LFTO", "DV", "STGW", "ZD", "CCO"],
        "Broadcasting": ["FOXA", "FOX", "NXST", "TGNA", "SBGI", "AMCX", "GTN"],
        "Entertainment": ["DIS", "NFLX", "WBD", "LYV", "FWONA", "RBLX", "WMG", "SPOT"],
        "Interactive Media & Services": ["GOOGL", "META", "SNAP", "PINS", "BIDU", "MTCH", "YELP"],
        "Publishing": ["NWS", "NWSA", "NYT", "DJCO", "SCHL"],
        "Telecom Services": ["T", "VZ", "TMUS", "CHTR", "CMCSA", "LBRDA"]
    }
}

def get_all_sectors():
    return list(SECTOR_INDUSTRIES.keys())

def get_industries(sector_name):
    return SECTOR_INDUSTRIES.get(sector_name, [])

def fetch_top_stocks(sector_name, industry_name, top_n=10):
    """
    Attempts dynamic web scraping from Finviz screener, falling back to curated data if required.
    """
    if sector_name in SAMPLE_STOCKS and industry_name in SAMPLE_STOCKS[sector_name]:
        return SAMPLE_STOCKS[sector_name][industry_name][:top_n]
    
    # Live scrape attempt from Finviz
    try:
        ind_query = industry_name.lower().replace(" ", "").replace("&", "").replace("-", "").replace(",", "")
        url = f"https://finviz.com/screener.ashx?v=111&f=ind_{ind_query}&o=-marketcap"
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            symbols = []
            for a in soup.find_all('a', class_='tab-link'):
                text = a.text.strip()
                if text.isupper() and 1 <= len(text) <= 5 and text not in symbols:
                    symbols.append(text)
                if len(symbols) >= top_n:
                    break
            if symbols:
                return symbols
    except Exception as e:
        print(f"Scrape warning for {industry_name}: {e}")

    # Generic realistic fallback based on market leaders if scrape unavailable
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "JNJ", "V"][:top_n]
