#!/usr/bin/env python
"""
Analyze results from the adversarial test.
Provides detailed insights about the most effective evasive texts.
"""

import os
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def find_latest_results(log_dir: str = "logs") -> str:
    """Find the most recent results file."""
    log_path = Path(log_dir)
    if not log_path.exists():
        return None
    
    files = list(log_path.glob("adversarial_results_*.json"))
    if not files:
        return None
    
    return str(sorted(files)[-1])

def analyze_results(filepath: str):
    """Analyze the results from a test run."""
    
    print("=" * 80)
    print("RESULTS ANALYSIS")
    print("=" * 80)
    print(f"File: {filepath}")
    print()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load results: {e}")
        return
    
    # Extract data
    config = data.get('config', {})
    history = data.get('history', [])
    best_score = data.get('best_score', 0)
    best_text = data.get('best_text', '')
    stats = data.get('stats', {})
    
    print("CONFIGURATION")
    print("-" * 80)
    print(f"  Detector Type: {config.get('detector_type', 'unknown')}")
    print(f"  Epochs: {config.get('max_iterations', 'unknown')}")
    print(f"  Population: {config.get('population_size', 'unknown')}")
    print(f"  Mutation Rate: {config.get('mutation_rate', 'unknown')}")
    print(f"  Elite Ratio: {config.get('elite_ratio', 'unknown')}")
    print()
    
    print("PERFORMANCE METRICS")
    print("-" * 80)
    print(f"  Total Evaluations: {stats.get('total_evaluations', 'unknown')}")
    print(f"  Best Score Achieved: {best_score:.4f}")
    print(f"  Best Text: {best_text}")
    print()
    
    # Score progression
    if history:
        best_scores = [h.get('best_score', 0) for h in history]
        avg_scores = [h.get('avg_score', 0) for h in history]
        median_scores = [h.get('median_score', 0) for h in history]
        
        print("SCORE PROGRESSION")
        print("-" * 80)
        print(f"  Initial Best: {best_scores[0]:.4f}")
        print(f"  Final Best: {best_scores[-1]:.4f}")
        print(f"  Improvement: {best_scores[0] - best_scores[-1]:.4f}")
        print(f"  Initial Avg: {avg_scores[0]:.4f}")
        print(f"  Final Avg: {avg_scores[-1]:.4f}")
        print()
        
        # Find top 10 evasive texts
        all_texts = []
        all_scores = []
        for h in history:
            texts = h.get('all_texts', [])
            scores = h.get('all_scores', [])
            all_texts.extend(texts)
            all_scores.extend(scores)
        
        # Combine and get unique
        text_score_pairs = {}
        for t, s in zip(all_texts, all_scores):
            if t not in text_score_pairs or s < text_score_pairs[t]:
                text_score_pairs[t] = s
        
        # Sort by score
        sorted_pairs = sorted(text_score_pairs.items(), key=lambda x: x[1])
        
        print("TOP 10 MOST EVASIVE TEXTS")
        print("-" * 80)
        for i, (text, score) in enumerate(sorted_pairs[:10], 1):
            print(f"  {i:02d}. Score: {score:.4f}")
            print(f"      Text: {text}")
            print()
    
    print("RECOMMENDATIONS")
    print("-" * 80)
    if best_score < 0.3:
        print("  ✓ Your classifier is performing well - few texts are evasive")
    elif best_score < 0.5:
        print("  ⚠️ Some texts are evading detection - consider reviewing")
    else:
        print("  ✗ Many texts are evading detection - classifier may need improvement")
    
    print()
    print("To improve your classifier:")
    print("  1. Add the top evasive texts to your training set")
    print("  2. Review the patterns in the most evasive texts")
    print("  3. Consider tuning your classifier's threshold")
    print("  4. Run additional test iterations with different mutation rates")

if __name__ == "__main__":
    # Find latest results
    results_file = find_latest_results()
    
    if not results_file:
        print("[ERROR] No results files found in logs/ directory")
        sys.exit(1)
    
    analyze_results(results_file)
