"""
SharePoint connector module for authenticating and interacting with SharePoint.
"""
import os
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from dotenv import load_dotenv


class SharePointConnector:
    """Handles SharePoint authentication and file operations."""
    
    def __init__(self):
        """Initialize SharePoint connector with credentials from environment."""
        load_dotenv()
        
        self.site_url = os.getenv('SHAREPOINT_SITE_URL')
        self.client_id = os.getenv('SHAREPOINT_CLIENT_ID')
        self.client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
        self.tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
        
        if not all([self.site_url, self.client_id, self.client_secret]):
            raise ValueError("Missing required SharePoint credentials in environment variables")
        
        self.ctx = None
    
    def connect(self):
        """Establish connection to SharePoint."""
        credentials = ClientCredential(self.client_id, self.client_secret)
        self.ctx = ClientContext(self.site_url).with_credentials(credentials)
        return self.ctx
    
    def get_library_files(self, library_name):
        """
        Get all files from a SharePoint library.
        
        Args:
            library_name: Name of the document library
            
        Returns:
            List of file objects
        """
        if not self.ctx:
            self.connect()
        
        library = self.ctx.web.lists.get_by_title(library_name)
        items = library.items.get().execute_query()
        return items
    
    def download_file(self, file_url, local_path):
        """
        Download a file from SharePoint to local path.
        
        Args:
            file_url: Server-relative URL of the file
            local_path: Local path where file should be saved
        """
        if not self.ctx:
            self.connect()
        
        response = self.ctx.web.get_file_by_server_relative_url(file_url)
        response.download(local_path).execute_query()
        
    def get_recent_files(self, library_name, minutes=5):
        """
        Get files uploaded in the last N minutes.
        
        Args:
            library_name: Name of the document library
            minutes: Number of minutes to look back
            
        Returns:
            List of recently added files
        """
        from datetime import datetime, timedelta
        
        if not self.ctx:
            self.connect()
        
        library = self.ctx.web.lists.get_by_title(library_name)
        items = library.items.get().execute_query()
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_files = []
        
        for item in items:
            if hasattr(item.properties, 'Created'):
                created = item.properties.get('Created', '')
                if created:
                    # Parse ISO format datetime
                    try:
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        if created_dt.replace(tzinfo=None) > cutoff_time:
                            recent_files.append(item)
                    except (ValueError, AttributeError):
                        continue
        
        return recent_files
