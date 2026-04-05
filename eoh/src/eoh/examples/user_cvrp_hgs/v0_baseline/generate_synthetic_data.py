import json
import random
import os
import numpy as np

# ---------------------------------------------------------
# Quality Standards for Synthetic Data Generation
# ---------------------------------------------------------
# High Quality Criteria:
# 1. Correctness: Must be valid Python code, import numpy, and match function signature.
# 2. Performance: Algorithm complexity should be reasonable (e.g., vectorized is better than pure loops).
# 3. Diversity: Cover various heuristic families (Greedy, Geometric, Meta-heuristic, Hybrid).
# 4. Readability: Code should be structured (though EoH output is often raw, synthetic data should be clean).
#
# Quality Labels:
# - 'gold': High-performance, vectorized, sophisticated logic (e.g., SWAP*, SA, GA-XO).
# - 'silver': Correct and functional, standard heuristics (e.g., NN, Sweep, 2-opt).
# - 'bronze': Basic baselines, simple sorts, or random (useful for negative examples or starting points).
# ---------------------------------------------------------

def generate_synthetic_data(num_samples=1000):
    dataset = []
    
    # ---------------------------------------------------------
    # 1. Constructive Algorithms (Giant Tour)
    # ---------------------------------------------------------
    constructive_templates = [
        # --- Bronze (Baselines) ---
        {
            "code": """import numpy as np
def generate_giant_tour(coords, demands, dist_matrix):
    # Random Permutation
    n = len(coords)
    unvisited = list(range(1, n))
    random.shuffle(unvisited)
    return np.array(unvisited)
""",
            "alg": "Random Permutation. Baseline strategy.",
            "quality": "bronze"
        },
        {
            "code": """import numpy as np
def generate_giant_tour(coords, demands, dist_matrix):
    # Sort by Distance from Depot
    n = len(coords)
    dists = dist_matrix[0, 1:]
    indices = np.argsort(dists) + 1
    return indices
""",
            "alg": "Radial Sort. Visits closest customers first.",
            "quality": "bronze"
        },
        
        # --- Silver (Standard Heuristics) ---
        {
            "code": """import numpy as np
def generate_giant_tour(coords, demands, dist_matrix):
    # Nearest Neighbor (Greedy)
    n = len(coords)
    unvisited = list(range(1, n))
    current = 0
    tour = []
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_matrix[current, x])
        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    return np.array(tour)
""",
            "alg": "Nearest Neighbor. Classic greedy construction.",
            "quality": "silver"
        },
        {
            "code": """import numpy as np
def generate_giant_tour(coords, demands, dist_matrix):
    # Sweep Algorithm (Geometric)
    n = len(coords)
    depot = coords[0]
    angles = []
    for i in range(1, n):
        dx = coords[i][0] - depot[0]
        dy = coords[i][1] - depot[1]
        angles.append((i, np.arctan2(dy, dx)))
    angles.sort(key=lambda x: x[1])
    return np.array([x[0] for x in angles])
""",
            "alg": "Sweep Algorithm. Polar angle sorting.",
            "quality": "silver"
        },
        
        # --- Gold (Advanced/Hybrid) ---
        {
            "code": """import numpy as np
def generate_giant_tour(coords, demands, dist_matrix):
    # Farthest Insertion
    n = len(coords)
    unvisited = set(range(1, n))
    # Start with farthest from depot
    farthest = max(unvisited, key=lambda x: dist_matrix[0, x])
    tour = [farthest]
    unvisited.remove(farthest)
    
    while unvisited:
        # Find unvisited node farthest from any node in tour
        best_node = -1
        max_min_dist = -1
        
        for u in unvisited:
            min_dist_to_tour = min(dist_matrix[u, v] for v in tour)
            if min_dist_to_tour > max_min_dist:
                max_min_dist = min_dist_to_tour
                best_node = u
                
        # Insert best_node at best position
        best_pos = -1
        min_added_cost = float('inf')
        
        for i in range(len(tour) + 1):
            prev = tour[i-1] if i > 0 else tour[-1]
            curr = tour[i] if i < len(tour) else tour[0]
            cost = dist_matrix[prev, best_node] + dist_matrix[best_node, curr] - dist_matrix[prev, curr]
            if cost < min_added_cost:
                min_added_cost = cost
                best_pos = i
                
        tour.insert(best_pos, best_node)
        unvisited.remove(best_node)
        
    return np.array(tour)
""",
            "alg": "Farthest Insertion. Maximizes coverage before refinement.",
            "quality": "gold"
        },
        {
            "code": """import numpy as np
import random
def generate_giant_tour(coords, demands, dist_matrix):
    # GA-Inspired (NN + Sweep Hybrid)
    n = len(coords)
    
    # Parent 1: NN
    unvisited = list(range(1, n))
    curr = 0
    p1 = []
    while unvisited:
        nxt = min(unvisited, key=lambda x: dist_matrix[curr, x])
        p1.append(nxt)
        unvisited.remove(nxt)
        curr = nxt
        
    # Parent 2: Sweep
    depot = coords[0]
    angles = [(i, np.arctan2(coords[i][1]-depot[1], coords[i][0]-depot[0])) for i in range(1, n)]
    angles.sort(key=lambda x: x[1])
    p2 = [x[0] for x in angles]
    
    # Crossover
    cut = n // 2
    child = p1[:cut]
    seen = set(child)
    for node in p2:
        if node not in seen:
            child.append(node)
    return np.array(child)
""",
            "alg": "Hybrid GA Crossover. Combines local density (NN) with global structure (Sweep).",
            "quality": "gold"
        }
    ]
    
    # ---------------------------------------------------------
    # 2. Local Search Algorithms (Education)
    # ---------------------------------------------------------
    ls_templates = [
        # --- Bronze ---
        {
            "code": """import numpy as np
def run_education(routes, dist_matrix, demands, capacity):
    # Random Route Shuffle
    # Just shuffles customers within each route (weak improvement)
    for route in routes:
        if len(route) > 2:
            np.random.shuffle(route)
    return routes
""",
            "alg": "Intra-route Shuffle. Weak stochastic operator.",
            "quality": "bronze"
        },
        
        # --- Silver ---
        {
            "code": """import numpy as np
def run_education(routes, dist_matrix, demands, capacity):
    # 2-Opt (Intra-route)
    improved = True
    while improved:
        improved = False
        for r_idx in range(len(routes)):
            route = list(routes[r_idx])
            n = len(route)
            if n < 2: continue
            for i in range(n - 1):
                for j in range(i + 1, n):
                    # Check distance improvement
                    u, v = (0 if i==0 else route[i-1]), route[i]
                    x, y = route[j], (0 if j==n-1 else route[j+1])
                    delta = (dist_matrix[u, x] + dist_matrix[v, y]) - (dist_matrix[u, v] + dist_matrix[x, y])
                    if delta < -1e-6:
                        route[i:j+1] = route[i:j+1][::-1]
                        routes[r_idx] = route
                        improved = True
    return routes
""",
            "alg": "2-Opt. Standard edge uncrossing operator.",
            "quality": "silver"
        },
        
        # --- Gold ---
        {
            "code": """import numpy as np
def run_education(routes, dist_matrix, demands, capacity):
    # Relocate (Inter-route)
    improved = True
    while improved:
        improved = False
        for r1_idx in range(len(routes)):
            for r2_idx in range(len(routes)):
                if r1_idx == r2_idx: continue
                r1, r2 = list(routes[r1_idx]), list(routes[r2_idx])
                if not r1: continue
                
                load2 = sum(demands[c] for c in r2)
                for i, cust in enumerate(r1):
                    if load2 + demands[cust] > capacity: continue
                    
                    # Best insertion in r2
                    best_pos, min_cost = -1, float('inf')
                    for j in range(len(r2) + 1):
                        prev = 0 if j==0 else r2[j-1]
                        nxt = 0 if j==len(r2) else r2[j]
                        cost = dist_matrix[prev, cust] + dist_matrix[cust, nxt] - dist_matrix[prev, nxt]
                        if cost < min_cost:
                            min_cost = cost
                            best_pos = j
                            
                    # Cost of removal from r1
                    prev_u = 0 if i==0 else r1[i-1]
                    nxt_u = 0 if i==len(r1)-1 else r1[i+1]
                    rem_cost = dist_matrix[prev_u, nxt_u] - (dist_matrix[prev_u, cust] + dist_matrix[cust, nxt_u])
                    
                    if min_cost + rem_cost < -1e-6:
                        r1.pop(i)
                        r2.insert(best_pos, cust)
                        routes[r1_idx], routes[r2_idx] = r1, r2
                        improved = True
                        break
                if improved: break
            if improved: break
    return routes
""",
            "alg": "Relocate. Moves customers between routes to balance load and reduce distance.",
            "quality": "gold"
        },
        {
            "code": """import numpy as np
def run_education(routes, dist_matrix, demands, capacity):
    # SWAP* (Advanced Inter-route)
    def get_best_insert(route, node):
        best_cost, best_pos = float('inf'), -1
        for i in range(len(route) + 1):
            prev = 0 if i == 0 else route[i-1]
            nxt = 0 if i == len(route) else route[i]
            cost = dist_matrix[prev, node] + dist_matrix[node, nxt] - dist_matrix[prev, nxt]
            if cost < best_cost: best_cost, best_pos = cost, i
        return best_pos, best_cost

    improved = True
    while improved:
        improved = False
        for r1_idx in range(len(routes)):
            for r2_idx in range(len(routes)):
                if r1_idx >= r2_idx: continue
                r1, r2 = list(routes[r1_idx]), list(routes[r2_idx])
                if not r1 or not r2: continue
                
                l1, l2 = sum(demands[c] for c in r1), sum(demands[c] for c in r2)
                best_move, best_delta = None, 0
                
                for i, u in enumerate(r1):
                    for j, v in enumerate(r2):
                        if l1 - demands[u] + demands[v] > capacity or l2 - demands[v] + demands[u] > capacity: continue
                        
                        # Removal costs (simplified)
                        u_prev, u_next = (0 if i==0 else r1[i-1]), (0 if i==len(r1)-1 else r1[i+1])
                        rem_u = dist_matrix[u_prev, u_next] - (dist_matrix[u_prev, u] + dist_matrix[u, u_next])
                        
                        v_prev, v_next = (0 if j==0 else r2[j-1]), (0 if j==len(r2)-1 else r2[j+1])
                        rem_v = dist_matrix[v_prev, v_next] - (dist_matrix[v_prev, v] + dist_matrix[v, v_next])
                        
                        # Re-insert
                        r1_no_u = r1[:i] + r1[i+1:]
                        pos_v, cost_v = get_best_insert(r1_no_u, v)
                        
                        r2_no_v = r2[:j] + r2[j+1:]
                        pos_u, cost_u = get_best_insert(r2_no_v, u)
                        
                        delta = rem_u + rem_v + cost_v + cost_u
                        if delta < best_delta - 1e-6:
                            best_delta = delta
                            best_move = (i, j, pos_v, pos_u)
                
                if best_move:
                    i, j, pos_v, pos_u = best_move
                    u, v = r1[i], r2[j]
                    r1.pop(i); r1.insert(pos_v, v)
                    r2.pop(j); r2.insert(pos_u, u)
                    routes[r1_idx], routes[r2_idx] = r1, r2
                    improved = True; break
            if improved: break
    return routes
""",
            "alg": "SWAP*. Optimal re-insertion of swapped nodes.",
            "quality": "gold"
        }
    ]

    # Generate weighted dataset
    # 20% Bronze (Negative/Baseline)
    # 30% Silver (Standard)
    # 50% Gold (Target)
    
    counts = {
        'bronze': int(num_samples * 0.2),
        'silver': int(num_samples * 0.3),
        'gold': int(num_samples * 0.5)
    }
    
    # Adjust last to match total
    counts['gold'] += num_samples - sum(counts.values())
    
    for quality, count in counts.items():
        for _ in range(count):
            # 50/50 Constructive vs LS
            if random.random() < 0.5:
                pool = [t for t in constructive_templates if t['quality'] == quality]
                if not pool: pool = constructive_templates # Fallback
                template = random.choice(pool)
                task_type = "constructive"
                sys_prompt = "You are an expert in combinatorial optimization. Design a 'Giant Tour' generation algorithm for CVRP."
                user_prompt = "Write a Python function `generate_giant_tour(coords, demands, dist_matrix)` that returns a permutation of customers."
            else:
                pool = [t for t in ls_templates if t['quality'] == quality]
                if not pool: pool = ls_templates # Fallback
                template = random.choice(pool)
                task_type = "local_search"
                sys_prompt = "You are an expert in combinatorial optimization. Design a 'Local Search' heuristic for CVRP."
                user_prompt = "Write a Python function `run_education(routes, dist_matrix, demands, capacity)` that improves route quality."
            
            entry = {
                "conversations": [
                    {"from": "system", "value": sys_prompt},
                    {"from": "user", "value": user_prompt},
                    {"from": "assistant", "value": f"```python\n{template['code']}\n```\n\n# Algorithm: {template['alg']}\n# Quality Label: {template['quality']}"}
                ],
                "task": task_type,
                "quality": quality,
                "source": "synthetic_v2"
            }
            dataset.append(entry)
        
    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    data = generate_synthetic_data(1000)
    output_file = "cvrp_synthetic_1k_quality_labeled.jsonl"
    
    with open(output_file, 'w') as f:
        for entry in data:
            f.write(json.dumps(entry) + '\n')
            
    print(f"Generated {len(data)} synthetic samples to {output_file}")
    print("Quality Distribution:")
    from collections import Counter
    print(Counter([d['quality'] for d in data]))
