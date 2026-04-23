"""
Django application configuration for ingestion module.
Handles data ingestion pipeline setup.
"""

from django.apps import AppConfig


class IngestionConfig(AppConfig):
    """Configuration class for ingestion app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "ingestion"
