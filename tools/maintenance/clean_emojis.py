#!/usr/bin/env python3
"""
Emoji Cleaner Tool

This script removes emoji characters from all project files to ensure
compatibility across different systems and improve code readability.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmojiCleaner:
    """Removes emoji characters from project files."""
    
    # Unicode ranges for emoji characters
    EMOJI_PATTERNS = [
        r'[\U0001f600-\U0001f64f]',  # Emoticons
        r'[\U0001f300-\U0001f5ff]',  # Miscellaneous Symbols and Pictographs
        r'[\U0001f680-\U0001f6ff]',  # Transport and Map Symbols
        r'[\U0001f1e0-\U0001f1ff]',  # Regional Indicator Symbols
        r'[\U00002600-\U000026ff]',  # Miscellaneous Symbols
        r'[\U00002700-\U000027bf]',  # Dingbats
        r'[\U0001f700-\U0001f77f]',  # Alchemical Symbols
        r'[\U0001f780-\U0001f7ff]',  # Geometric Shapes Extended
        r'[\U0001f800-\U0001f8ff]',  # Supplemental Arrows-C
        r'[\U0001f900-\U0001f9ff]',  # Supplemental Symbols and Pictographs
        r'[\U0001fa00-\U0001fa6f]',  # Chess Symbols
        r'[\U0001fa70-\U0001faff]',  # Symbols and Pictographs Extended-A
    ]
    
    def __init__(self, project_root: Path = None):
        """Initialize the emoji cleaner."""
        self.project_root = project_root or Path.cwd()
        self.emoji_regex = re.compile('|'.join(self.EMOJI_PATTERNS))
        
        # Default file extensions to process
        self.extensions = {'.py', '.sh', '.md', '.txt', '.yml', '.yaml', '.json'}
        
        # Directories to exclude
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'env', '.env', 'dist', 'build'
        }
        
        # Files processed and modified
        self.processed_files = 0
        self.modified_files = 0
        self.errors = []
        
    def should_process_file(self, filepath: Path) -> bool:
        """Check if file should be processed."""
        # Check extension
        if filepath.suffix.lower() not in self.extensions:
            return False
            
        # Check if in excluded directory
        for part in filepath.parts:
            if part in self.exclude_dirs:
                return False
                
        return True
        
    def remove_emojis_from_content(self, content: str) -> tuple[str, int]:
        """
        Remove emojis from content.
        
        Returns:
            Tuple of (cleaned_content, emoji_count_removed)
        """
        original_content = content
        cleaned_content = self.emoji_regex.sub(' ', content)
        
        # Count emojis removed
        emoji_count = len(self.emoji_regex.findall(original_content))
        
        return cleaned_content, emoji_count
        
    def process_file(self, filepath: Path) -> bool:
        """
        Process a single file to remove emojis.
        
        Returns:
            True if file was modified, False otherwise
        """
        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # Remove emojis
            cleaned_content, emoji_count = self.remove_emojis_from_content(original_content)
            
            # Write back if content changed
            if cleaned_content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                    
                logger.info(f"Cleaned {emoji_count} emojis from: {filepath}")
                return True
                
            return False
            
        except Exception as e:
            error_msg = f"Error processing {filepath}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
            
    def scan_and_clean(self, dry_run: bool = False) -> dict:
        """
        Scan project and clean emoji characters.
        
        Args:
            dry_run: If True, only report what would be changed
            
        Returns:
            Dictionary with statistics
        """
        logger.info(f"Starting emoji cleanup (dry_run: {dry_run})")
        logger.info(f"Project root: {self.project_root}")
        
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                filepath = root_path / file
                
                if not self.should_process_file(filepath):
                    continue
                    
                self.processed_files += 1
                
                if dry_run:
                    # Just check for emojis
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        _, emoji_count = self.remove_emojis_from_content(content)
                        if emoji_count > 0:
                            logger.info(f"Would clean {emoji_count} emojis from: {filepath}")
                            self.modified_files += 1
                    except Exception as e:
                        self.errors.append(f"Error scanning {filepath}: {e}")
                else:
                    # Actually clean the file
                    if self.process_file(filepath):
                        self.modified_files += 1
                        
        return {
            'processed_files': self.processed_files,
            'modified_files': self.modified_files,
            'errors': len(self.errors),
            'error_details': self.errors
        }
        
    def clean_specific_files(self, filepaths: List[Path], dry_run: bool = False) -> dict:
        """Clean specific files."""
        logger.info(f"Cleaning specific files (dry_run: {dry_run})")
        
        for filepath in filepaths:
            if not filepath.exists():
                error_msg = f"File not found: {filepath}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                continue
                
            if not self.should_process_file(filepath):
                logger.warning(f"Skipping file (not in allowed extensions): {filepath}")
                continue
                
            self.processed_files += 1
            
            if dry_run:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    _, emoji_count = self.remove_emojis_from_content(content)
                    if emoji_count > 0:
                        logger.info(f"Would clean {emoji_count} emojis from: {filepath}")
                        self.modified_files += 1
                except Exception as e:
                    self.errors.append(f"Error scanning {filepath}: {e}")
            else:
                if self.process_file(filepath):
                    self.modified_files += 1
                    
        return {
            'processed_files': self.processed_files,
            'modified_files': self.modified_files,
            'errors': len(self.errors),
            'error_details': self.errors
        }


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Remove emoji characters from project files")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--files', nargs='+', type=Path, help='Specific files to clean')
    parser.add_argument('--extensions', nargs='+', help='File extensions to process (default: .py .sh .md .txt .yml .yaml .json)')
    parser.add_argument('--exclude-dirs', nargs='+', help='Additional directories to exclude')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize cleaner
    cleaner = EmojiCleaner(args.project_root)
    
    # Configure extensions if provided
    if args.extensions:
        cleaner.extensions = {ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions}
        
    # Add additional exclude directories
    if args.exclude_dirs:
        cleaner.exclude_dirs.update(args.exclude_dirs)
        
    # Process files
    if args.files:
        stats = cleaner.clean_specific_files(args.files, args.dry_run)
    else:
        stats = cleaner.scan_and_clean(args.dry_run)
        
    # Print results
    print(f"\n{'=' * 50}")
    print("EMOJI CLEANUP RESULTS")
    print(f"{'=' * 50}")
    print(f"Files processed: {stats['processed_files']}")
    print(f"Files {'would be ' if args.dry_run else ''}modified: {stats['modified_files']}")
    print(f"Errors encountered: {stats['errors']}")
    
    if stats['error_details']:
        print(f"\nErrors:")
        for error in stats['error_details']:
            print(f"  - {error}")
            
    if args.dry_run:
        print(f"\nThis was a dry run. Use without --dry-run to actually modify files.")
        
    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())
