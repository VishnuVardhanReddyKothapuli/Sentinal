"""Sentinel media inference. Heavy model dependencies are deliberately lazy."""

from .pipeline import analyze_media, delete_record, delete_vector, get_capabilities

__all__ = ["analyze_media", "delete_record", "delete_vector", "get_capabilities"]
