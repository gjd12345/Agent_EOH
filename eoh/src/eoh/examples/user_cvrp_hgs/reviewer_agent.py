import numpy as np
import types
import traceback
import re

class ReviewerAgent:
    """
    Reviewer Agent for EoH.
    Performs static analysis and mock testing on generated heuristic code.
    """
    def __init__(self):
        pass

    def review_code(self, code_string: str) -> dict:
        """
        Performs a multi-step review of the provided code.
        """
        results = {
            "is_pass": True,
            "issues": [],
            "suggestions": []
        }

        # 1. Basic Syntax & Signature Check
        if "def generate_giant_tour" not in code_string:
            results["is_pass"] = False
            results["issues"].append("Missing required function: 'generate_giant_tour'")
            return results

        # 2. Infinite Loop Risk (Basic static check)
        if "while" in code_string and "unvisited" in code_string and "remove" not in code_string and "pop" not in code_string:
            results["is_pass"] = False
            results["issues"].append("High risk of infinite loop: 'while' loop detected without clear removal from unvisited list.")

        # 3. Mock Execution Test
        try:
            # Setup mock data (5 nodes: 1 depot + 4 customers)
            mock_coords = np.array([[0,0], [1,1], [2,2], [3,3], [4,4]])
            mock_demands = np.array([0, 10, 10, 10, 10])
            mock_dist_matrix = np.sqrt(np.sum((mock_coords[:, None, :] - mock_coords[None, :, :])**2, axis=-1))
            
            # Execute code
            module = types.ModuleType("mock_heuristic")
            exec(code_string, module.__dict__)
            
            tour = module.generate_giant_tour(mock_coords, mock_demands, mock_dist_matrix)
            
            # 4. Specification Check
            if not isinstance(tour, (list, np.ndarray)):
                results["is_pass"] = False
                results["issues"].append(f"Invalid return type: expected list/ndarray, got {type(tour)}")
            else:
                tour_arr = np.array(tour).flatten()
                if len(tour_arr) != 4:
                    results["is_pass"] = False
                    results["issues"].append(f"Invalid tour length: got {len(tour_arr)}, expected 4 (excluding depot).")
                
                if any(node == 0 for node in tour_arr):
                    results["is_pass"] = False
                    results["issues"].append("Tour contains depot (0). It should only contain customer indices (1 to N).")
                
                if len(set(tour_arr)) != len(tour_arr):
                    results["is_pass"] = False
                    results["issues"].append("Tour contains duplicate customer indices.")

        except Exception as e:
            results["is_pass"] = False
            results["issues"].append(f"Mock execution failed: {str(e)}")
            results["suggestions"].append("Check for indexing errors or undefined variables.")

        return results

if __name__ == "__main__":
    reviewer = ReviewerAgent()
    bad_code = "def generate_giant_tour(c, d, m): return [0, 1, 2]"
    print(reviewer.review_code(bad_code))
