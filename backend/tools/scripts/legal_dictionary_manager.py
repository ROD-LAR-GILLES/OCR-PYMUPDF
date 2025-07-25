#!/usr/bin/env python3
"""
Legal Dictionary Manager

This script manages legal terminology dictionaries for OCR post-processing.
It provides functionality to load, validate, and update legal word lists
and patterns used for improving OCR accuracy in legal documents.
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Set, Optional
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LegalDictionaryManager:
    """Manages legal terminology dictionaries and patterns."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the legal dictionary manager.
        
        Args:
            data_dir: Path to data directory. Defaults to ../data relative to script.
        """
        if data_dir is None:
            script_dir = Path(__file__).parent
            self.data_dir = script_dir / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.dictionaries_dir = self.data_dir / "dictionaries"
        self.corrections_dir = self.data_dir / "corrections"
        self.config_dir = self.data_dir / "config"
        
        # Dictionary files
        self.legal_words_file = self.dictionaries_dir / "legal_words.txt"
        self.legal_patterns_file = self.dictionaries_dir / "legal_patterns.txt"
        self.corrections_file = self.corrections_dir / "corrections.csv"
        
    def load_legal_words(self) -> Set[str]:
        """
        Load legal words from the dictionary file.
        
        Returns:
            Set of legal words in uppercase
        """
        words = set()
        
        if not self.legal_words_file.exists():
            logger.warning(f"Legal words file not found: {self.legal_words_file}")
            return words
            
        try:
            with open(self.legal_words_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        words.add(line.upper())
                        
            logger.info(f"Loaded {len(words)} legal words from {self.legal_words_file}")
            
        except Exception as e:
            logger.error(f"Error loading legal words: {e}")
            
        return words
    
    def load_legal_patterns(self) -> List[str]:
        """
        Load legal patterns from the patterns file.
        
        Returns:
            List of regex patterns
        """
        patterns = []
        
        if not self.legal_patterns_file.exists():
            logger.warning(f"Legal patterns file not found: {self.legal_patterns_file}")
            return patterns
            
        try:
            with open(self.legal_patterns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.append(line)
                        
            logger.info(f"Loaded {len(patterns)} legal patterns from {self.legal_patterns_file}")
            
        except Exception as e:
            logger.error(f"Error loading legal patterns: {e}")
            
        return patterns
    
    def load_corrections(self) -> Dict[str, str]:
        """
        Load OCR corrections from the corrections file.
        
        Returns:
            Dictionary mapping incorrect text to correct text
        """
        corrections = {}
        
        if not self.corrections_file.exists():
            logger.warning(f"Corrections file not found: {self.corrections_file}")
            return corrections
            
        try:
            with open(self.corrections_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'incorrect' in row and 'correct' in row:
                        corrections[row['incorrect']] = row['correct']
                        
            logger.info(f"Loaded {len(corrections)} corrections from {self.corrections_file}")
            
        except Exception as e:
            logger.error(f"Error loading corrections: {e}")
            
        return corrections
    
    def add_legal_word(self, word: str) -> bool:
        """
        Add a new legal word to the dictionary.
        
        Args:
            word: Word to add (will be converted to uppercase)
            
        Returns:
            True if word was added, False if it already exists
        """
        word = word.upper().strip()
        if not word:
            return False
            
        existing_words = self.load_legal_words()
        
        if word in existing_words:
            logger.info(f"Word '{word}' already exists in dictionary")
            return False
            
        try:
            # Append to file
            with open(self.legal_words_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{word}")
                
            logger.info(f"Added word '{word}' to legal dictionary")
            return True
            
        except Exception as e:
            logger.error(f"Error adding word '{word}': {e}")
            return False
    
    def add_correction(self, incorrect: str, correct: str) -> bool:
        """
        Add a new OCR correction mapping.
        
        Args:
            incorrect: Incorrect text as OCR'd
            correct: Correct text
            
        Returns:
            True if correction was added successfully
        """
        try:
            # Check if file exists and has headers
            file_exists = self.corrections_file.exists()
            
            with open(self.corrections_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Write header if file is new
                if not file_exists:
                    writer.writerow(['incorrect', 'correct', 'frequency', 'context'])
                    
                writer.writerow([incorrect, correct, '1', 'manual'])
                
            logger.info(f"Added correction: '{incorrect}' -> '{correct}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding correction: {e}")
            return False
    
    def validate_dictionary(self) -> Dict[str, List[str]]:
        """
        Validate the legal dictionary for common issues.
        
        Returns:
            Dictionary with validation results
        """
        issues = {
            'duplicates': [],
            'invalid_chars': [],
            'too_short': [],
            'mixed_case': []
        }
        
        words = []
        
        try:
            with open(self.legal_words_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        words.append((line_num, line))
                        
            # Check for issues
            seen_words = set()
            for line_num, word in words:
                # Check duplicates
                if word in seen_words:
                    issues['duplicates'].append(f"Line {line_num}: '{word}'")
                seen_words.add(word)
                
                # Check invalid characters
                if not word.replace('_', '').replace('-', '').isalnum():
                    issues['invalid_chars'].append(f"Line {line_num}: '{word}'")
                    
                # Check length
                if len(word) < 2:
                    issues['too_short'].append(f"Line {line_num}: '{word}'")
                    
                # Check case consistency
                if word != word.upper():
                    issues['mixed_case'].append(f"Line {line_num}: '{word}'")
                    
        except Exception as e:
            logger.error(f"Error validating dictionary: {e}")
            
        return issues
    
    def export_to_json(self, output_file: Path) -> bool:
        """
        Export all dictionaries to a JSON file.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if export was successful
        """
        try:
            data = {
                'legal_words': list(self.load_legal_words()),
                'legal_patterns': self.load_legal_patterns(),
                'corrections': self.load_corrections(),
                'metadata': {
                    'version': '1.0',
                    'total_words': len(self.load_legal_words()),
                    'total_patterns': len(self.load_legal_patterns()),
                    'total_corrections': len(self.load_corrections())
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Dictionary exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting dictionary: {e}")
            return False


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description="Legal Dictionary Manager")
    parser.add_argument("--data-dir", type=Path, help="Path to data directory")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List dictionary contents')
    list_parser.add_argument('--type', choices=['words', 'patterns', 'corrections'], 
                            default='words', help='Type of data to list')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new entries')
    add_parser.add_argument('--word', help='Add a legal word')
    add_parser.add_argument('--correction', nargs=2, metavar=('INCORRECT', 'CORRECT'),
                           help='Add OCR correction mapping')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate dictionary')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export to JSON')
    export_parser.add_argument('output', type=Path, help='Output JSON file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = LegalDictionaryManager(args.data_dir)
    
    if args.command == 'list':
        if args.type == 'words':
            words = manager.load_legal_words()
            print(f"Legal words ({len(words)}):")
            for word in sorted(words):
                print(f"  {word}")
                
        elif args.type == 'patterns':
            patterns = manager.load_legal_patterns()
            print(f"Legal patterns ({len(patterns)}):")
            for pattern in patterns:
                print(f"  {pattern}")
                
        elif args.type == 'corrections':
            corrections = manager.load_corrections()
            print(f"OCR corrections ({len(corrections)}):")
            for incorrect, correct in corrections.items():
                print(f"  '{incorrect}' -> '{correct}'")
                
    elif args.command == 'add':
        if args.word:
            if manager.add_legal_word(args.word):
                print(f"Added word: {args.word}")
            else:
                print(f"Word already exists or error occurred: {args.word}")
                
        if args.correction:
            incorrect, correct = args.correction
            if manager.add_correction(incorrect, correct):
                print(f"Added correction: '{incorrect}' -> '{correct}'")
            else:
                print("Error adding correction")
                
    elif args.command == 'validate':
        issues = manager.validate_dictionary()
        print("Dictionary validation results:")
        
        for issue_type, problems in issues.items():
            if problems:
                print(f"\n{issue_type.upper()}:")
                for problem in problems:
                    print(f"  {problem}")
            else:
                print(f"\n{issue_type.upper()}: No issues found")
                
    elif args.command == 'export':
        if manager.export_to_json(args.output):
            print(f"Dictionary exported to: {args.output}")
        else:
            print("Export failed")


if __name__ == "__main__":
    main()
