# Advanced Configuration Guide

This guide covers advanced configuration options and use cases.

## Multiple Automations

You can define multiple automations in `config.yaml`:

```yaml
automations:
  # Process sales reports
  - name: "Sales Report Processing"
    enabled: true
    trigger:
      file_pattern: "sales_*.csv"
      folder: "Reports/Sales"
    script: "scripts/process_sales.py"
    args:
      - "--input"
      - "{file_path}"
      - "--output"
      - "processed/sales/"
  
  # Process HR data
  - name: "HR Data Import"
    enabled: true
    trigger:
      file_pattern: "employees_*.xlsx"
      folder: "HR/Uploads"
    script: "scripts/import_hr_data.py"
    args:
      - "{file_path}"
  
  # Archive documents
  - name: "Document Archival"
    enabled: true
    trigger:
      file_pattern: "*.pdf"
      folder: "Archive"
    script: "scripts/archive_document.py"
    args:
      - "{file_path}"
      - "{file_name}"
```

## File Pattern Examples

### Exact extension match
```yaml
file_pattern: "*.csv"      # Matches: data.csv, report.csv
file_pattern: "*.xlsx"     # Matches: sales.xlsx, budget.xlsx
file_pattern: "*.pdf"      # Matches: document.pdf, invoice.pdf
```

### Prefix match
```yaml
file_pattern: "report_*"   # Matches: report_jan.csv, report_2024.xlsx
file_pattern: "invoice_*"  # Matches: invoice_123.pdf, invoice_abc.docx
```

### Complex patterns
```yaml
file_pattern: "sales_*.csv"     # Matches: sales_jan.csv, sales_2024.csv
file_pattern: "report_????.*"   # Matches: report_2024.csv, report_0001.xlsx
```

### Match all files
```yaml
file_pattern: "*"          # Matches: any file
```

## Folder Filtering

### Exact folder name
```yaml
folder: "Uploads"          # Matches paths containing "Uploads"
```

### Nested folders
```yaml
folder: "Reports/Sales"    # Matches paths containing "Reports/Sales"
```

### No filter (all folders)
```yaml
folder: ""                 # Matches files in any folder
```

## Script Arguments

### Available placeholders

- `{file_path}` - Full local path to downloaded file
- `{file_name}` - Just the filename
- `{folder}` - SharePoint folder path

### Examples

```yaml
# Simple input argument
args:
  - "--input"
  - "{file_path}"

# Multiple arguments
args:
  - "{file_path}"
  - "--output"
  - "processed/{file_name}"
  - "--folder"
  - "{folder}"

# No arguments
args: []
```

## Environment Variables

### Required variables

```bash
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_TENANT_ID=your-tenant-id
```

### Optional variables

```bash
# Document library to monitor (default: "Shared Documents")
MONITOR_LIBRARY=Shared Documents

# Polling interval in seconds (default: 60)
POLL_INTERVAL=60

# Set to override default download directory
# DOWNLOAD_DIR=/custom/path/to/downloads
```

## Custom Script Development

### Script template

```python
#!/usr/bin/env python3
"""
Description of what this script does.
"""
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_file(file_path):
    """
    Process the uploaded file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Processing: {file_path}")
    
    try:
        # Your processing logic here
        
        logger.info("Processing completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 3:
        logger.error("Usage: python script.py --input <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[2]
    
    # Validate file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Process the file
    success = process_file(file_path)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

### Best practices for scripts

1. **Use logging** - Log important operations and errors
2. **Validate inputs** - Check file exists and is readable
3. **Handle errors gracefully** - Use try/except blocks
4. **Exit with proper codes** - 0 for success, non-zero for failure
5. **Keep it focused** - One script should do one thing well
6. **Add docstrings** - Document what the script does

## Advanced Use Cases

### Email notification on file upload

```python
# scripts/send_notification.py
import smtplib
from email.mime.text import MIMEText

def send_email(file_name):
    msg = MIMEText(f"New file uploaded: {file_name}")
    msg['Subject'] = 'SharePoint File Upload'
    msg['From'] = 'automation@company.com'
    msg['To'] = 'admin@company.com'
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)
```

### Database import

```python
# scripts/import_to_database.py
import pandas as pd
import sqlalchemy

def import_csv(file_path):
    df = pd.read_csv(file_path)
    engine = sqlalchemy.create_engine('postgresql://...')
    df.to_sql('uploaded_data', engine, if_exists='append')
```

### File transformation

```python
# scripts/transform_data.py
import pandas as pd

def transform_csv(file_path):
    df = pd.read_csv(file_path)
    # Apply transformations
    df['processed_date'] = pd.Timestamp.now()
    df = df[df['amount'] > 0]  # Filter
    # Save transformed data
    output = file_path.replace('.csv', '_processed.csv')
    df.to_csv(output, index=False)
```

### API integration

```python
# scripts/post_to_api.py
import requests
import json

def post_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    response = requests.post(
        'https://api.example.com/data',
        json=data,
        headers={'Authorization': 'Bearer TOKEN'}
    )
    response.raise_for_status()
```

## Running in Production

### As a systemd service (Linux)

Create `/etc/systemd/system/sharepoint-automation.service`:

```ini
[Unit]
Description=SharePoint File Automation
After=network.target

[Service]
Type=simple
User=automation
WorkingDirectory=/opt/sharepoint-automation
ExecStart=/usr/bin/python3 /opt/sharepoint-automation/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sharepoint-automation
sudo systemctl start sharepoint-automation
sudo systemctl status sharepoint-automation
```

### As a Docker container

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t sharepoint-automation .
docker run -d --env-file .env sharepoint-automation
```

### Using PM2 (Node.js process manager)

```bash
npm install -g pm2
pm2 start main.py --interpreter python3 --name sharepoint-automation
pm2 save
pm2 startup
```

## Monitoring and Maintenance

### Log rotation

Use logrotate to manage log files:

```bash
# /etc/logrotate.d/sharepoint-automation
/opt/sharepoint-automation/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Health checks

Add to your monitoring system:

```bash
# Check if process is running
ps aux | grep "python.*main.py" | grep -v grep

# Check recent activity
tail -n 20 logs/automation.log | grep "New file detected"
```

### Cleanup old files

Add cron job to clean downloaded files:

```bash
# /etc/cron.daily/cleanup-downloads
#!/bin/bash
find /opt/sharepoint-automation/downloaded_files -mtime +7 -delete
```

## Security Best Practices

1. **Protect credentials**
   - Never commit .env file
   - Use environment variables in production
   - Rotate secrets regularly

2. **Limit permissions**
   - Use minimal SharePoint permissions needed
   - Run with dedicated service account
   - Restrict file system access

3. **Validate inputs**
   - Check file types in scripts
   - Sanitize file names
   - Limit file sizes

4. **Monitor activity**
   - Review logs regularly
   - Set up alerts for failures
   - Track processed files

5. **Update dependencies**
   - Keep Python packages updated
   - Monitor security advisories
   - Test updates in staging first
