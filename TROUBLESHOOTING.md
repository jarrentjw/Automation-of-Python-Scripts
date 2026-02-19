# Troubleshooting Guide

Common issues and solutions for the SharePoint File Automation system.

## Installation Issues

### Problem: pip install fails for Office365-REST-Python-Client

**Solution:**
```bash
# Try upgrading pip first
pip install --upgrade pip

# Install with specific version
pip install Office365-REST-Python-Client==2.5.3
```

### Problem: Python version compatibility

**Solution:**
This system requires Python 3.7 or higher. Check your version:
```bash
python --version
```

If you have an older version, install Python 3.7+ from python.org.

## Connection Issues

### Problem: "Failed to connect to SharePoint"

**Possible causes and solutions:**

1. **Invalid credentials in .env file**
   - Double-check SHAREPOINT_CLIENT_ID and SHAREPOINT_CLIENT_SECRET
   - Ensure there are no extra spaces or quotes
   - Verify the values match your Azure AD app registration

2. **Incorrect site URL**
   - Ensure SHAREPOINT_SITE_URL is complete and correct
   - Format: `https://yourtenant.sharepoint.com/sites/yoursite`
   - Don't include trailing slashes

3. **Missing or expired permissions**
   - Go to Azure AD > App registrations > Your app > API permissions
   - Ensure Sites.Read.All or Sites.ReadWrite.All is granted
   - Click "Grant admin consent" if needed

4. **Expired client secret**
   - In Azure AD, check if your client secret has expired
   - Generate a new secret if needed
   - Update SHAREPOINT_CLIENT_SECRET in .env

### Problem: "Authentication failed" or 401 Unauthorized

**Solution:**
This usually indicates permission issues.

1. Verify API permissions in Azure AD:
   - Sites.Read.All (minimum)
   - Sites.ReadWrite.All (if you need to modify files)

2. Ensure admin consent has been granted:
   - Go to API permissions in Azure AD
   - Click "Grant admin consent for [organization]"

3. Check tenant ID:
   - Verify SHAREPOINT_TENANT_ID matches your Azure AD tenant

## File Detection Issues

### Problem: Files are uploaded but not detected

**Possible causes and solutions:**

1. **Incorrect library name**
   ```bash
   # In .env, ensure MONITOR_LIBRARY matches your SharePoint library name exactly
   MONITOR_LIBRARY=Shared Documents
   ```

2. **Poll interval too long**
   ```bash
   # Reduce poll interval in .env (in seconds)
   POLL_INTERVAL=30
   ```

3. **File pattern doesn't match**
   - Check config.yaml file_pattern
   - Use `*` to match all files
   - Example: `*.csv` matches only CSV files

4. **Folder filter too restrictive**
   - In config.yaml, check the folder parameter
   - Empty string `""` matches all folders
   - Partial matches are supported (e.g., "Uploads" matches "Shared Documents/Uploads")

### Problem: Same files being processed multiple times

**Solution:**
This shouldn't happen as files are tracked by ID. If it does:

1. Check the logs for errors during processing
2. Ensure the script completes successfully
3. The processed_files set is maintained in memory - restart clears it

## Script Execution Issues

### Problem: "Script not found" error

**Possible causes:**

1. **Incorrect path in config.yaml**
   ```yaml
   # Use relative path from project root
   script: "scripts/process_csv.py"
   # Not: "process_csv.py" or "/full/path/to/script.py"
   ```

2. **Script file doesn't exist**
   ```bash
   # Verify the script exists
   ls -la scripts/
   ```

### Problem: Script runs but produces errors

**Debugging steps:**

1. **Test the script manually:**
   ```bash
   python scripts/process_csv.py --input sample_data.csv
   ```

2. **Check script arguments in config.yaml:**
   ```yaml
   args:
     - "--input"
     - "{file_path}"  # Ensure placeholders are correct
   ```

3. **Review script logs:**
   - Scripts should log to stdout/stderr
   - Check main.py output for script output

4. **Add error handling to your script:**
   ```python
   try:
       # Your processing code
       pass
   except Exception as e:
       logger.error(f"Error: {str(e)}")
       sys.exit(1)
   ```

### Problem: Script timeout

**Solution:**
The default timeout is 300 seconds (5 minutes).

1. **Optimize your script** - Make it more efficient
2. **Or increase timeout in script_executor.py:**
   ```python
   result = subprocess.run(
       cmd,
       capture_output=True,
       text=True,
       timeout=600  # Increase to 10 minutes
   )
   ```

## Configuration Issues

### Problem: "No automations defined in configuration"

**Solution:**
Check config.yaml format:

```yaml
automations:
  - name: "My Automation"
    enabled: true
    trigger:
      file_pattern: "*.csv"
      folder: ""
    script: "scripts/my_script.py"
    args: []
```

Ensure:
- Proper YAML indentation (use spaces, not tabs)
- All required fields are present
- File is saved with .yaml extension

### Problem: Automation not triggering

**Checklist:**

1. **Is it enabled?**
   ```yaml
   enabled: true  # Not false
   ```

2. **Does the file pattern match?**
   ```yaml
   file_pattern: "*.csv"  # Matches test.csv, data.csv, etc.
   file_pattern: "report_*.xlsx"  # Matches report_jan.xlsx, etc.
   ```

3. **Does the folder filter match?**
   ```yaml
   folder: ""  # Matches all folders
   folder: "Uploads"  # Matches paths containing "Uploads"
   ```

## Performance Issues

### Problem: System is slow or uses too much memory

**Solutions:**

1. **Increase poll interval:**
   ```bash
   # In .env
   POLL_INTERVAL=120  # Check every 2 minutes instead of 1
   ```

2. **Limit file history:**
   The monitor keeps track of processed files. For long-running instances:
   - Restart periodically to clear the processed_files set
   - Or modify sharepoint_monitor.py to limit set size

3. **Clean up downloaded files:**
   ```bash
   # Files accumulate in downloaded_files/
   # Periodically clean up old files
   rm downloaded_files/*
   ```

## Logging and Debugging

### Enable detailed logging

Modify the logging level in main.py:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Save logs to file

Add file handler to main.py:

```python
import logging

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
```

## Still Having Issues?

1. **Check the logs** - Review console output for error messages
2. **Test components individually:**
   - Test SharePoint connection
   - Test script execution manually
   - Validate config.yaml syntax
3. **Search existing issues** on GitHub
4. **Open a new issue** with:
   - Error message
   - Relevant logs
   - Steps to reproduce
   - Environment details (Python version, OS, etc.)
