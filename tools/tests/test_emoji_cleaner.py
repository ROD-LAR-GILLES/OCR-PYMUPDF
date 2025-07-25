#!/usr/bin/env python3
"""
Tests for the emoji cleaner tool.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from testing.tools.clean_emojis import EmojiCleaner


class TestEmojiCleaner:
    """Test cases for EmojiCleaner."""
    
    def test_emoji_detection(self):
        """Test that emojis are correctly detected and removed."""
        cleaner = EmojiCleaner()
        
        # Test content with various emojis
        test_content = "Hello   World  ! This is a test   with emojis  "
        cleaned_content, emoji_count = cleaner.remove_emojis_from_content(test_content)
        
        assert emoji_count == 4
        assert " " not in cleaned_content
        assert " " not in cleaned_content
        assert " " not in cleaned_content
        assert " " not in cleaned_content
        assert "Hello" in cleaned_content
        assert "World" in cleaned_content
        
    def test_no_emojis(self):
        """Test content without emojis."""
        cleaner = EmojiCleaner()
        
        test_content = "This is regular text without any emojis."
        cleaned_content, emoji_count = cleaner.remove_emojis_from_content(test_content)
        
        assert emoji_count == 0
        assert cleaned_content == test_content
        
    def test_should_process_file(self):
        """Test file filtering logic."""
        cleaner = EmojiCleaner()
        
        # Should process
        assert cleaner.should_process_file(Path("test.py"))
        assert cleaner.should_process_file(Path("script.sh"))
        assert cleaner.should_process_file(Path("README.md"))
        assert cleaner.should_process_file(Path("config.yml"))
        
        # Should not process
        assert not cleaner.should_process_file(Path("image.jpg"))
        assert not cleaner.should_process_file(Path("binary.exe"))
        assert not cleaner.should_process_file(Path(".git/config"))
        assert not cleaner.should_process_file(Path("__pycache__/module.pyc"))
        
    def test_file_processing(self):
        """Test actual file processing."""
        cleaner = EmojiCleaner()
        
        # Create temporary file with emojis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write("# This is a Python file  \nprint('Hello World!  ')\n")
            temp_file = Path(f.name)
            
        try:
            # Process the file
            was_modified = cleaner.process_file(temp_file)
            assert was_modified
            
            # Check file content
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            assert " " not in content
            assert " " not in content
            assert "Python file" in content
            assert "Hello World!" in content
            
        finally:
            # Clean up
            temp_file.unlink()
            
    def test_dry_run_mode(self):
        """Test dry run functionality."""
        cleaner = EmojiCleaner()
        
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file with emojis
            test_file = temp_path / "test.py"
            test_file.write_text("print('Hello  ')", encoding='utf-8')
            
            # Run dry run
            original_root = cleaner.project_root
            cleaner.project_root = temp_path
            
            stats = cleaner.scan_and_clean(dry_run=True)
            
            # Check that file wasn't actually modified
            content = test_file.read_text(encoding='utf-8')
            assert " " in content
            
            # But stats should show it would be modified
            assert stats['processed_files'] >= 1
            assert stats['modified_files'] >= 1
            
            cleaner.project_root = original_root
            
    def test_multiple_emoji_types(self):
        """Test various emoji types."""
        cleaner = EmojiCleaner()
        
        test_content = """
        Faces:                
        Animals:                
        Food:                
        Transport:            ️    
        Symbols: ⭐              ️
        Flags:                  
        """
        
        cleaned_content, emoji_count = cleaner.remove_emojis_from_content(test_content)
        
        # Should detect and remove multiple emojis
        assert emoji_count > 20
        
        # Check that regular text is preserved
        assert "Faces:" in cleaned_content
        assert "Animals:" in cleaned_content
        assert "Food:" in cleaned_content
        assert "Transport:" in cleaned_content
        assert "Symbols:" in cleaned_content
        assert "Flags:" in cleaned_content
        
        # Check that no emojis remain
        # Re-run to ensure all were caught
        _, remaining_emojis = cleaner.remove_emojis_from_content(cleaned_content)
        assert remaining_emojis == 0


def test_cli_integration():
    """Test that the CLI script can be imported and called."""
    # This test ensures the script structure is correct
    from testing.tools.clean_emojis import main
    assert callable(main)


if __name__ == "__main__":
    pytest.main([__file__])
