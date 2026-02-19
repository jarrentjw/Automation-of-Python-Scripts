"""
Script executor module for running Python scripts based on file events.
"""
import subprocess
import logging
import os
import fnmatch
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScriptExecutor:
    """Executes Python scripts based on configuration."""
    
    def __init__(self, config):
        """
        Initialize the script executor.
        
        Args:
            config: Configuration dictionary containing automation rules
        """
        self.config = config
        self.automations = config.get('automations', [])
    
    def match_file(self, file_info, automation):
        """
        Check if a file matches the automation trigger criteria.
        
        Args:
            file_info: Dictionary with file information (name, path, folder)
            automation: Automation configuration
            
        Returns:
            True if file matches, False otherwise
        """
        trigger = automation.get('trigger', {})
        file_pattern = trigger.get('file_pattern', '*')
        folder = trigger.get('folder', '')
        
        # Check file pattern
        if not fnmatch.fnmatch(file_info['name'], file_pattern):
            return False
        
        # Check folder if specified
        if folder and folder not in file_info.get('folder', ''):
            return False
        
        return True
    
    def execute_script(self, automation, file_info):
        """
        Execute a script with the given file information.
        
        Args:
            automation: Automation configuration
            file_info: Dictionary with file information
            
        Returns:
            Tuple of (success, output/error message)
        """
        if not automation.get('enabled', False):
            logger.info(f"Automation '{automation['name']}' is disabled, skipping")
            return False, "Automation disabled"
        
        script_path = automation.get('script')
        if not script_path:
            logger.error(f"No script specified for automation '{automation['name']}'")
            return False, "No script specified"
        
        # Check if script exists
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
            return False, f"Script not found: {script_path}"
        
        # Prepare arguments
        args = automation.get('args', [])
        processed_args = []
        
        for arg in args:
            # Replace placeholders with actual file information
            processed_arg = arg.format(
                file_path=file_info.get('path', ''),
                file_name=file_info.get('name', ''),
                folder=file_info.get('folder', '')
            )
            processed_args.append(processed_arg)
        
        # Build command
        cmd = ['python', script_path] + processed_args
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Script executed successfully: {automation['name']}")
                return True, result.stdout
            else:
                logger.error(f"Script failed: {automation['name']}\n{result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"Script timed out: {automation['name']}")
            return False, "Script execution timed out"
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return False, str(e)
    
    def process_file(self, file_info):
        """
        Process a file by executing matching automations.
        
        Args:
            file_info: Dictionary with file information
            
        Returns:
            List of execution results
        """
        results = []
        
        logger.info(f"Processing file: {file_info['name']}")
        
        for automation in self.automations:
            if self.match_file(file_info, automation):
                logger.info(f"File matches automation: {automation['name']}")
                success, output = self.execute_script(automation, file_info)
                results.append({
                    'automation': automation['name'],
                    'success': success,
                    'output': output
                })
        
        if not results:
            logger.info(f"No matching automations for file: {file_info['name']}")
        
        return results
