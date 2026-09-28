import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# User-Agent to avoid getting blocked by Finviz
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Standard Finviz Sectors & sample fallback mappings if dynamic scraping meets network issues
SECTOR_MAP = {
    "Basic Materials": "sec_basicmaterials",
    "Communication Services": "sec_communicationservices",
    "Consumer Cyclical": "sec_consumercyclical",
    "Consumer Defensive": "sec_consumerdefensive",
    "Energy": "sec_energy",
    "Financial": "sec_financial",
    "Healthcare": "sec_healthcare",
    "Industrials": "sec_industrials",
    "Real Estate": "sec_realestate",
    "Technology": "sec_technology",
    "Utilities": "sec_utilities"
}

def get_sectors():
    """Returns list of sector names."""
    return list(SECTOR_MAP.keys())

def fetch_industries_for_sector(sector_name):
    """
    Fetches industries belonging to a given sector from Finviz group page.
    """
    url = "https://finviz.com/groups.ashx?g=industry&v=110"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Extract industry links with sector metadata if available
            # Or fall back to known finviz industry query parameters
            # For reliability, query finviz screener by sector
    except Exception as e:
        print(f"Error fetching industries for {sector_name}: {e}")
    
    # Return placeholder/scraped industry list
    return []

def fetch_top_stocks_for_industry(sector_name, industry_name, top_n=10):
    """
    Fetches top N stock symbols by market cap for a given sector & industry from Finviz screener.
    """
    # Finviz screener URL parameters: v=111 (Overview), f=sec_...,ind_... , o=-marketcap
    # We query the screener endpoint with URL encoding
    formatted_sec = sector_name.lower().replace(" ", "")
    formatted_ind = industry_name.lower().replace(" ", "").replace("&", "").replace("-", "")
    
    url = f"https://finviz.com/screener.ashx?v=111&f=sector_{formatted_sec},industry_{formatted_ind}&o=-marketcap"
    
    symbols = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for screener table links containing ticker symbols
            links = soup.find_all('a', class_='tab-link')
            for a in links:
                text = a.text.strip()
                if text.isupper() and 1 <= len(text) <= 5 and text not in symbols:
                    symbols.append(text)
                if len(symbols) >= top_n:
                    break
    except Exception as e:
        print(f"Error scraping stocks for industry '{industry_name}': {e}")
        
    return symbols[:top_n]

def generate_pdf_report(sector_name, df_sector, output_path):
    """
    Generates a cleanly formatted PDF document for the sector leaders table.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )
    normal_style = styles['Normal']

    elements = []
    elements.append(Paragraph(f"Sector Industry Leaders: {sector_name}", title_style))
    elements.append(Spacer(1, 10))

    # Format table data
    table_data = [["Sector", "Industry", "Top Stocks (Market Cap)"]]
    for _, row in df_sector.iterrows():
        stocks_str = row['Stock Symbols'] if isinstance(row['Stock Symbols'], str) else ", ".join(row['Stock Symbols'])
        table_data.append([
            Paragraph(str(row['Sector']), normal_style),
            Paragraph(str(row['Industry']), normal_style),
            Paragraph(stocks_str, normal_style)
        ])

    t = Table(table_data, colWidths=[120, 160, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(t)
    doc.build(elements)
    return output_path
