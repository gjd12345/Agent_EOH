class GetPrompts():
    def __init__(self):
        self.prompt_task = "You are an expert in combinatorial optimization. Your task is to design a 'Giant Tour' generation algorithm for the Capacitated Vehicle Routing Problem (CVRP). \
Given the coordinates, demands, and distance matrix of customers, you need to produce a single permutation of all customers (a Giant Tour). \
This Giant Tour will later be partitioned into feasible routes. Your goal is to find an ordering that, when split optimally, results in the minimum total travel distance. \
Mathematical Properties to Consider:\n\
1. Polar Alignment: High-quality giant tours often exhibit 'Sweep' characteristics where sequential nodes have similar polar angles relative to the depot.\n\
2. Load Balance: Consider the demands of sequential nodes to avoid creating segments that exceed vehicle capacity too quickly or leave too much empty space.\n\
3. Locality: Nodes that are physically close should ideally be close in the permutation to facilitate efficient sub-routes."
        
        self.prompt_func_name = "generate_giant_tour"
        self.prompt_func_inputs = ["coords", "demands", "dist_matrix"]
        self.prompt_func_outputs = ["giant_tour"]
        self.prompt_inout_inf = "- 'coords': A 2D numpy array of (x, y) coordinates for all nodes (index 0 is depot).\n\
- 'demands': A 1D numpy array where demands[i] is the demand of node i (demands[0] is 0).\n\
- 'dist_matrix': A 2D numpy array of distances between all nodes.\n\
- 'giant_tour': A 1D numpy array containing a permutation of all customer indices (excluding depot, i.e., indices 1 to N)."
        
        self.prompt_other_inf = "The algorithm should return a valid permutation of all customers. The quality of the tour will be evaluated by its total distance after optimal partitioning. \
CRITICAL: Return ONLY the Python code. Do not wrap it in markdown blocks (```python ... ```). Do not include any explanations, comments, or descriptions outside the code. Start directly with 'import numpy as np'."

    def get_task(self):
        return self.prompt_task
    
    def get_func_name(self):
        return self.prompt_func_name
    
    def get_func_inputs(self):
        return self.prompt_func_inputs
    
    def get_func_outputs(self):
        return self.prompt_func_outputs
    
    def get_inout_inf(self):
        return self.prompt_inout_inf

    def get_other_inf(self):
        return self.prompt_other_inf
