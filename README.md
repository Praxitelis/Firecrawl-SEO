# Firecrawl SEO Analyzer

A comprehensive SEO analysis tool that uses the Firecrawl API to analyze web pages and extract detailed SEO metrics.

## Features

- **Comprehensive SEO Analysis**: Analyzes titles, meta descriptions, headings, links, images, and more
- **Advanced SEO Elements**: Captures schema markup, canonical tags, hreflang tags, and image dimensions
- **Batch Processing**: Analyze multiple URLs from a CSV file
- **Detailed Output**: Three-column format with metrics, values, and detailed descriptions
- **Excel Compilation**: Compile all results into a single Excel file with multiple sheets

## Installation

1. Clone the repository
2. Install required packages:
   ```bash
   pip install requests python-dotenv pandas openpyxl
   ```
3. Create a `.env` file with your Firecrawl API key:
   ```
   FIRECRAWL_API_KEY=your_api_key_here
   ```

## Usage

### Single URL Analysis

```bash
python seo_crawler.py https://example.com
```

### Batch Analysis from CSV

1. Create a CSV file with URLs:
   ```csv
   url
   https://example1.com
   https://example2.com
   ```

2. Run the analysis:
   ```bash
   python seo_crawler.py urls_to_crawl.csv
   ```

### Compile Results to Excel

After running the SEO analysis, compile all results into a single Excel file:

```bash
python compile_results.py
```

## Output Format

### Individual CSV Files
Each URL analysis creates a CSV file with three columns:
- **Column A**: Metric name
- **Column B**: Value
- **Column C**: Additional details/description

### Excel Compilation
The compiler creates an Excel file with multiple sheets:

1. **Summary Sheet**: Key metrics overview for all URLs
   - URL, Title, Meta Description Length
   - Canonical URL, Heading counts
   - Link counts (total, internal, external, nofollow)
   - Image counts and missing alt text
   - Schema markup and hreflang counts

2. **Comparison Sheet**: Side-by-side metric comparison
   - All metrics as rows
   - URLs as columns
   - Easy comparison across pages

3. **Individual Sheets**: Detailed analysis for each URL
   - Complete analysis in the same format as CSV files

## Metrics Analyzed

### Basic SEO
- Title and meta description (with length analysis)
- Meta keywords, robots, viewport
- Canonical URL
- Open Graph tags (title, description, image)

### Content Structure
- H1, H2, H3 heading counts and content
- Total links (internal, external, nofollow)
- Image analysis (count, alt text, dimensions)

### Advanced SEO
- Schema markup (count and types)
- Hreflang tags (count and language variants)
- Page load time and status codes

## File Structure

```
├── seo_crawler.py          # Main SEO analysis script
├── compile_results.py      # Excel compilation script
├── urls_to_crawl.csv       # Input URLs file
├── results/                # Individual CSV results
│   ├── seo_results_page1.csv
│   ├── seo_results_page2.csv
│   └── ...
└── seo_analysis_summary_YYYYMMDD_HHMMSS.xlsx  # Compiled Excel file
```

## Notes

- The script uses Firecrawl's `rawHtml` format to ensure complete HTML including head sections
- Canonical tags are extracted from both metadata and HTML parsing
- Image dimensions are captured where available in the HTML
- All URLs are made absolute for proper analysis
- Excel sheet names are automatically cleaned to comply with Excel limitations

## Requirements

- Python 3.7+
- Firecrawl API key
- Internet connection for API calls

## Analysis Components

The tool performs the following checks:

### Meta Tags Analysis
- Title tag presence and length (optimal: 30-60 characters)
- Meta description presence and length (optimal: 120-155 characters)
- Keywords meta tag
- Robots meta tag
- Viewport meta tag
- Character encoding

### Heading Structure
- H1 tag presence and uniqueness
- Heading hierarchy
- Heading count by level

### Image Optimization
- Alt tag presence
- Empty alt tags detection
- Total image count

### Link Analysis
- Internal vs external links ratio
- Nofollow links detection
- Broken links detection
- Link text analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 