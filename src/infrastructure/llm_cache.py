"""Sistema de caché para resultados de LLM.

Implementa un sistema de caché persistente y en memoria para
resultados de refinamiento LLM, reduciendo llamadas a APIs externas
y mejorando el rendimiento general del sistema.
"""
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional, Any


class LLMCache:
    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        """Inicializa el sistema de caché LLM.

        Args:
            cache_dir: Directorio para almacenar caché persistente.
                      Si es None, usa 'data/cache/llm'.
        """
        self.cache_dir = cache_dir or Path('data/cache/llm')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, str] = {}

    def _generate_hash(self, text: str, model: str, temperature: float) -> str:
        """Genera un hash único para una solicitud LLM.

        Args:
            text: Texto de entrada
            model: Modelo LLM utilizado
            temperature: Temperatura de generación

        Returns:
            Hash único para esta combinación de parámetros
        """
        # Crear una representación única de los parámetros
        key_parts = [
            text.strip(),
            str(model),
            str(temperature)
        ]
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()

    def get(self, text: str, model: str, temperature: float = 0.0) -> Optional[str]:
        """Obtiene un resultado cacheado para una solicitud LLM.

        Args:
            text: Texto de entrada
            model: Modelo LLM utilizado
            temperature: Temperatura de generación

        Returns:
            Resultado cacheado o None si no existe
        """
        key = self._generate_hash(text, model, temperature)

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

    def set(self, text: str, model: str, temperature: float, result: str) -> None:
        """Almacena un resultado en la caché.

        Args:
            text: Texto de entrada
            model: Modelo LLM utilizado
            temperature: Temperatura de generación
            result: Resultado a almacenar
        """
        key = self._generate_hash(text, model, temperature)

        # Guardar en memoria
        self.memory_cache[key] = result

        # Guardar en disco
        cache_file = self.cache_dir / f"{key}.json"
        data = {
            'content': result,
            'params': {
                'model': model,
                'temperature': temperature,
                'text_hash': hashlib.md5(text.encode('utf-8')).hexdigest()  # Solo guardar hash del texto
            },
            'timestamp': os.path.getmtime(cache_file) if cache_file.exists() else None
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except IOError:
            pass  # Fallar silenciosamente si no se puede escribir

    def invalidate(self, text: str, model: str, temperature: float = 0.0) -> None:
        """Invalida una entrada específica de la caché.

        Args:
            text: Texto de entrada
            model: Modelo LLM utilizado
            temperature: Temperatura de generación
        """
        key = self._generate_hash(text, model, temperature)

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

        # Limpiar disco
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except (IOError, OSError):
            pass  # Fallar silenciosamente