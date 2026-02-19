# SharePoint File Automation System

Automatically trigger Python scripts when files are added to SharePoint document libraries.

## Overview

This system monitors a SharePoint document library and automatically executes Python scripts when new files are detected. It's ideal for automating file processing tasks such as:

- Processing uploaded CSV/Excel files
- Converting document formats
- Extracting data from files
- Validating file contents
- Sending notifications
- Any custom file processing task

## Features

- **Automatic File Detection**: Monitors SharePoint libraries for new files
- **Flexible Configuration**: Define multiple automations with file patterns and folder filters
- **Script Execution**: Automatically runs Python scripts when matching files are detected
- **File Pattern Matching**: Support for wildcards (*.csv, *.xlsx, etc.)
- **Local File Download**: Downloads files from SharePoint for processing
- **Logging**: Comprehensive logging of all operations
- **Error Handling**: Robust error handling and timeout protection

## Prerequisites

- Python 3.7 or higher
- SharePoint Online with appropriate permissions
- Azure AD App Registration (for SharePoint authentication)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jarrentjw/Automation-of-Python-Scripts.git
cd Automation-of-Python-Scripts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your SharePoint credentials:
```
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_CLIENT_ID=your-client-id
SHAREPOINT_CLIENT_SECRET=your-client-secret
SHAREPOINT_TENANT_ID=your-tenant-id
MONITOR_LIBRARY=Shared Documents
POLL_INTERVAL=60
```

## SharePoint Setup

### 1. Register Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Enter a name (e.g., "SharePoint File Automation")
5. Set supported account types to "Accounts in this organizational directory only"
6. Click "Register"

### 2. Configure API Permissions

1. In your app registration, go to "API permissions"
2. Click "Add a permission" > "SharePoint" > "Application permissions"
3. Add these permissions:
   - `Sites.Read.All` - Read items in all site collections
   - `Sites.ReadWrite.All` - Read and write items in all site collections (if you need write access)
4. Click "Grant admin consent"

### 3. Create Client Secret

1. Go to "Certificates & secrets"
2. Click "New client secret"
3. Add a description and set expiration
4. Copy the secret value (you won't be able to see it again!)
5. Use this as `SHAREPOINT_CLIENT_SECRET` in your `.env` file

### 4. Get Required IDs

- **Client ID**: Found on the app registration overview page
- **Tenant ID**: Found on the Azure AD overview page
- **Site URL**: Your SharePoint site URL (e.g., `https://contoso.sharepoint.com/sites/mysite`)

## Configuration

Edit `config.yaml` to define your automations:

```yaml
automations:
  - name: "Process CSV Files"
    enabled: true
    trigger:
      file_pattern: "*.csv"
      folder: "Uploads"  # Optional: filter by folder
    script: "scripts/process_csv.py"
    args:
      - "--input"
      - "{file_path}"
  
  - name: "Convert Documents"
    enabled: true
    trigger:
      file_pattern: "*.docx"
      folder: ""
    script: "scripts/convert_document.py"
    args:
      - "{file_path}"
      - "{file_name}"
```

### Configuration Options

- **name**: Descriptive name for the automation
- **enabled**: Set to `true` to enable, `false` to disable
- **trigger.file_pattern**: Wildcard pattern for matching files (e.g., `*.csv`, `report_*.xlsx`)
- **trigger.folder**: Optional folder path filter (matches if folder path contains this string)
- **script**: Path to the Python script to execute
- **args**: List of arguments to pass to the script
  - `{file_path}`: Replaced with local path to downloaded file
  - `{file_name}`: Replaced with the file name
  - `{folder}`: Replaced with the SharePoint folder path

## Usage

### Start the Monitor

Run the main application:
```bash
python main.py
```

The monitor will:
1. Connect to SharePoint
2. Check for new files every `POLL_INTERVAL` seconds (default: 60)
3. Download matching files
4. Execute configured scripts
5. Log all operations

### Creating Custom Scripts

Create your automation scripts in the `scripts/` directory:

```python
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_file(file_path):
    logger.info(f"Processing: {file_path}")
    # Your processing logic here
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(1)
    
    file_path = sys.argv[2]  # Assuming --input argument
    success = process_file(file_path)
    sys.exit(0 if success else 1)
```

## Example Scripts

### Process CSV Files

The included `scripts/process_csv.py` demonstrates:
- Reading CSV files
- Extracting column information
- Counting rows
- Basic data validation

### Convert Documents

The included `scripts/convert_document.py` demonstrates:
- File type detection
- Document processing workflow
- Output file generation

## Monitoring and Logs

The system provides detailed logging:

```
2024-01-15 10:30:00 - SharePointMonitor - INFO - Starting SharePoint monitor...
2024-01-15 10:30:00 - SharePointMonitor - INFO - Connected to SharePoint successfully
2024-01-15 10:30:05 - SharePointMonitor - INFO - New file detected: sales_data.csv
2024-01-15 10:30:06 - SharePointMonitor - INFO - Downloading sales_data.csv from SharePoint...
2024-01-15 10:30:07 - ScriptExecutor - INFO - Executing: python scripts/process_csv.py --input downloaded_files/sales_data.csv
2024-01-15 10:30:08 - ScriptExecutor - INFO - Script executed successfully: Process CSV Files
```

## Troubleshooting

### Connection Issues

If you can't connect to SharePoint:
- Verify your credentials in `.env`
- Ensure API permissions are granted
- Check that the client secret hasn't expired
- Verify the site URL is correct

### Script Execution Failures

If scripts fail to execute:
- Check that the script path is correct in `config.yaml`
- Ensure the script has proper error handling
- Review the logs for specific error messages
- Test the script manually with a sample file

### Files Not Detected

If files aren't being detected:
- Verify the `MONITOR_LIBRARY` name matches your SharePoint library
- Check the `POLL_INTERVAL` - increase if needed
- Ensure file patterns match your uploaded files
- Check folder filters are correct

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SharePoint Online                     │
│                  (Document Library)                      │
└────────────────────┬────────────────────────────────────┘
                     │ Polls for new files
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SharePoint Monitor                          │
│  - Polls SharePoint at regular intervals                 │
│  - Detects new files                                     │
│  - Downloads files locally                               │
└────────────────────┬────────────────────────────────────┘
                     │ Triggers
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Script Executor                             │
│  - Matches files against patterns                        │
│  - Executes configured scripts                           │
│  - Manages script lifecycle                              │
└────────────────────┬────────────────────────────────────┘
                     │ Runs
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Custom Python Scripts                       │
│  - Process files                                         │
│  - Perform automation tasks                              │
│  - Generate outputs                                      │
└─────────────────────────────────────────────────────────┘
```

## Security Considerations

- Store credentials securely in `.env` file (never commit to git)
- Use the principle of least privilege for SharePoint permissions
- Regularly rotate client secrets
- Validate and sanitize file inputs in scripts
- Implement timeout protection for long-running scripts
- Review logs regularly for suspicious activity

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.