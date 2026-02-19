"""
Example script: Process CSV files uploaded to SharePoint.

This script demonstrates how to process CSV files that are uploaded to SharePoint.
It reads the CSV file and performs basic analysis.
"""
import sys
import csv
import logging
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_csv(file_path):
    """
    Process a CSV file.
    
    Args:
        file_path: Path to the CSV file
    """
    logger.info(f"Processing CSV file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            logger.info(f"CSV contains {len(rows)} rows")
            
            if rows:
                logger.info(f"Columns: {', '.join(rows[0].keys())}")
                
                # Example: Count rows
                logger.info(f"Total records: {len(rows)}")
                
                # Example: Show first few rows
                logger.info("First 3 rows:")
                for i, row in enumerate(rows[:3], 1):
                    logger.info(f"  Row {i}: {row}")
            
            logger.info("CSV processing completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        logger.error("Usage: python process_csv.py --input <file_path>")
        sys.exit(1)
    
    if sys.argv[1] != '--input':
        logger.error("Expected --input argument")
        sys.exit(1)
    
    file_path = sys.argv[2]
    
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    success = process_csv(file_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
