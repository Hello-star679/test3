"""
Main adversarial loop orchestrator.
Implements the GAN-style generate-score-evolve cycle.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from collections import defaultdict

from .config import SandboxConfig

class AdversarialLoop:
    """
    GAN-style iterative testing loop for content classifiers.
    Maintains a population of texts and evolves them to find boundary cases.
    """
    
    def __init__(self, generator, detector, config: SandboxConfig):
        self.generator = generator
        self.detector = detector
        self.config = config
        self.population = []
        self.history = []
        self.stats = defaultdict(int)
        self.best_text = None
        self.best_score = float('inf')
        
        # Track unique texts to avoid duplicates
        self.seen_texts = set()
    
    def initialize_population(self):
        """Initialize the population with generated texts."""
        print(f"[INFO] Initializing population of {self.config.population_size} texts...")
        
        # Try to balance across categories if using categories
        if self.config.use_categories:
            categories = self.generator.get_categories()
            per_category = max(1, self.config.population_size // len(categories))
            
            for category in categories:
                for _ in range(per_category):
                    text = self.generator.generate(category)
                    if text not in self.seen_texts:
                        self.population.append(text)
                        self.seen_texts.add(text)
            
            # Fill remaining with random
            while len(self.population) < self.config.population_size:
                text = self.generator.generate()
                if text not in self.seen_texts:
                    self.population.append(text)
                    self.seen_texts.add(text)
        else:
            # Simple uniform initialization
            for _ in range(self.config.population_size):
                text = self.generator.generate()
                if text not in self.seen_texts:
                    self.population.append(text)
                    self.seen_texts.add(text)
        
        print(f"[INFO] Population initialized with {len(self.population)} unique texts")
    
    def evaluate_population(self) -> List[Tuple[str, float]]:
        """
        Evaluate all texts in the population and return (text, score) pairs.
        """
        scored = []
        for text in self.population:
            score = self.detector.score(text)
            scored.append((text, score))
            
            # Track best overall
            if score < self.best_score:
                self.best_score = score
                self.best_text = text
        
        # Sort by score (lower = better for evasion)
        scored.sort(key=lambda x: x[1])
        return scored
    
    def evolve_population(self, scored: List[Tuple[str, float]]) -> List[str]:
        """
        Evolve the population by keeping elites and generating offspring.
        """
        # Calculate elite count
        elite_count = max(1, int(len(scored) * self.config.elite_ratio))
        
        # Keep elites (lowest scores)
        elites = scored[:elite_count]
        elite_texts = [text for text, _ in elites]
        
        # Generate offspring through mutation
        offspring = []
        target_size = self.config.population_size
        
        while len(offspring) < (target_size - len(elite_texts)):
            # Select a parent from elites (weighted by score)
            parent = self._select_parent(elites)
            
            # Mutate the parent
            child = self.generator.mutate(parent)
            
            # Ensure uniqueness
            if child not in self.seen_texts:
                offspring.append(child)
                self.seen_texts.add(child)
            else:
                # If duplicate, try a different mutation
                for _ in range(3):
                    child = self.generator.mutate(parent)
                    if child not in self.seen_texts:
                        offspring.append(child)
                        self.seen_texts.add(child)
                        break
                else:
                    # If still duplicate, generate a completely new text
                    child = self.generator.generate()
                    if child not in self.seen_texts:
                        offspring.append(child)
                        self.seen_texts.add(child)
        
        # New population = elites + offspring
        new_population = elite_texts + offspring
        random.shuffle(new_population)  # Shuffle to maintain diversity
        
        return new_population
    
    def _select_parent(self, elites: List[Tuple[str, float]]) -> str:
        """
        Select a parent from elites using tournament selection.
        """
        # Weighted selection: lower score = higher chance
        # Convert scores to weights (inverse)
        weights = [1.0 / (score + 0.001) for _, score in elites]
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(elites)[0]
        
        # Normalize weights
        normalized = [w / total_weight for w in weights]
        
        # Select
        r = random.random()
        cumulative = 0
        for i, weight in enumerate(normalized):
            cumulative += weight
            if r <= cumulative:
                return elites[i][0]
        
        return elites[-1][0]
    
    def run(self):
        """Execute the full adversarial loop."""
        print("=" * 80)
        print("ADVERSARIAL CONTENT TEST FRAMEWORK")
        print("=" * 80)
        print(f"Target Classifier: {self.config.classifier_endpoint}")
        print(f"Detector Type: {self.config.detector_type}")
        print(f"Max Epochs: {self.config.max_iterations}")
        print(f"Population Size: {self.config.population_size}")
        print(f"Elite Ratio: {self.config.elite_ratio}")
        print(f"Mutation Rate: {self.config.mutation_rate}")
        print(f"Sandbox Mode: {self.config.sandbox_mode}")
        print("=" * 80)
        print()
        
        # Initialize population
        self.initialize_population()
        
        # Main loop
        start_time = time.time()
        best_overall = None
        best_overall_score = float('inf')
        
        for epoch in range(self.config.max_iterations):
            # Evaluate current population
            scored = self.evaluate_population()
            
            # Track best in this generation
            best_epoch_text, best_epoch_score = scored[0]
            
            # Update overall best
            if best_epoch_score < best_overall_score:
                best_overall_score = best_epoch_score
                best_overall = best_epoch_text
            
            # Log epoch results
            avg_score = sum(score for _, score in scored) / len(scored)
            median_score = scored[len(scored)//2][1]
            
            print(f"Epoch {epoch+1:03d}/{self.config.max_iterations} | "
                  f"Best: {best_epoch_score:.4f} | "
                  f"Avg: {avg_score:.4f} | "
                  f"Median: {median_score:.4f} | "
                  f"Text: {best_epoch_text[:50]}...")
            
            # Store history
            self.history.append({
                'epoch': epoch + 1,
                'best_score': best_epoch_score,
                'best_text': best_epoch_text,
                'avg_score': avg_score,
                'median_score': median_score,
                'all_scores': [score for _, score in scored],
                'all_texts': [text for text, _ in scored[:10]]  # Keep top 10
            })
            
            # Update statistics
            self.stats['total_evaluations'] += len(scored)
            self.stats['best_score_so_far'] = min(self.stats.get('best_score_so_far', float('inf')), best_epoch_score)
            
            # Evolve population for next generation
            if epoch < self.config.max_iterations - 1:
                self.population = self.evolve_population(scored)
        
        elapsed = time.time() - start_time
        
        # Summary
        print()
        print("=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"Completed: {self.config.max_iterations} epochs in {elapsed:.2f}s")
        print(f"Total evaluations: {self.stats['total_evaluations']}")
        print(f"Best overall score: {best_overall_score:.4f}")
        print(f"Best overall text: {best_overall}")
        print("=" * 80)
        print()
        
        # Save results
        if self.config.save_results:
            self._save_results(best_overall, best_overall_score)
        
        return best_overall, best_overall_score, self.history
    
    def _save_results(self, best_text: str, best_score: float):
        """Save results to a timestamped file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.log_dir}/adversarial_results_{timestamp}.json"
        
        output = {
            'timestamp': timestamp,
            'config': self.config.to_dict(),
            'best_score': best_score,
            'best_text': best_text,
            'history': self.history,
            'stats': dict(self.stats)
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Results saved to: {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to save results: {e}")
