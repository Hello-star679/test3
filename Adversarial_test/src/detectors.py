"""
Content detector implementations for the adversarial test framework.
Supports multiple backends with a unified scoring interface.
"""

import requests
import json
import os
from typing import Optional, Union, List, Dict, Any
from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """Abstract base class for all detectors."""
    
    @abstractmethod
    def score(self, text: str) -> float:
        """Return a suspicion score between 0.0 (safe) and 1.0 (malicious)."""
        pass
    
    def batch_score(self, texts: List[str]) -> List[float]:
        """Score multiple texts in batch if supported."""
        return [self.score(text) for text in texts]

# ============================================
# MOCK DETECTOR
# ============================================
class MockDetector(BaseDetector):
    """
    Placeholder detector for initial testing without external dependencies.
    Generates deterministic but meaningless scores based on text properties.
    """
    
    def __init__(self, threshold: float = 0.7, seed: int = 42):
        self.threshold = threshold
        self.seed = seed
        import random
        random.seed(seed)
    
    def score(self, text: str) -> float:
        """
        Calculate a fake score based on:
        - Length (longer texts get higher scores)
        - Uniqueness of characters
        - Presence of common words
        """
        if not text:
            return 0.0
        
        # Length factor (capped at 1.0)
        length_score = min(1.0, len(text) / 150)
        
        # Uniqueness factor
        unique_ratio = len(set(text.lower())) / max(1, len(text))
        
        # Common word factor (words like "verify", "account" increase score)
        common_words = ["verify", "account", "update", "security", "password", "confirm"]
        word_score = sum(1 for word in common_words if word in text.lower()) / len(common_words)
        
        # Combine scores
        raw_score = (length_score * 0.4 + unique_ratio * 0.3 + word_score * 0.3)
        
        # Add some randomness to simulate real classifier behavior
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16) / (16**8)
        noise = (hash_val - 0.5) * 0.1
        
        return max(0.0, min(1.0, raw_score + noise))

# ============================================
# HUGGING FACE DETECTOR
# ============================================
class HuggingFaceDetector(BaseDetector):
    """
    Connects to a Hugging Face model endpoint (local or cloud).
    Supports custom response parsing based on model output format.
    """
    
    def __init__(
        self,
        api_url: str,
        threshold: float = 0.7,
        use_local: bool = True,
        api_token: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 10
    ):
        self.api_url = api_url
        self.threshold = threshold
        self.use_local = use_local
        self.timeout = timeout
        self.model_name = model_name
        
        # Headers for authentication
        self.headers = {}
        if not use_local and api_token:
            self.headers["Authorization"] = f"Bearer {api_token}"
        elif not use_local:
            print("[WARN] No API token provided for cloud HF inference")
    
    def score(self, text: str) -> float:
        """
        Send text to HF model and extract the suspicion score.
        Supports multiple response formats automatically.
        """
        if not text:
            return 0.0
        
        payload = {
            "inputs": text,
            "parameters": {
                "truncation": True,
                "max_length": 512,
                "padding": "max_length"
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # ============================================================
            # AUTO-DETECT RESPONSE FORMAT
            # ============================================================
            
            # FORMAT A: [{"label": "malicious", "score": 0.95}, ...]
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'label' in result[0] and 'score' in result[0]:
                    # Find malicious label
                    for item in result:
                        label = item.get('label', '').lower()
                        if label in ['malicious', 'unsafe', 'spam', 'fraud', 'scam', 'abusive', 'harmful']:
                            return float(item.get('score', 0.0))
                    # If no malicious label found, use first score
                    return float(result[0].get('score', 0.0))
            
            # FORMAT B: {'prediction': 0.89, 'confidence': 0.92}
            if isinstance(result, dict):
                # Try common keys
                for key in ['prediction', 'score', 'probability', 'prob', 'confidence']:
                    if key in result:
                        return float(result[key])
                # Try nested results
                if 'results' in result:
                    return self._parse_nested_results(result['results'])
                # Try to find any numeric value
                for key, value in result.items():
                    if isinstance(value, (int, float)) and key.lower() not in ['id', 'timestamp']:
                        return float(value)
            
            # FORMAT C: [0.2, 0.8] (probabilities)
            if isinstance(result, list) and all(isinstance(x, (int, float)) for x in result):
                if len(result) == 2:
                    # Assume [safe, malicious] or [malicious, safe]
                    # Higher score likely indicates malicious
                    return max(result)
                elif len(result) > 2:
                    # Multi-class, return max
                    return max(result)
            
            # FORMAT D: string response (parse it)
            if isinstance(result, str):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(result)
                    return self.score(parsed)  # Recursive call with parsed
                except:
                    # Try to extract a number
                    import re
                    numbers = re.findall(r'\d+\.\d+', result)
                    if numbers:
                        return float(numbers[0])
            
            # Fallback: log and return safe value
            print(f"[WARN] Unrecognized response format: {type(result)} - {str(result)[:200]}")
            return 0.0
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API call failed: {e}")
            return 0.5
        except Exception as e:
            print(f"[ERROR] Unexpected error in HuggingFaceDetector: {e}")
            if self.use_local:
                print("[INFO] Trying fallback to mock detector")
            return 0.5
    
    def _parse_nested_results(self, nested: Any) -> float:
        """Helper to parse nested result structures."""
        if isinstance(nested, list):
            for item in nested:
                if isinstance(item, dict):
                    # Look for category/score pattern
                    category = item.get('category', '').lower()
                    score = item.get('score', 0.0)
                    if category in ['fraud', 'scam', 'malicious', 'unsafe']:
                        return float(score)
                    if 'score' in item:
                        return float(item['score'])
        elif isinstance(nested, dict):
            # Try category keys
            for key in ['fraud', 'scam', 'malicious', 'unsafe']:
                if key in nested:
                    return float(nested[key])
            # Try score keys
            for key in ['score', 'probability', 'confidence']:
                if key in nested:
                    return float(nested[key])
        return 0.0

# ============================================
# OPENAI MODERATION DETECTOR
# ============================================
class OpenAIModerationDetector(BaseDetector):
    """
    Uses OpenAI's Moderation API to score content.
    Requires a valid OpenAI API key.
    """
    
    def __init__(self, api_key: str, threshold: float = 0.7, fallback_to_mock: bool = True):
        self.api_key = api_key
        self.threshold = threshold
        self.fallback_to_mock = fallback_to_mock
        self._mock = MockDetector(threshold) if fallback_to_mock else None
        
        if not api_key:
            print("[WARN] OpenAI API key not set")
            if not fallback_to_mock:
                raise ValueError("OpenAI API key required")
    
    def score(self, text: str) -> float:
        """Get moderation score from OpenAI."""
        if not self.api_key:
            return self._mock.score(text) if self._mock else 0.0
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.Moderation.create(input=text)
            
            results = response["results"][0]
            category_scores = results["category_scores"]
            
            # Get the highest score across all categories
            max_score = max(category_scores.values()) if category_scores else 0.0
            
            return max_score
            
        except ImportError:
            print("[ERROR] OpenAI package not installed. Run: pip install openai")
            return self._mock.score(text) if self._mock else 0.5
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {e}")
            return self._mock.score(text) if self._mock else 0.5

# ============================================
# LOCAL ML DETECTOR
# ============================================
class LocalMLDetector(BaseDetector):
    """
    Loads a locally saved model for offline testing.
    Supports Hugging Face transformers and custom PyTorch models.
    """
    
    def __init__(
        self,
        model_path: str,
        threshold: float = 0.7,
        malicious_index: int = 1,
        malicious_label: str = "malicious",
        fallback_to_mock: bool = True
    ):
        self.model_path = model_path
        self.threshold = threshold
        self.malicious_index = malicious_index
        self.malicious_label = malicious_label
        self.fallback_to_mock = fallback_to_mock
        self._mock = MockDetector(threshold) if fallback_to_mock else None
        self._loaded = False
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self):
        """Load model and tokenizer from disk."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            # Check if CUDA is available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"[INFO] Using device: {self.device}")
            
            # Load tokenizer and model
            print(f"[INFO] Loading model from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            
            self._loaded = True
            print("[INFO] Model loaded successfully")
            
        except ImportError:
            print("[ERROR] transformers or torch not installed")
            print("[INFO] Install with: pip install transformers torch")
            if not self.fallback_to_mock:
                raise
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            if self.fallback_to_mock:
                print("[INFO] Falling back to mock detector")
            else:
                raise
    
    def score(self, text: str) -> float:
        """Run inference on local model."""
        if not self._loaded:
            return self._mock.score(text) if self._mock else 0.5
        
        try:
            import torch
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
                probs = probabilities[0].cpu().numpy()
            
            # Extract malicious score
            if len(probs) > self.malicious_index:
                return float(probs[self.malicious_index])
            else:
                # Try to find by label
                try:
                    if hasattr(self.model.config, 'id2label'):
                        for idx, label in self.model.config.id2label.items():
                            if self.malicious_label.lower() in label.lower():
                                return float(probs[idx])
                except:
                    pass
                # Fallback: return max probability
                return float(max(probs))
            
        except Exception as e:
            print(f"[ERROR] Local model inference failed: {e}")
            return self._mock.score(text) if self._mock else 0.5

# ============================================
# DETECTOR FACTORY
# ============================================
def create_detector(config):
    """
    Factory function to create the appropriate detector based on configuration.
    """
    if config.use_mock:
        print("[INFO] Using MOCK detector (for initial testing)")
        return MockDetector(threshold=0.6)
    
    detector_type = config.detector_type.lower()
    
    if detector_type == "openai":
        print("[INFO] Using OpenAI Moderation detector")
        return OpenAIModerationDetector(
            api_key=config.openai_api_key,
            threshold=config.openai_threshold,
            fallback_to_mock=True
        )
    
    elif detector_type == "local":
        print(f"[INFO] Using LOCAL model from {config.local_model_path}")
        return LocalMLDetector(
            model_path=config.local_model_path,
            threshold=0.6,
            malicious_index=config.local_model_index,
            malicious_label=config.local_model_label,
            fallback_to_mock=True
        )
    
    elif detector_type == "hf":
        print(f"[INFO] Using Hugging Face detector at {config.hf_local_url}")
        return HuggingFaceDetector(
            api_url=config.hf_local_url,
            threshold=0.6,
            use_local=True,
            api_token=config.hf_api_token,
            model_name=config.hf_model_name,
            timeout=config.classifier_timeout
        )
    
    else:
        print(f"[WARN] Unknown detector type '{detector_type}'. Using Mock.")
        return MockDetector(threshold=0.6)
