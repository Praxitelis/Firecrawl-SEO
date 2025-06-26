#!/usr/bin/env python3
"""
Master SEO Analyzer - A comprehensive tool for SEO analysis and reporting
Combines multiple analysis modules into a single workflow
"""

import argparse
import sys
import os
from datetime import datetime
import importlib.util

# Import our modules
from seo_crawler import SEOAnalyzer
from compile_results import ResultsCompiler

class MasterSEOAnalyzer:
    def __init__(self):
        """
        Initialize the Master SEO Analyzer
        """
        self.analyzer = SEOAnalyzer()
        self.compiler = ResultsCompiler()
        self.results_dir = 'results'
        
    def analyze_single_url(self, url):
        """
        Analyze a single URL
        """
        print(f"\n{'='*60}")
        print(f"ANALYZING SINGLE URL: {url}")
        print(f"{'='*60}")
        
        try:
            analysis = self.analyzer.analyze_page(url)
            self.analyzer.export_to_csv(analysis, url)
            print(f"\n✅ Single URL analysis completed successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error analyzing URL: {str(e)}")
            return False
    
    def analyze_batch_urls(self, csv_file):
        """
        Analyze multiple URLs from a CSV file
        """
        print(f"\n{'='*60}")
        print(f"BATCH ANALYSIS FROM: {csv_file}")
        print(f"{'='*60}")
        
        try:
            import pandas as pd
            
            # Read URLs from CSV file
            df = pd.read_csv(csv_file)
            if 'url' not in df.columns:
                raise ValueError("CSV file must contain a 'url' column")
            
            urls = df['url'].tolist()
            print(f"Found {len(urls)} URLs to analyze")
            
            success_count = 0
            failed_urls = []
            
            # Process each URL
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] Analyzing: {url}")
                try:
                    analysis = self.analyzer.analyze_page(url)
                    self.analyzer.export_to_csv(analysis, url)
                    success_count += 1
                    print(f"✅ Success")
                except Exception as e:
                    print(f"❌ Failed: {str(e)}")
                    failed_urls.append(url)
            
            print(f"\n{'='*60}")
            print(f"BATCH ANALYSIS COMPLETED")
            print(f"{'='*60}")
            print(f"✅ Successful: {success_count}/{len(urls)}")
            if failed_urls:
                print(f"❌ Failed: {len(failed_urls)}")
                print("Failed URLs:")
                for url in failed_urls:
                    print(f"  - {url}")
            
            return success_count == len(urls)
            
        except Exception as e:
            print(f"\n❌ Error in batch analysis: {str(e)}")
            return False
    
    def compile_results(self):
        """
        Compile all results into Excel
        """
        print(f"\n{'='*60}")
        print(f"COMPILING RESULTS TO EXCEL")
        print(f"{'='*60}")
        
        try:
            self.compiler.compile_to_excel()
            print(f"\n✅ Results compilation completed successfully!")
            return True
        except Exception as e:
            print(f"\n❌ Error compiling results: {str(e)}")
            return False
    
    def run_full_workflow(self, input_source):
        """
        Run the complete workflow: analyze URLs and compile results
        """
        print(f"\n{'='*60}")
        print(f"MASTER SEO ANALYZER - FULL WORKFLOW")
        print(f"{'='*60}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        success = False
        
        try:
            # Step 1: Analyze URLs
            if input_source.endswith('.csv'):
                success = self.analyze_batch_urls(input_source)
            else:
                success = self.analyze_single_url(input_source)
            
            if not success:
                print(f"\n❌ URL analysis failed. Stopping workflow.")
                return False
            
            # Step 2: Compile results
            print(f"\n{'='*60}")
            print(f"PROCEEDING TO RESULTS COMPILATION")
            print(f"{'='*60}")
            
            compile_success = self.compile_results()
            
            if compile_success:
                print(f"\n{'='*60}")
                print(f"🎉 FULL WORKFLOW COMPLETED SUCCESSFULLY!")
                print(f"{'='*60}")
                print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                print(f"\n❌ Results compilation failed.")
                return False
                
        except Exception as e:
            print(f"\n❌ Workflow error: {str(e)}")
            return False

def add_future_module(module_name, module_function):
    """
    Template for adding future modules
    This function can be expanded to include additional analysis modules
    """
    print(f"Future module '{module_name}' would be called here")
    # Example: module_function()
    pass

def main():
    """
    Main function with command line interface
    """
    parser = argparse.ArgumentParser(
        description="Master SEO Analyzer - Comprehensive SEO analysis and reporting tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single URL
  python master_seo_analyzer.py https://example.com
  
  # Analyze URLs from CSV file
  python master_seo_analyzer.py urls.csv
  
  # Analyze single URL and compile results
  python master_seo_analyzer.py --full-workflow https://example.com
  
  # Analyze batch URLs and compile results
  python master_seo_analyzer.py --full-workflow urls.csv
  
  # Only compile existing results
  python master_seo_analyzer.py --compile-only
        """
    )
    
    parser.add_argument(
        'input_source',
        nargs='?',
        help='URL to analyze or CSV file with URLs'
    )
    
    parser.add_argument(
        '--full-workflow',
        action='store_true',
        help='Run complete workflow: analyze URLs and compile results'
    )
    
    parser.add_argument(
        '--compile-only',
        action='store_true',
        help='Only compile existing results to Excel (skip URL analysis)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Master SEO Analyzer v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Initialize the master analyzer
    master = MasterSEOAnalyzer()
    
    try:
        if args.compile_only:
            # Only compile results
            success = master.compile_results()
            return 0 if success else 1
            
        elif args.full_workflow:
            # Run complete workflow
            if not args.input_source:
                print("❌ Error: Input source required for full workflow")
                print("Use: python master_seo_analyzer.py --full-workflow <url_or_csv>")
                return 1
            
            success = master.run_full_workflow(args.input_source)
            return 0 if success else 1
            
        elif args.input_source:
            # Analyze only (no compilation)
            if args.input_source.endswith('.csv'):
                success = master.analyze_batch_urls(args.input_source)
            else:
                success = master.analyze_single_url(args.input_source)
            return 0 if success else 1
            
        else:
            # No arguments provided
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 