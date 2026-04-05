import json
import numpy as np
import random
import os
import sys

# Add the current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import heuristics_lib
except ImportError:
    # If run from root, adjust path
    sys.path.append(os.path.join(os.getcwd(), 'eoh/src/eoh/examples/user_cvrp_hgs'))
    import heuristics_lib

def read_vrplib_instance(file_path):
    """Parse CVRPLIB .vrp file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    instance = {}
    coord_section = False
    demand_section = False
    coords = []
    demands = []
    
    for line in lines:
        if "CAPACITY" in line:
            instance['capacity'] = int(line.split()[-1])
        elif "NODE_COORD_SECTION" in line:
            coord_section = True
            continue
        elif "DEMAND_SECTION" in line:
            coord_section = False
            demand_section = True
            continue
        elif "DEPOT_SECTION" in line:
            break
            
        if coord_section:
            parts = line.split()
            # CVRPLIB uses 1-based indexing, we keep it but coords[0] will be depot
            # Sometimes parts might not be float friendly, skip if fails
            try:
                coords.append([float(parts[1]), float(parts[2])])
            except:
                pass
        elif demand_section:
            try:
                demands.append(int(line.split()[1]))
            except:
                pass
            
    instance['coords'] = np.array(coords)
    instance['demands'] = np.array(demands)
    instance['n_customers'] = len(coords) - 1
    
    # Calculate distance matrix
    dist_matrix = np.sqrt(np.sum((instance['coords'][:, np.newaxis, :] - instance['coords'][np.newaxis, :, :]) ** 2, axis=-1))
    instance['dist_matrix'] = dist_matrix
    instance['name'] = os.path.basename(file_path)
    
    return instance

def evaluate_solution(routes, dist_matrix):
    """Calculates total distance of the routes."""
    total_dist = 0
    for route in routes:
        if not route: continue
        # Depot -> First
        total_dist += dist_matrix[0, route[0]]
        # Inter-node
        for i in range(len(route) - 1):
            total_dist += dist_matrix[route[i], route[i+1]]
        # Last -> Depot
        total_dist += dist_matrix[route[-1], 0]
    return total_dist

def split_giant_tour(tour, demands, capacity, dist_matrix):
    """
    Simple Split algorithm (Optimal Split is better but this is a fast baseline).
    Splits the giant tour into feasible routes respecting capacity.
    """
    routes = []
    current_route = []
    current_load = 0
    
    for node in tour:
        node_demand = demands[node]
        if current_load + node_demand <= capacity:
            current_route.append(node)
            current_load += node_demand
        else:
            routes.append(current_route)
            current_route = [node]
            current_load = node_demand
            
    if current_route:
        routes.append(current_route)
        
    return routes

def main():
    print("Generating Performance Dataset on Real CVRPLib Instances...")
    
    # 1. Configuration
    num_runs_per_alg = 5  # Run stochastic algorithms multiple times
    output_file = "cvrp_performance_dataset_real.jsonl"
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    # 2. Load Heuristics
    seeds = heuristics_lib.get_seed_operators()
    print(f"Loaded {len(seeds)} heuristic algorithms.")
    
    # 3. Load Real Instances
    instance_files = [f for f in os.listdir(data_dir) if f.endswith(".vrp")]
    print(f"Found {len(instance_files)} instances: {instance_files}")
    
    dataset = []
    
    # 4. Generation Loop
    for file_name in instance_files:
        file_path = os.path.join(data_dir, file_name)
        try:
            instance = read_vrplib_instance(file_path)
        except Exception as e:
            print(f"Failed to read {file_name}: {e}")
            continue
            
        n = instance['n_customers']
        coords = instance['coords']
        demands = instance['demands']
        dist_matrix = instance['dist_matrix']
        capacity = instance['capacity']
        
        print(f"Processing {instance['name']} (n={n})...")
        
        # Metadata for the problem
        problem_desc = f"CVRP Instance {instance['name']} with {n} customers, Capacity {capacity}. Coordinates and Demands provided."
        
        # Evaluate each heuristic
        for seed in seeds:
            code = seed['code']
            alg_name = seed.get('algorithm', 'Unknown Algorithm')
            
            # Run multiple rounds for robustness
            costs = []
            best_routes = None
            best_cost = float('inf')
            
            # Check if deterministic (heuristic guess)
            is_deterministic = "random" not in code and "shuffle" not in code and "np.random" not in code
            current_runs = 1 if is_deterministic else num_runs_per_alg
            
            for run_idx in range(current_runs):
                try:
                    # Dynamic execution of the heuristic code
                    local_scope = {}
                    exec(code, local_scope)
                    
                    if 'generate_giant_tour' not in local_scope:
                        continue
                        
                    generate_giant_tour = local_scope['generate_giant_tour']
                    
                    # Run Algorithm
                    tour = generate_giant_tour(coords, demands, dist_matrix)
                    
                    # Verify Tour (must be permutation of 1..n)
                    if len(tour) != n:
                        # Some algorithms might return different lengths or fail
                        continue
                        
                    # Split into routes
                    routes = split_giant_tour(tour, demands, capacity, dist_matrix)
                    
                    # Calculate Cost
                    cost = evaluate_solution(routes, dist_matrix)
                    costs.append(cost)
                    
                    if cost < best_cost:
                        best_cost = cost
                        best_routes = routes
                        
                except Exception as e:
                    # print(f"Error running {alg_name}: {e}")
                    pass
            
            if not costs:
                continue
                
            avg_cost = sum(costs) / len(costs)
            min_cost = min(costs)
            
            # Create Dataset Entry (Use Best Result)
            # We record statistics in metadata
            
            # Formatted for SFT (ShareGPT style)
            sft_entry = {
                "conversations": [
                    {
                        "from": "system",
                        "value": "You are an expert in combinatorial optimization. Solve the following CVRP problem using a constructive heuristic."
                    },
                    {
                        "from": "user",
                        "value": f"Problem: {problem_desc}\nWrite a Python function `generate_giant_tour` to solve it."
                    },
                    {
                        "from": "assistant",
                        "value": f"I will use {alg_name}. This algorithm achieved a best cost of {min_cost:.2f} (Avg: {avg_cost:.2f}) on this instance.\n\n```python\n{code}\n```"
                    }
                ],
                "metadata": {
                    "instance": instance['name'],
                    "n_customers": n,
                    "algorithm": alg_name,
                    "best_cost": min_cost,
                    "avg_cost": avg_cost,
                    "num_runs": current_runs
                }
            }
            
            dataset.append(sft_entry)
            print(f"  > {alg_name[:30]}...: Best={min_cost:.2f}, Avg={avg_cost:.2f}")

    # 5. Save
    with open(output_file, 'w') as f:
        for entry in dataset:
            f.write(json.dumps(entry) + '\n')
            
    print(f"Generated {len(dataset)} performance-labeled samples to {output_file}")

if __name__ == "__main__":
    main()
