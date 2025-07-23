#!/bin/bash
# Script de healthcheck para la API

curl -f http://localhost:8000/api/health || exit 1
