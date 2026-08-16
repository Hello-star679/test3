"""
Adversarial Content Testing Framework
For internal red-team / vulnerability testing only
"""

__version__ = "1.0.0"
__author__ = "Internal Security Team"

from .config import SandboxConfig
from .detectors import (
    MockDetector,
    HuggingFaceDetector,
    OpenAIModerationDetector,
    LocalMLDetector,
    create_detector
)
from .generator import ConfigurableGenerator
from .loop import AdversarialLoop

__all__ = [
    "SandboxConfig",
    "MockDetector",
    "HuggingFaceDetector",
    "OpenAIModerationDetector",
    "LocalMLDetector",
    "create_detector",
    "ConfigurableGenerator",
    "AdversarialLoop"
]
