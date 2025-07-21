"""
Sistema de caché para resultados OCR y LLM.

Implementa un sistema de caché persistente y en memoria para
resultados de OCR y refinamiento LLM, mejorando el rendimiento
y reduciendo llamadas a APIs externas.
"""
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Any
from PIL import Image
import numpy as np


class OCRCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Inicializa el sistema de caché OCR.
        
        Args:
            cache_dir: Directorio para almacenar caché persistente.
                      Si es None, usa 'data/cache/ocr'.
        """
        self.cache_dir = cache_dir or Path('data/cache/ocr')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, str] = {}
    
    @lru_cache(maxsize=100)
    def get_image_hash(self, image: Image.Image) -> str:
        """Genera un hash único para una imagen."""
        img_array = np.array(image)
        return hashlib.md5(img_array.tobytes()).hexdigest()
    
    def get(self, key: str) -> Optional[str]:
        """
        Obtiene un resultado cacheado por su clave.
        
        Args:
            key: Clave única (normalmente hash de imagen)
            
        Returns:
            Contenido cacheado o None si no existe
        """
        # Primero buscar en memoria
        if key in self.memory_cache:
            return self.memory_cache[key]
            
        # Luego buscar en disco
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory_cache[key] = data['content']  # Actualizar caché en memoria
                    return data['content']
            except (json.JSONDecodeError, KeyError, IOError):
                return None
                
        return None
    
    def set(self, key: str, value: str) -> None:
        """
        Almacena un resultado en la caché.
        
        Args:
            key: Clave única (normalmente hash de imagen)
            value: Contenido a almacenar
        """
        # Guardar en memoria
        self.memory_cache[key] = value
        
        # Guardar en disco
        cache_file = self.cache_dir / f"{key}.json"
        data = {
            'content': value,
            'timestamp': os.path.getmtime(cache_file) if cache_file.exists() else None
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except IOError:
            pass  # Fallar silenciosamente si no se puede escribir
    
    def invalidate(self, key: str) -> None:
        """
        Invalida una entrada específica de la caché.
        
        Args:
            key: Clave a invalidar
        """
        # Eliminar de memoria
        if key in self.memory_cache:
            del self.memory_cache[key]
            
        # Eliminar de disco
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except IOError:
                pass  # Fallar silenciosamente
    
    def clear(self) -> None:
        """Limpia toda la caché (memoria y disco)."""
        # Limpiar memoria
        self.memory_cache.clear()
        self.get_image_hash.cache_clear()
        
        # Limpiar disco
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except (IOError, OSError):
            pass  # Fallar silenciosamente