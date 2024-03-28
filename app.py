import time
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

def fetch_webpage(url, proxy=None):
    start_time = time.time()
    try:
        # Define proxy settings if provided
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy
            }
        else:
            proxies = None
        
        # Fetch the webpage content with proxy settings
        response = requests.get(url, proxies=proxies)
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if response.status_code == 200:
            return response.content, load_time
        else:
            return None, load_time
    except Exception as e:
        return None, None

def scrape_data(url, proxy=None):
    webpage_content, load_time = fetch_webpage(url, proxy)
    if webpage_content is not None:
        try:
            # Parse the HTML content
            soup = BeautifulSoup(webpage_content, 'html.parser')
            # Prettify the HTML content for better readability
            prettified_html = soup.prettify()
            # Evaluate SEO rank
            seo_rank = evaluate_seo_rank(soup)
            # Simple analysis for potential weak coding
            weak_coding, weak_lines = check_weak_coding(prettified_html)
            return {
                "url": url,
                "seo_rank": seo_rank,
                "page_source": prettified_html,
                "weak_coding": weak_coding,
                "weak_lines": weak_lines,
                "load_time": load_time
            }
        except Exception as e:
            return {"error": "Error parsing HTML: {}".format(str(e))}
    else:
        return {"error": "Failed to fetch webpage."}

def evaluate_seo_rank(soup):
    # Evaluate SEO rank based on certain factors such as meta tags, headings, etc.
    seo_rank = 0
    
    # Check for presence of title tag
    if soup.title:
        seo_rank += 1
    
    # Check for presence of meta description tag
    meta_description = soup.find("meta", attrs={"name": "description"})
    if meta_description:
        seo_rank += 1
    
    # Check for presence of h1 tag
    h1_tags = soup.find_all("h1")
    if h1_tags:
        seo_rank += len(h1_tags)
    
    # You can add more SEO factors to evaluate here
    
    return seo_rank

def check_weak_coding(html_content):
    # Regular expressions to identify potential weak coding patterns
    weak_patterns = [
        (r'<script.*?>.*?</script>', 'Script'),  # Scripts
        (r'<iframe.*?>.*?</iframe>', 'Iframe'),  # Iframes
        (r'<embed.*?>.*?</embed>', 'Embed'),     # Embeds
        (r'on\w+=".*?"', 'Event attributes')    # Event attributes
    ]
    weak_count = 0
    weak_lines = []
    
    for pattern, pattern_name in weak_patterns:
        matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            weak_count += 1
            # Find the line number of the match
            lines = html_content.count('\n', 0, match.start()) + 1
            weak_lines.append((pattern_name, lines, match.group()))
    
    return weak_count, weak_lines

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        proxy = request.form['proxy'] if 'proxy' in request.form else None
        scraped_data = scrape_data(url, proxy)
        return render_template('index.html', scraped_data=scraped_data)
    return render_template('index.html', scraped_data=None)

if __name__ == '__main__':
    app.run(debug=True)
