import pandas as pd
import os
import glob
from datetime import datetime
import re

class ResultsCompiler:
    def __init__(self, results_dir='results'):
        """
        Initialize the Results Compiler
        """
        self.results_dir = results_dir
        self.output_file = f"seo_analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
    def load_csv_files(self):
        """
        Load all CSV files from the results directory
        """
        csv_files = glob.glob(os.path.join(self.results_dir, "*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in {self.results_dir}")
        
        dataframes = {}
        for csv_file in csv_files:
            # Extract URL from filename
            filename = os.path.basename(csv_file)
            url_match = re.search(r'seo_results_(.+)\.csv', filename)
            if url_match:
                url_name = url_match.group(1)
            else:
                url_name = filename.replace('.csv', '')
            
            # Load CSV data
            df = pd.read_csv(csv_file)
            dataframes[url_name] = df
            
        return dataframes
    
    def create_summary_sheet(self, dataframes):
        """
        Create a summary sheet with key metrics for all URLs
        """
        summary_data = []
        
        for url_name, df in dataframes.items():
            # Convert dataframe to dictionary for easier access
            data_dict = dict(zip(df['Metric'], df['Value']))
            
            # Extract key metrics
            summary_row = {
                'URL Name': url_name,
                'URL': data_dict.get('URL', ''),
                'Title': data_dict.get('Title', ''),
                'Title Length': len(str(data_dict.get('Title', ''))),
                'Meta Description Length': len(str(data_dict.get('Meta Description', ''))),
                'Canonical URL': data_dict.get('Canonical URL', ''),
                'H1 Count': data_dict.get('H1 Headings', 0),
                'H2 Count': data_dict.get('H2 Headings', 0),
                'H3 Count': data_dict.get('H3 Headings', 0),
                'Total Links': data_dict.get('Total Links', 0),
                'Internal Links': data_dict.get('Internal Links', 0),
                'External Links': data_dict.get('External Links', 0),
                'Nofollow Links': data_dict.get('Nofollow Links', 0),
                'Total Images': data_dict.get('Total Images', 0),
                'Images Missing Alt': data_dict.get('Images Missing Alt', 0),
                'Schema Markup Count': data_dict.get('Schema Markup', 0),
                'Hreflang Count': data_dict.get('Hreflang Tags', 0),
                'Status Code': data_dict.get('Status Code', ''),
                'Load Time': data_dict.get('Load Time', ''),
                'Robots Meta': data_dict.get('Robots Meta', ''),
                'OG Title': data_dict.get('OG Title', ''),
                'OG Description': data_dict.get('OG Description', ''),
                'OG Image': data_dict.get('OG Image', '')
            }
            summary_data.append(summary_row)
        
        return pd.DataFrame(summary_data)
    
    def create_comparison_sheet(self, dataframes):
        """
        Create a comparison sheet with metrics as rows and URLs as columns
        """
        # Get all unique metrics
        all_metrics = set()
        for df in dataframes.values():
            all_metrics.update(df['Metric'].tolist())
        
        # Create comparison dataframe
        comparison_data = {'Metric': sorted(all_metrics)}
        
        for url_name, df in dataframes.items():
            metric_dict = dict(zip(df['Metric'], df['Value']))
            comparison_data[url_name] = [metric_dict.get(metric, '') for metric in sorted(all_metrics)]
        
        return pd.DataFrame(comparison_data)
    
    def compile_to_excel(self):
        """
        Compile all results into a single Excel file
        """
        try:
            print(f"Loading CSV files from {self.results_dir}...")
            dataframes = self.load_csv_files()
            
            print(f"Found {len(dataframes)} CSV files to compile")
            
            # Create Excel writer
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                
                # Create Summary Sheet
                print("Creating Summary Sheet...")
                summary_df = self.create_summary_sheet(dataframes)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Create Comparison Sheet
                print("Creating Comparison Sheet...")
                comparison_df = self.create_comparison_sheet(dataframes)
                comparison_df.to_excel(writer, sheet_name='Comparison', index=False)
                
                # Create individual detailed sheets
                print("Creating detailed sheets for each URL...")
                for url_name, df in dataframes.items():
                    # Clean sheet name (Excel has limitations on sheet names)
                    sheet_name = url_name[:31]  # Excel sheet names limited to 31 characters
                    sheet_name = re.sub(r'[\\/*?:\[\]]', '_', sheet_name)  # Remove invalid characters
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths for all sheets
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"\nExcel file created successfully: {self.output_file}")
            print(f"Total sheets created: {len(dataframes) + 2}")  # +2 for Summary and Comparison
            print("\nSheets included:")
            print("- Summary: Key metrics overview")
            print("- Comparison: Side-by-side metric comparison")
            for url_name in dataframes.keys():
                print(f"- {url_name}: Detailed analysis")
                
        except Exception as e:
            print(f"Error compiling results: {str(e)}")
            raise

def main():
    """
    Main function to run the results compiler
    """
    try:
        compiler = ResultsCompiler()
        compiler.compile_to_excel()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 