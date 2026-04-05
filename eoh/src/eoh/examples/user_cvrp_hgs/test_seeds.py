import sys
import os
import json
import numpy as np

# Add the src directory to sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
example_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if example_root not in sys.path:
    sys.path.insert(0, example_root)

import prob

def test_seeds():
    eva = prob.Evaluation()
    seed_path = os.path.join(os.path.dirname(__file__), "v2_agent", "refined_seeds.json")
    
    with open(seed_path, 'r', encoding='utf-8') as f:
        seeds = json.load(f)
        
    for i, seed in enumerate(seeds):
        print(f"\nTesting Seed {i+1}: {seed['algorithm']}")
        try:
            fitness = eva.evaluate(seed['code'])
            if fitness is not None:
                print(f"Success! Fitness: {fitness:.2f}")
            else:
                print(f"Failed! Error: {eva._last_error}")
                if eva._last_traceback:
                    print(f"Traceback: {eva._last_traceback}")
        except Exception as e:
            print(f"Exception during evaluation: {e}")

if __name__ == "__main__":
    test_seeds()
