"""
File storage infrastructure module.

This module provides file storage operations for the OCR-PYMUPDF application,
including file management, temporary storage, and file system utilities.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Optional, List
import logging

logger = logging.getLogger(__name__)


class FileStorageManager:
    """Manages file storage operations for the application."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the file storage manager.
        
        Args:
            base_path: Base directory for file operations. Defaults to temp directory.
        """
        self.base_path = Path(base_path) if base_path else Path(tempfile.gettempdir())
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def save_file(self, file_content: bytes, filename: str, subfolder: str = "") -> Path:
        """
        Save file content to storage.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file to save
            subfolder: Optional subfolder within base path
            
        Returns:
            Path to the saved file
        """
        target_dir = self.base_path / subfolder if subfolder else self.base_path
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
            
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def read_file(self, file_path: Union[str, Path]) -> bytes:
        """
        Read file content from storage.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Binary content of the file
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(path, 'rb') as f:
            content = f.read()
            
        logger.info(f"File read: {file_path}")
        return content
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    
    def list_files(self, pattern: str = "*", subfolder: str = "") -> List[Path]:
        """
        List files in storage matching a pattern.
        
        Args:
            pattern: Glob pattern to match files
            subfolder: Optional subfolder to search in
            
        Returns:
            List of matching file paths
        """
        search_dir = self.base_path / subfolder if subfolder else self.base_path
        if not search_dir.exists():
            return []
            
        files = list(search_dir.glob(pattern))
        return [f for f in files if f.is_file()]
    
    def create_temp_file(self, suffix: str = "", prefix: str = "ocr_") -> Path:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to the temporary file
        """
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=self.base_path)
        os.close(fd)  # Close the file descriptor
        return Path(temp_path)
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified hours.
        
        Args:
            older_than_hours: Remove files older than this many hours
            
        Returns:
            Number of files removed
        """
        import time
        current_time = time.time()
        cutoff_time = current_time - (older_than_hours * 3600)
        
        removed_count = 0
        for file_path in self.list_files("ocr_*"):
            if file_path.stat().st_mtime < cutoff_time:
                if self.delete_file(file_path):
                    removed_count += 1
                    
        logger.info(f"Cleaned up {removed_count} temporary files")
        return removed_count


# Global instance for convenience
default_storage = FileStorageManager()
