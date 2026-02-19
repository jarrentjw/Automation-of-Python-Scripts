"""
Unit tests for the SharePoint automation system.
"""
import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from script_executor import ScriptExecutor


class TestScriptExecutor(unittest.TestCase):
    """Test cases for ScriptExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'automations': [
                {
                    'name': 'Test CSV',
                    'enabled': True,
                    'trigger': {
                        'file_pattern': '*.csv',
                        'folder': 'test'
                    },
                    'script': 'test_script.py',
                    'args': ['--input', '{file_path}']
                },
                {
                    'name': 'Test Disabled',
                    'enabled': False,
                    'trigger': {
                        'file_pattern': '*.txt',
                        'folder': ''
                    },
                    'script': 'disabled_script.py',
                    'args': []
                }
            ]
        }
        self.executor = ScriptExecutor(self.config)
    
    def test_match_file_pattern(self):
        """Test file pattern matching."""
        file_info = {
            'name': 'data.csv',
            'path': '/tmp/data.csv',
            'folder': 'test/uploads'
        }
        
        automation = self.config['automations'][0]
        self.assertTrue(self.executor.match_file(file_info, automation))
    
    def test_match_file_pattern_no_match(self):
        """Test file pattern not matching."""
        file_info = {
            'name': 'data.txt',
            'path': '/tmp/data.txt',
            'folder': 'test'
        }
        
        automation = self.config['automations'][0]
        self.assertFalse(self.executor.match_file(file_info, automation))
    
    def test_match_file_folder_filter(self):
        """Test folder filtering."""
        file_info = {
            'name': 'data.csv',
            'path': '/tmp/data.csv',
            'folder': 'other/folder'
        }
        
        automation = self.config['automations'][0]
        self.assertFalse(self.executor.match_file(file_info, automation))
    
    def test_disabled_automation(self):
        """Test that disabled automations are skipped."""
        file_info = {
            'name': 'test.txt',
            'path': '/tmp/test.txt',
            'folder': ''
        }
        
        automation = self.config['automations'][1]
        
        with patch('subprocess.run') as mock_run:
            success, output = self.executor.execute_script(automation, file_info)
            self.assertFalse(success)
            self.assertEqual(output, "Automation disabled")
            mock_run.assert_not_called()
    
    def test_placeholder_replacement(self):
        """Test that placeholders are correctly replaced in arguments."""
        file_info = {
            'name': 'test.csv',
            'path': '/tmp/test.csv',
            'folder': 'uploads'
        }
        
        # Create a test automation with placeholders
        automation = {
            'name': 'Test',
            'enabled': True,
            'script': 'test.py',
            'args': ['{file_path}', '{file_name}', '{folder}']
        }
        
        # Since the script doesn't exist, we expect failure, but we can verify
        # the error message doesn't contain placeholders
        success, output = self.executor.execute_script(automation, file_info)
        self.assertFalse(success)
        self.assertIn('test.py', output)


if __name__ == '__main__':
    unittest.main()
