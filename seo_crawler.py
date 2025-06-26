import requests
import csv
from datetime import datetime
import sys
import os
from dotenv import load_dotenv
import json
import re
from urllib.parse import urlparse, urljoin
import pandas as pd

# Load environment variables
load_dotenv()

class SEOAnalyzer:
    def __init__(self):
        """
        Initialize SEO Analyzer with Firecrawl API
        """
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set FIRECRAWL_API_KEY in .env file")
        
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def count_headings(self, markdown):
        """Count headings in markdown content"""
        h1_count = len(re.findall(r'^# [^#]', markdown, re.MULTILINE))
        h2_count = len(re.findall(r'^## [^#]', markdown, re.MULTILINE))
        h3_count = len(re.findall(r'^### [^#]', markdown, re.MULTILINE))
        return h1_count, h2_count, h3_count

    def extract_heading_content(self, markdown):
        """Extract heading content from markdown"""
        h1_pattern = re.compile(r'^# ([^\n]+)', re.MULTILINE)
        h2_pattern = re.compile(r'^## ([^\n]+)', re.MULTILINE)
        h3_pattern = re.compile(r'^### ([^\n]+)', re.MULTILINE)
        
        h1_content = '; '.join(h1_pattern.findall(markdown))
        h2_content = '; '.join(h2_pattern.findall(markdown))
        h3_content = '; '.join(h3_pattern.findall(markdown))
        
        return h1_content, h2_content, h3_content

    def extract_links_from_html(self, html):
        """Extract links from HTML content"""
        links = []
        link_pattern = re.compile(r'<a[^>]+href=["\'](.*?)["\']([^>]*?)>', re.IGNORECASE)
        matches = link_pattern.finditer(html)
        for match in matches:
            link = match.group(1)
            attrs = match.group(2)
            if link and not link.startswith(('#', 'javascript:', 'mailto:')):
                rel = re.search(r'rel=["\'](.*?)["\']', attrs)
                links.append({
                    'url': link,
                    'rel': rel.group(1) if rel else '',
                    'text': re.sub(r'<[^>]+>', '', match.group(0))
                })
        return links

    def extract_images_from_html(self, html, base_url):
        """Extract images from HTML with enhanced information"""
        images = []
        img_pattern = re.compile(r'<img[^>]+(?:src|data-src)=["\'](.*?)["\']([^>]*)>', re.IGNORECASE)
        matches = img_pattern.finditer(html)
        for match in matches:
            src = match.group(1)
            attrs = match.group(2)
            
            # Extract alt text
            alt_match = re.search(r'alt=["\'](.*?)["\']', attrs)
            alt_text = alt_match.group(1) if alt_match else ''
            
            # Extract width and height
            width_match = re.search(r'width=["\'](.*?)["\']', attrs)
            height_match = re.search(r'height=["\'](.*?)["\']', attrs)
            
            # Extract srcset if available
            srcset_match = re.search(r'srcset=["\'](.*?)["\']', attrs)
            srcset = srcset_match.group(1) if srcset_match else ''
            
            # Make image URL absolute
            absolute_src = urljoin(base_url, src)
            
            images.append({
                'src': absolute_src,
                'alt': alt_text,
                'has_alt': bool(alt_text),
                'width': width_match.group(1) if width_match else None,
                'height': height_match.group(1) if height_match else None,
                'srcset': srcset
            })
        return images

    def extract_meta_tags(self, html):
        """Extract meta tags from HTML"""
        meta_tags = []
        meta_pattern = re.compile(r'<meta[^>]+>', re.IGNORECASE)
        matches = meta_pattern.finditer(html)
        for match in matches:
            tag = match.group(0)
            name = re.search(r'name=["\'](.*?)["\']', tag)
            content = re.search(r'content=["\'](.*?)["\']', tag)
            if name and content:
                meta_tags.append({
                    'name': name.group(1),
                    'content': content.group(1)
                })
        return meta_tags

    def is_internal_link(self, base_url, link):
        """Check if a link is internal"""
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        return not link_domain or base_domain == link_domain

    def extract_schema_markup(self, html):
        """Extract schema markup from HTML"""
        schema_data = []
        schema_pattern = re.compile(r'<script[^>]*type=["\'](application/ld\+json)["\'][^>]*>(.*?)</script>', re.DOTALL)
        matches = schema_pattern.finditer(html)
        for match in matches:
            try:
                schema_json = json.loads(match.group(2))
                schema_data.append(schema_json)
            except json.JSONDecodeError:
                continue
        return schema_data

    def extract_canonical_tag(self, html):
        """Extract canonical tag from HTML"""
        # Try different possible formats of canonical tags
        canonical_patterns = [
            # Format: <link rel="canonical" href="url">
            r'<link[^>]*rel=["\'](canonical)["\'][^>]*href=["\'](.*?)["\']',
            # Format: <link href="url" rel="canonical">
            r'<link[^>]*href=["\'](.*?)["\'][^>]*rel=["\'](canonical)["\']'
        ]
        
        for pattern in canonical_patterns:
            matches = re.finditer(pattern, html, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # For the first pattern
                if match.group(1) == 'canonical':
                    return match.group(2)
                # For the second pattern
                elif match.group(2) == 'canonical':
                    return match.group(1)
        
        # If no canonical found with regex, try a more lenient approach
        head_match = re.search(r'<head[^>]*>(.*?)</head>', html, re.DOTALL | re.IGNORECASE)
        if head_match:
            head_content = head_match.group(1)
            print("\nDebug: Found <head> section")
            # Look for any link tag containing canonical
            canonical_tag = re.search(r'<link[^>]*?(?:canonical)[^>]*?>', head_content, re.IGNORECASE)
            if canonical_tag:
                print(f"Debug: Found canonical tag: {canonical_tag.group(0)}")
                href_match = re.search(r'href=["\'](.*?)["\']', canonical_tag.group(0))
                if href_match:
                    return href_match.group(1)
        
        return None

    def extract_hreflang_tags(self, html):
        """Extract hreflang tags from HTML"""
        hreflang_pattern = re.compile(r'<link[^>]*rel=["\'](alternate)["\'][^>]*hreflang=["\'](.*?)["\'][^>]*href=["\'](.*?)["\']', re.IGNORECASE)
        matches = hreflang_pattern.finditer(html)
        hreflang_data = []
        for match in matches:
            hreflang_data.append({
                'language': match.group(2),
                'url': match.group(3)
            })
        return hreflang_data

    def analyze_page(self, url: str):
        """
        Analyze a webpage using Firecrawl API
        """
        try:
            print(f"\nMaking request to Firecrawl API...")
            print(f"URL: {url}")
            print(f"API Key (first 10 chars): {self.api_key[:10]}...")
            
            payload = {
                "url": url,
                "formats": ["markdown", "rawHtml"],  # Request raw HTML to get complete page including head
                "onlyMainContent": False,
                "blockAds": True,
                "storeInCache": True
            }
            
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json=payload
            )
            
            print(f"\nResponse Status Code: {response.status_code}")
            print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            
            if response.status_code != 200:
                print(f"Response Text: {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")

            result = response.json()
            
            if not result.get('success'):
                raise Exception(f"API request failed: {result.get('error')}")
            
            data = result.get('data', {})
            metadata = data.get('metadata', {})
            markdown_content = data.get('markdown', '')
            html_content = data.get('rawHtml', '')  # Use raw HTML instead of processed HTML
            
            # Debug: Print a small section of the HTML to check for head content
            print("\nDebug: First 500 characters of HTML content:")
            print(html_content[:500] if html_content else "No HTML content")
            
            # Extract all data including new metrics
            links = self.extract_links_from_html(html_content)
            images = self.extract_images_from_html(html_content, url)
            meta_tags = self.extract_meta_tags(html_content)
            h1_content, h2_content, h3_content = self.extract_heading_content(markdown_content)
            schema_data = self.extract_schema_markup(html_content)
            
            # Try to get canonical from metadata first
            canonical_url = metadata.get('canonical')
            if not canonical_url:
                # If not in metadata, try to extract from HTML
                canonical_url = self.extract_canonical_tag(html_content)
            print(f"\nDebug: Canonical URL found: {canonical_url}")
            
            hreflang_tags = self.extract_hreflang_tags(html_content)
            
            # Count headings
            h1_count, h2_count, h3_count = self.count_headings(markdown_content)
            
            # Analyze links
            internal_links = [l for l in links if self.is_internal_link(url, l['url'])]
            external_links = [l for l in links if not self.is_internal_link(url, l['url'])]
            nofollow_links = [l for l in links if 'nofollow' in l.get('rel', '')]
            
            # Format image dimensions and srcset info
            image_details = []
            for img in images:
                details = f"{img['src']}"
                if img['width'] and img['height']:
                    details += f" ({img['width']}x{img['height']})"
                if img['alt']:
                    details += f" [alt: {img['alt']}]"
                if img['srcset']:
                    details += f" [srcset available]"
                image_details.append(details)

            # Prepare the analysis dictionary with new metrics
            analysis = {
                "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""],
                "URL": [url, ""],
                "Status Code": [metadata.get('statusCode', response.status_code), ""],
                "Load Time": [f"{round(response.elapsed.total_seconds(), 2)} seconds", ""],
                "Title": [metadata.get('title', ''), f"Length: {len(metadata.get('title', ''))} chars"],
                "Meta Description": [metadata.get('description', ''), f"Length: {len(metadata.get('description', ''))} chars"],
                "Meta Keywords": [metadata.get('keywords', ''), "Comma-separated list of keywords"],
                "Canonical URL": [canonical_url or "Not found", "Specified canonical URL"],
                "Schema Markup": [len(schema_data), f"Types: {', '.join([s.get('@type', 'Unknown') for s in schema_data]) if schema_data else 'None found'}"],
                "Hreflang Tags": [len(hreflang_tags), '; '.join([f"{h['language']}: {h['url']}" for h in hreflang_tags]) if hreflang_tags else "None found"],
                "Robots Meta": [metadata.get('robots', 'Not found'), "Robots meta tag content"],
                "Viewport Meta": [metadata.get('viewport', 'Not found'), "Viewport meta tag content"],
                "OG Title": [metadata.get('ogTitle', ''), "Open Graph title"],
                "OG Description": [metadata.get('ogDescription', ''), "Open Graph description"],
                "OG Image": [metadata.get('ogImage', ''), "Open Graph image URL"],
                "H1 Headings": [h1_count, h1_content],
                "H2 Headings": [h2_count, h2_content],
                "H3 Headings": [h3_count, h3_content],
                "Total Links": [len(links), "Total number of links found"],
                "Internal Links": [len(internal_links), '; '.join(l['url'] for l in internal_links)],
                "External Links": [len(external_links), '; '.join(l['url'] for l in external_links)],
                "Nofollow Links": [len(nofollow_links), '; '.join(l['url'] for l in nofollow_links)],
                "Total Images": [len(images), "Total number of images found"],
                "Images Missing Alt": [len([img for img in images if not img['has_alt']]), 
                                     '; '.join(img['src'] for img in images if not img['has_alt'])],
                "Images with Details": [len(images), '\n'.join(image_details)]
            }
            
            return analysis
            
        except Exception as e:
            print(f"\nError analyzing page: {str(e)}")
            sys.exit(1)

    def export_to_csv(self, analysis, url):
        """
        Export the analysis results to CSV in a transposed format with details
        Column A: Metric name
        Column B: Value
        Column C: Additional details/description
        
        The output filename is derived from the last part of the URL
        """
        try:
            # Extract the last part of the URL to use as filename
            url_path = urlparse(url).path
            filename = url_path.split('/')[-1]
            if not filename:  # Handle URLs ending in slash
                filename = 'index'
            if not filename.endswith('.html'):  # Handle URLs without extension
                filename += '.html'
            output_filename = f"seo_results_{filename}.csv"
            
            # Create output directory if it doesn't exist
            os.makedirs('results', exist_ok=True)
            output_path = os.path.join('results', output_filename)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value', 'Details'])  # Header row
                for key, (value, details) in analysis.items():
                    writer.writerow([key, value, details])
                print(f"\nResults exported to {output_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            sys.exit(1)

def main():
    """
    Main function to run the SEO crawler
    Supports both single URL and CSV file with URLs
    """
    if len(sys.argv) != 2:
        print("Usage: python seo_crawler.py <url_or_csv_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    
    # Initialize the analyzer
    analyzer = SEOAnalyzer()
    
    try:
        if input_path.endswith('.csv'):
            # Read URLs from CSV file
            df = pd.read_csv(input_path)
            if 'url' not in df.columns:
                raise ValueError("CSV file must contain a 'url' column")
            
            urls = df['url'].tolist()
            print(f"\nFound {len(urls)} URLs to analyze")
            
            # Process each URL
            for url in urls:
                print(f"\nAnalyzing {url}...")
                analysis = analyzer.analyze_page(url)
                analyzer.export_to_csv(analysis, url)
                
            print("\nAll URLs have been analyzed successfully!")
        else:
            # Treat input as a single URL
            url = input_path
            print(f"\nAnalyzing single URL: {url}")
            analysis = analyzer.analyze_page(url)
            analyzer.export_to_csv(analysis, url)
            print("\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"Error processing input: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 