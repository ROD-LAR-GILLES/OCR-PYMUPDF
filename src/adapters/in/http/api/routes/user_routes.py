"""Rutas para la gestión de usuarios en la interfaz web.

Este módulo define las rutas específicas para la gestión de usuarios
en la interfaz web, incluyendo autenticación y preferencias.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import json
from pathlib import Path
import os
from datetime import datetime, timedelta

# Crear router
router = APIRouter(prefix="/api/users", tags=["users"])

# Modelos de datos
class UserPreferences(BaseModel):
    """Preferencias de usuario."""
    default_use_llm: bool = False
    default_process_tables: bool = True
    default_detect_language: bool = True
    default_spell_check: bool = True
    theme: str = "light"  # light, dark
    language: str = "es"  # es, en

class UserProfile(BaseModel):
    """Perfil de usuario."""
    username: str
    email: Optional[str] = None
    preferences: UserPreferences = UserPreferences()

# Directorio para almacenar perfiles de usuario
USER_DIR = Path("users")
USER_DIR.mkdir(exist_ok=True)

# Rutas
@router.get("/preferences", response_model=UserPreferences)
async def get_preferences():
    """Obtiene las preferencias del usuario actual.
    
    Por ahora, devuelve preferencias por defecto ya que no hay autenticación.
    
    Returns:
        UserPreferences: Preferencias del usuario
    """
    # En una implementación real, obtendríamos las preferencias del usuario autenticado
    # Por ahora, devolvemos preferencias por defecto
    return UserPreferences()

@router.post("/preferences", response_model=UserPreferences)
async def update_preferences(preferences: UserPreferences):
    """Actualiza las preferencias del usuario actual.
    
    Por ahora, simplemente devuelve las preferencias enviadas ya que no hay persistencia.
    
    Args:
        preferences: Nuevas preferencias del usuario
        
    Returns:
        UserPreferences: Preferencias actualizadas
    """
    # En una implementación real, guardaríamos las preferencias del usuario autenticado
    # Por ahora, simplemente devolvemos las preferencias enviadas
    return preferences

@router.get("/profile", response_model=UserProfile)
async def get_profile():
    """Obtiene el perfil del usuario actual.
    
    Por ahora, devuelve un perfil por defecto ya que no hay autenticación.
    
    Returns:
        UserProfile: Perfil del usuario
    """
    # En una implementación real, obtendríamos el perfil del usuario autenticado
    # Por ahora, devolvemos un perfil por defecto
    return UserProfile(
        username="usuario_demo",
        email="demo@example.com",
        preferences=UserPreferences()
    )