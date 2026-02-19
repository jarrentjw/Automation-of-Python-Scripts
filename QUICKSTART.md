# Quick Start Guide

Get started with SharePoint File Automation in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up SharePoint Credentials

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Fill in your SharePoint credentials in `.env`:
   - Get these from your Azure AD App Registration
   - See README.md for detailed setup instructions

## Step 3: Configure Your Automation

Edit `config.yaml` to define what should happen when files are uploaded:

```yaml
automations:
  - name: "Process CSV Files"
    enabled: true
    trigger:
      file_pattern: "*.csv"
      folder: ""
    script: "scripts/process_csv.py"
    args:
      - "--input"
      - "{file_path}"
```

## Step 4: Test with Example Script

The project includes example scripts in the `scripts/` folder:
- `process_csv.py` - Processes CSV files
- `convert_document.py` - Converts documents

## Step 5: Run the Monitor

```bash
python main.py
```

The system will now:
- Connect to SharePoint
- Monitor for new files
- Execute your scripts automatically

## What's Next?

1. **Create custom scripts** - Add your own Python scripts in the `scripts/` folder
2. **Customize automations** - Edit `config.yaml` to match your needs
3. **Monitor logs** - Watch the console for activity and errors
4. **Add more patterns** - Create multiple automations for different file types

## Quick Test

To test if everything works:

1. Upload a CSV file to your SharePoint library
2. Watch the console for detection and processing
3. Check the `downloaded_files/` folder for the downloaded file
4. Review the logs for script execution results

## Need Help?

- Check README.md for detailed documentation
- Review the example scripts for guidance
- Check logs for error messages
- Open an issue on GitHub
