#!/usr/bin/env python
"""
Diagnostic tool to identify your classifier's response format.
Run this first to understand what your classifier returns.
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Get configuration
CLASSIFIER_URL = os.getenv("CLASSIFIER_URL", "http://localhost:8080/classify")
DETECTOR_TYPE = os.getenv("DETECTOR_TYPE", "hf").lower()

# Test texts
TEST_TEXTS = [
    "Your account needs verification",
    "Please update your security settings",
    "Transaction completed successfully",
    "New device detected on your account",
    "Security alert: unusual activity detected"
]

def test_classifier():
    """Test the classifier with different texts and display responses."""
    
    print("=" * 80)
    print("CLASSIFIER DIAGNOSTIC TOOL")
    print("=" * 80)
    print(f"URL: {CLASSIFIER_URL}")
    print(f"Detector Type: {DETECTOR_TYPE}")
    print()
    
    # Try different request formats
    formats = [
        {"name": "Standard HF format", "payload": {"inputs": ""}},
        {"name": "JSON with text", "payload": {"text": ""}},
        {"name": "JSON with inputs", "payload": {"input": ""}},
        {"name": "Simple text", "payload": ""},  # Will be sent as raw text
    ]
    
    for text in TEST_TEXTS:
        print(f"\n{'='*80}")
        print(f"TEST TEXT: '{text}'")
        print("=" * 80)
        
        for format_info in formats:
            name = format_info["name"]
            base_payload = format_info["payload"]
            
            # Fill the payload
            if isinstance(base_payload, dict):
                payload = base_payload.copy()
                # Find the first key and fill it
                for key in payload:
                    payload[key] = text
                    break
            else:
                payload = text
            
            print(f"\n  Format: {name}")
            print(f"  Payload: {json.dumps(payload) if isinstance(payload, dict) else payload}")
            
            try:
                if isinstance(payload, dict):
                    response = requests.post(
                        CLASSIFIER_URL,
                        json=payload,
                        timeout=10
                    )
                else:
                    response = requests.post(
                        CLASSIFIER_URL,
                        data=payload,
                        headers={"Content-Type": "text/plain"},
                        timeout=10
                    )
                
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  Response Type: {type(result).__name__}")
                    print(f"  Response Data: {json.dumps(result, indent=2)[:500]}...")
                    
                    # Determine format
                    print("\n  ✓ This appears to be:")
                    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'label' in result[0]:
                        print("    FORMAT A: List of label/score pairs")
                        print("    → Use this in detectors.py:")
                        print("      if isinstance(result, list):")
                        print("          for item in result:")
                        print("              if item.get('label') == 'malicious':")
                        print("                  return item.get('score')")
                    elif isinstance(result, dict) and 'prediction' in result:
                        print("    FORMAT B: Dictionary with 'prediction' key")
                        print("    → Use this in detectors.py:")
                        print("      if isinstance(result, dict) and 'prediction' in result:")
                        print("          return float(result['prediction'])")
                    elif isinstance(result, list) and all(isinstance(x, (int, float)) for x in result):
                        print("    FORMAT C: List of probabilities")
                        print("    → Use this in detectors.py:")
                        print("      if isinstance(result, list) and len(result) == 2:")
                        print("          return float(result[1])  # index 1 = malicious")
                    elif isinstance(result, dict) and 'results' in result:
                        print("    FORMAT D: Nested with 'results'")
                        print("    → Use this in detectors.py:")
                        print("      if isinstance(result, dict) and 'results' in result:")
                        print("          # Parse result['results']")
                    else:
                        print("    UNKNOWN FORMAT - Please share this output")
                        print(f"    Raw: {str(result)[:200]}")
                else:
                    print(f"  Error: {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError:
                print("  ✗ Connection error - Classifier not running")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("1. Based on the responses above, copy the appropriate parsing code")
    print("2. Paste it into the score() method in detectors.py")
    print("3. Run with mock detector first: USE_MOCK=True python run_test.py")
    print("4. Then test with real detector: USE_MOCK=False python run_test.py")

if __name__ == "__main__":
    test_classifier()
