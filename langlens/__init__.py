"""LangLens — fast, offline language detection with translation, a CLI, a quiz and a web app."""

from .detector import Analysis, Detection, Detector, analyze, detect, detect_all
from .languages import LANGUAGES, get, resolve

__all__ = ["Analysis", "Detection", "Detector", "LANGUAGES", "analyze", "detect", "detect_all", "get", "resolve"]
__version__ = "2.0.0"
