"""
job_scraper.py
Fetches job descriptions from URLs. Currently uses a BeautifulSoup implementation.
"""

import aiohttp
from bs4 import BeautifulSoup
import re

async def scrape_job_description(url: str) -> str:
    """
    Scrapes a job posting URL and extracts the main text content.
    This is a basic BeautifulSoup implementation. For heavily JavaScript-rendered
    sites (like LinkedIn or Greenhouse), a Playwright implementation may be required later.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=15) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch URL {url}: {e}")
            
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script, style, nav, header, footer tags to isolate main content
    for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
        element.decompose()
        
    # Attempt to find standard job description containers
    # Many ATS systems use specific IDs or classes
    job_content = soup.find(id=re.compile(r"job.*desc|desc.*job", re.I)) or \
                  soup.find(class_=re.compile(r"job.*desc|desc.*job", re.I))
                  
    if job_content:
        text = job_content.get_text(separator="\n", strip=True)
    else:
        # Fallback to body
        text = soup.body.get_text(separator="\n", strip=True) if soup.body else soup.get_text(separator="\n", strip=True)
        
    # Clean up excess whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text
