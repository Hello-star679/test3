#!/usr/bin/env python
"""
Main entry point for running the adversarial test.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SandboxConfig
from src.detectors import create_detector
from src.generator import ConfigurableGenerator
from src.loop import AdversarialLoop

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Adversarial Content Testing Framework"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force use of mock detector"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        help="Number of epochs to run"
    )
    parser.add_argument(
        "--population",
        type=int,
        help="Population size"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    return parser.parse_args()

def main():
    """Main entry point."""
    
    print("=" * 80)
    print("ADVERSARIAL CONTENT TEST FRAMEWORK")
    print("For internal red-team / vulnerability testing ONLY")
    print("=" * 80)
    print()
    
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    config = SandboxConfig()
    
    # Override with command line arguments
    if args.mock:
        config.use_mock = True
        print("[INFO] Using mock detector (forced by argument)")
    
    if args.epochs:
        config.max_iterations = args.epochs
    
    if args.population:
        config.population_size = args.population
    
    if args.verbose:
        config.verbose = True
    
    if args.debug:
        config.debug = True
    
    # Security check
    if not config.sandbox_mode:
        print("[WARN] Sandbox mode is disabled - ensure this is a controlled environment")
        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborting...")
            sys.exit(0)
    
    # Create components
    print("[INFO] Initializing components...")
    
    # Generator
    if config.use_categories:
        templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        generator = ConfigurableGenerator(
            template_file="",
            categories=config.template_categories,
            use_categories=True,
            templates_dir=templates_dir
        )
    else:
        template_file = os.path.join(os.path.dirname(__file__), "..", config.template_file)
        generator = ConfigurableGenerator(
            template_file=template_file,
            use_categories=False
        )
    
    # Detector
    detector = create_detector(config)
    
    # Create and run loop
    loop = AdversarialLoop(generator, detector, config)
    
    try:
        best_text, best_score, history = loop.run()
        
        print()
        print("=" * 80)
        print("TEST COMPLETE - NEXT STEPS")
        print("=" * 80)
        print("1. Review the results file in the logs/ directory")
        print("2. Analyze which texts scored lowest (most evasive)")
        print("3. Consider updating your classifier with the findings")
        print("4. Run the analyze_results.py script for detailed analysis")
        print("=" * 80)
        print()
        print(f"Best evasive score: {best_score:.4f}")
        print(f"Best evasive text: {best_text}")
        print()
        print("You can now proceed to the next step of your project.")
        
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
