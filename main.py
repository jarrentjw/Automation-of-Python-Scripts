"""
Main application entry point for SharePoint file automation.
"""
import yaml
import logging
import sys
from sharepoint_monitor import SharePointMonitor


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_file='config.yaml'):
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_file}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {str(e)}")
        sys.exit(1)


def main():
    """Main application entry point."""
    logger.info("SharePoint File Automation System Starting...")
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if 'automations' not in config:
        logger.error("No automations defined in configuration")
        sys.exit(1)
    
    enabled_automations = [a for a in config['automations'] if a.get('enabled', False)]
    logger.info(f"Loaded {len(enabled_automations)} enabled automation(s)")
    
    # Start monitor
    monitor = SharePointMonitor(config)
    monitor.start_monitoring()


if __name__ == '__main__':
    main()
