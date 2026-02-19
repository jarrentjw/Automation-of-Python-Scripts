"""
SharePoint file monitor that polls for new files and triggers automations.
"""
import time
import logging
import os
from datetime import datetime
from sharepoint_connector import SharePointConnector
from script_executor import ScriptExecutor
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SharePointMonitor:
    """Monitors SharePoint library for new files and triggers scripts."""
    
    def __init__(self, config):
        """
        Initialize the monitor.
        
        Args:
            config: Configuration dictionary
        """
        load_dotenv()
        
        self.config = config
        self.connector = SharePointConnector()
        self.executor = ScriptExecutor(config)
        
        self.library_name = os.getenv('MONITOR_LIBRARY', 'Shared Documents')
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '60'))
        self.processed_files = set()
        
        # Create download directory
        self.download_dir = os.path.join(os.getcwd(), 'downloaded_files')
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_file_locally(self, file_item):
        """
        Download a SharePoint file to local storage.
        
        Args:
            file_item: SharePoint file item
            
        Returns:
            Local file path or None if failed
        """
        try:
            file_name = file_item.properties.get('FileLeafRef', 'unknown')
            file_url = file_item.properties.get('FileRef', '')
            
            if not file_url:
                logger.error(f"No file URL found for {file_name}")
                return None
            
            local_path = os.path.join(self.download_dir, file_name)
            
            logger.info(f"Downloading {file_name} from SharePoint...")
            self.connector.download_file(file_url, local_path)
            logger.info(f"Downloaded to {local_path}")
            
            return local_path
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return None
    
    def process_new_files(self):
        """Check for new files and process them."""
        try:
            # Get recent files from SharePoint
            recent_files = self.connector.get_recent_files(
                self.library_name, 
                minutes=self.poll_interval // 60 + 1
            )
            
            logger.info(f"Found {len(recent_files)} recent files")
            
            for file_item in recent_files:
                file_id = file_item.properties.get('Id', '')
                file_name = file_item.properties.get('FileLeafRef', '')
                
                # Skip if already processed
                if file_id in self.processed_files:
                    continue
                
                logger.info(f"New file detected: {file_name}")
                
                # Download file
                local_path = self.download_file_locally(file_item)
                
                if local_path:
                    # Prepare file info
                    file_info = {
                        'name': file_name,
                        'path': local_path,
                        'folder': file_item.properties.get('FileDirRef', ''),
                        'id': file_id
                    }
                    
                    # Process with script executor
                    results = self.executor.process_file(file_info)
                    
                    # Log results
                    for result in results:
                        logger.info(
                            f"Automation '{result['automation']}': "
                            f"{'SUCCESS' if result['success'] else 'FAILED'}"
                        )
                
                # Mark as processed
                self.processed_files.add(file_id)
                
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
    
    def start_monitoring(self):
        """Start the monitoring loop."""
        logger.info(f"Starting SharePoint monitor...")
        logger.info(f"Monitoring library: {self.library_name}")
        logger.info(f"Poll interval: {self.poll_interval} seconds")
        
        # Initial connection
        try:
            self.connector.connect()
            logger.info("Connected to SharePoint successfully")
        except Exception as e:
            logger.error(f"Failed to connect to SharePoint: {str(e)}")
            return
        
        logger.info("Monitor started. Press Ctrl+C to stop.")
        
        try:
            while True:
                logger.info(f"Checking for new files at {datetime.now()}")
                self.process_new_files()
                
                logger.info(f"Waiting {self.poll_interval} seconds until next check...")
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
        except Exception as e:
            logger.error(f"Monitor error: {str(e)}")
            raise
