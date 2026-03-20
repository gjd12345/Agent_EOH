import numpy as np

def get_seed_operators():
    seeds = []
    
    # Seed 1: Nearest Neighbor (NN)
    code_nn = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
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
"""
    seeds.append({
        'algorithm': 'Nearest Neighbor. Greedily selects the closest unvisited customer.',
        'code': code_nn
    })

    # Seed 2: Sweep Algorithm
    code_sweep = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    depot = coords[0]
    angles = []
    for i in range(1, n):
        dx = coords[i][0] - depot[0]
        dy = coords[i][1] - depot[1]
        angle = np.arctan2(dy, dx)
        angles.append((i, angle))
    
    # Sort by angle
    angles.sort(key=lambda x: x[1])
    return np.array([x[0] for x in angles])
"""
    seeds.append({
        'algorithm': 'Sweep Algorithm. Sorts customers by polar angle around the depot.',
        'code': code_sweep
    })

    # Seed 3: Farthest Insertion (Simplified to Farthest Neighbor)
    code_farthest = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    unvisited = list(range(1, n))
    current = 0
    tour = []
    # Start with farthest from depot
    first = max(unvisited, key=lambda x: dist_matrix[0, x])
    tour.append(first)
    unvisited.remove(first)
    current = first
    
    while unvisited:
        # Find nearest to current (or farthest, depending on strategy, here standard NN from farthest start)
        next_node = min(unvisited, key=lambda x: dist_matrix[current, x])
        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    return np.array(tour)
"""
    seeds.append({
        'algorithm': 'Farthest Start NN. Starts with the farthest customer from depot, then NN.',
        'code': code_farthest
    })
    
    # Seed 4: Genetic Algorithm (GA) Order Crossover inspired
    code_ga = """import numpy as np
import random

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # GA often starts with random populations, but here we simulate a "child" 
    # produced by Order Crossover (OX1) from two simple parents (NN and Sweep).
    
    # Parent 1: Nearest Neighbor
    def get_nn():
        unvisited = list(range(1, n))
        curr = 0
        tour = []
        while unvisited:
            nxt = min(unvisited, key=lambda x: dist_matrix[curr, x])
            tour.append(nxt)
            unvisited.remove(nxt)
            curr = nxt
        return tour
        
    # Parent 2: Sweep
    def get_sweep():
        depot = coords[0]
        angles = []
        for i in range(1, n):
            dx = coords[i][0] - depot[0]
            dy = coords[i][1] - depot[1]
            angles.append((i, np.arctan2(dy, dx)))
        angles.sort(key=lambda x: x[1])
        return [x[0] for x in angles]

    p1 = get_nn()
    p2 = get_sweep()
    
    # Simple crossover simulation: take first half of p1, fill rest from p2
    cut = n // 2
    child = p1[:cut]
    seen = set(child)
    for node in p2:
        if node not in seen:
            child.append(node)
            
    return np.array(child)
"""
    seeds.append({
        'algorithm': 'Genetic Algorithm (GA) inspired. Simulates an Order Crossover (OX1) between a Nearest Neighbor tour and a Sweep tour.',
        'code': code_ga
    })

    # Seed 5: Particle Swarm Optimization (PSO) inspired
    code_pso = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # PSO logic: Customers are "particles". We sort them based on a "position" value.
    # The position is a mix of their angle (global trend) and distance (local feature).
    
    depot = coords[0]
    scores = []
    for i in range(1, n):
        dx = coords[i][0] - depot[0]
        dy = coords[i][1] - depot[1]
        angle = np.arctan2(dy, dx)
        dist = np.sqrt(dx**2 + dy**2)
        
        # Position formula: w1 * angle + w2 * log(dist)
        # This creates a spiral-like ordering
        score = angle + 0.1 * np.log(dist + 1e-6)
        scores.append((i, score))
        
    scores.sort(key=lambda x: x[1])
    return np.array([x[0] for x in scores])
"""
    seeds.append({
        'algorithm': 'Particle Swarm Optimization (PSO) inspired. Orders customers based on a composite score of polar angle and radial distance, simulating a spiral movement.',
        'code': code_pso
    })

    # Seed 6: Differential Evolution (DE) inspired
    code_de = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # DE logic: Mutation of coordinate space.
    # We project coordinates onto a random vector (mutation) and sort.
    
    # Target vector (Depot-Centric)
    target = coords[1:] - coords[0]
    
    # Random perturbation vector
    np.random.seed(42) # Deterministic for seed
    F = 0.8
    r1 = np.random.rand(n-1, 2)
    r2 = np.random.rand(n-1, 2)
    
    # Mutant vectors
    mutant = target + F * (r1 - r2)
    
    # Calculate "value" of each customer based on projection onto main axis (e.g., X+Y)
    values = []
    for i in range(n-1):
        # Simple projection score
        score = mutant[i][0] + mutant[i][1]
        values.append((i+1, score))
        
    values.sort(key=lambda x: x[1])
    return np.array([x[0] for x in values])
"""
    seeds.append({
        'algorithm': 'Differential Evolution (DE) inspired. Projects customer coordinates onto a mutated vector space and sorts them to generate the tour.',
        'code': code_de
    })

    # Seed 7: Simulated Annealing (SA) inspired
    code_sa = """import numpy as np
import math
import random

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    unvisited = list(range(1, n))
    current = 0
    tour = [current]
    
    # Initial Solution: Nearest Neighbor
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_matrix[current, x])
        tour.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    
    tour = tour[1:] # Remove depot for now, keeping it consistent with other seeds which return permutation of customers
    
    # SA Parameters
    T = 100.0
    alpha = 0.95
    max_iter = 1000
    
    best_tour = list(tour)
    current_tour = list(tour)
    
    def calculate_cost(t):
        cost = dist_matrix[0, t[0]]
        for i in range(len(t)-1):
            cost += dist_matrix[t[i], t[i+1]]
        cost += dist_matrix[t[-1], 0]
        return cost
        
    current_cost = calculate_cost(current_tour)
    best_cost = current_cost
    
    for i in range(max_iter):
        # Swap two random elements
        idx1, idx2 = random.sample(range(len(current_tour)), 2)
        new_tour = list(current_tour)
        new_tour[idx1], new_tour[idx2] = new_tour[idx2], new_tour[idx1]
        
        new_cost = calculate_cost(new_tour)
        
        delta = new_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_tour = new_tour
            current_cost = new_cost
            if current_cost < best_cost:
                best_cost = current_cost
                best_tour = list(current_tour)
                
        T *= alpha
        
    return np.array(best_tour)
"""
    seeds.append({
        'algorithm': 'Simulated Annealing (SA). Starts with NN solution and improves it by random swaps with probabilistic acceptance of worse solutions.',
        'code': code_sa
    })

    # Seed 8: Ant Colony Optimization (ACO) inspired
    code_aco = """import numpy as np
import random

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # Simplified ACO: Probabilistic construction based on pheromone (inverse distance)
    
    unvisited = list(range(1, n))
    current = 0
    tour = []
    
    alpha = 1.0 # Pheromone importance (here just inverse distance)
    beta = 2.0  # Heuristic importance
    
    while unvisited:
        probs = []
        for node in unvisited:
            dist = dist_matrix[current, node]
            if dist == 0: dist = 0.1
            prob = (1.0 / dist) ** beta
            probs.append(prob)
            
        total_prob = sum(probs)
        probs = [p / total_prob for p in probs]
        
        # Roulette Wheel Selection
        r = random.random()
        cumulative = 0.0
        selected_node = unvisited[-1]
        for i, node in enumerate(unvisited):
            cumulative += probs[i]
            if r <= cumulative:
                selected_node = node
                break
                
        tour.append(selected_node)
        unvisited.remove(selected_node)
        current = selected_node
        
    return np.array(tour)
"""
    seeds.append({
        'algorithm': 'Ant Colony Optimization (ACO) inspired. Constructs a tour probabilistically where shorter edges have higher probability of selection.',
        'code': code_aco
    })

    # Seed 9: Tabu Search (TS) inspired
    code_ts = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # Initial Solution: Nearest Neighbor
    unvisited = list(range(1, n))
    curr = 0
    tour = []
    while unvisited:
        nxt = min(unvisited, key=lambda x: dist_matrix[curr, x])
        tour.append(nxt)
        unvisited.remove(nxt)
        curr = nxt
        
    # Tabu Search parameters
    max_iter = 200
    tabu_list = []
    tabu_tenure = 10
    
    best_tour = list(tour)
    current_tour = list(tour)
    
    def calculate_cost(t):
        c = dist_matrix[0, t[0]]
        for k in range(len(t)-1): c += dist_matrix[t[k], t[k+1]]
        c += dist_matrix[t[-1], 0]
        return c
        
    best_cost = calculate_cost(best_tour)
    
    for _ in range(max_iter):
        best_neighbor = None
        best_neighbor_cost = float('inf')
        move = None
        
        # Evaluate 2-opt neighbors (subset for speed)
        for i in range(len(current_tour) - 1):
            for j in range(i + 1, len(current_tour)):
                if (i, j) in tabu_list: continue
                
                # Create neighbor
                neighbor = list(current_tour)
                neighbor[i:j+1] = neighbor[i:j+1][::-1]
                cost = calculate_cost(neighbor)
                
                if cost < best_neighbor_cost:
                    best_neighbor_cost = cost
                    best_neighbor = neighbor
                    move = (i, j)
        
        if best_neighbor:
            current_tour = best_neighbor
            tabu_list.append(move)
            if len(tabu_list) > tabu_tenure:
                tabu_list.pop(0)
                
            if best_neighbor_cost < best_cost:
                best_cost = best_neighbor_cost
                best_tour = list(best_neighbor)
                
    return np.array(best_tour)
"""
    seeds.append({
        'algorithm': 'Tabu Search (TS). Starts with NN and explores 2-opt neighbors while avoiding recently visited moves (Tabu list).',
        'code': code_ts
    })

    # Seed 10: Space Filling Curve (Hilbert) inspired
    code_hilbert = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    # Hilbert Curve Mapping
    # Map 2D coordinates to 1D Hilbert distance
    
    def rot(n, x, y, rx, ry):
        if ry == 0:
            if rx == 1:
                x = n - 1 - x
                y = n - 1 - y
            return y, x
        return x, y

    def xy2d(n, x, y):
        rx, ry, s, d = 0, 0, 0, 0
        s = n // 2
        while s > 0:
            rx = 1 if (x & s) > 0 else 0
            ry = 1 if (y & s) > 0 else 0
            d += s * s * ((3 * rx) ^ ry)
            x, y = rot(s, x, y, rx, ry)
            s //= 2
        return d

    # Normalize coords to grid
    n_points = len(coords)
    min_x, min_y = np.min(coords, axis=0)
    max_x, max_y = np.max(coords, axis=0)
    scale = 2**10 # 1024x1024 grid
    
    hilbert_indices = []
    for i in range(1, n_points):
        nx = int((coords[i][0] - min_x) / (max_x - min_x + 1e-6) * (scale - 1))
        ny = int((coords[i][1] - min_y) / (max_y - min_y + 1e-6) * (scale - 1))
        h_dist = xy2d(scale, nx, ny)
        hilbert_indices.append((i, h_dist))
        
    hilbert_indices.sort(key=lambda x: x[1])
    return np.array([x[0] for x in hilbert_indices])
"""
    seeds.append({
        'algorithm': 'Space Filling Curve (Hilbert). Maps 2D coordinates to 1D Hilbert distances to preserve locality.',
        'code': code_hilbert
    })

    # Seed 11: Minimum Spanning Tree (MST) Preorder
    code_mst = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    # Prim's Algorithm for MST
    visited = [False] * n
    min_dist = [float('inf')] * n
    parent = [-1] * n
    
    min_dist[0] = 0
    
    for _ in range(n):
        # Find min dist node
        u = -1
        min_val = float('inf')
        for i in range(n):
            if not visited[i] and min_dist[i] < min_val:
                min_val = min_dist[i]
                u = i
        
        if u == -1: break
        visited[u] = True
        
        for v in range(n):
            if not visited[v] and dist_matrix[u, v] < min_dist[v]:
                min_dist[v] = dist_matrix[u, v]
                parent[v] = u
                
    # Build Adjacency List from Parent array
    adj = [[] for _ in range(n)]
    for i in range(1, n):
        adj[parent[i]].append(i)
        
    # Preorder Traversal (DFS)
    tour = []
    stack = [0]
    while stack:
        u = stack.pop()
        if u != 0: tour.append(u)
        # Add children to stack in reverse order to process them in order
        # Sorting children by angle or distance could be an enhancement
        for v in reversed(adj[u]):
            stack.append(v)
            
    return np.array(tour)
"""
    seeds.append({
        'algorithm': 'Minimum Spanning Tree (MST). Constructs an MST and performs a preorder traversal (DFS) to generate the tour.',
        'code': code_mst
    })

    # Seed 12: Cluster-First Route-Second (K-Means)
    code_kmeans = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n_points = len(coords)
    customers = coords[1:]
    
    # Simple K-Means
    k = max(1, int(n_points / 10)) # Heuristic K
    
    # Initialize centroids randomly
    indices = np.random.choice(len(customers), k, replace=False)
    centroids = customers[indices]
    
    clusters = [[] for _ in range(k)]
    labels = [-1] * len(customers)
    
    for _ in range(10): # 10 iterations
        clusters = [[] for _ in range(k)]
        # Assignment
        for i, p in enumerate(customers):
            dists = np.sum((centroids - p)**2, axis=1)
            label = np.argmin(dists)
            clusters[label].append(i + 1) # +1 for original index
            labels[i] = label
            
        # Update
        for i in range(k):
            if clusters[i]:
                points_idx = [idx-1 for idx in clusters[i]]
                centroids[i] = np.mean(customers[points_idx], axis=0)
                
    # Concatenate clusters
    # Within each cluster, sort by distance to centroid (or angle)
    tour = []
    
    # Sort clusters by angle from depot
    cluster_angles = []
    depot = coords[0]
    for i in range(k):
        if not clusters[i]: 
            cluster_angles.append(0)
            continue
        dx = centroids[i][0] - depot[0]
        dy = centroids[i][1] - depot[1]
        cluster_angles.append(np.arctan2(dy, dx))
        
    sorted_clusters_idx = np.argsort(cluster_angles)
    
    for c_idx in sorted_clusters_idx:
        cluster_nodes = clusters[c_idx]
        if not cluster_nodes: continue
        
        # Sort nodes within cluster by angle relative to centroid
        cent = centroids[c_idx]
        nodes_angles = []
        for node_idx in cluster_nodes:
            p = coords[node_idx]
            angle = np.arctan2(p[1] - cent[1], p[0] - cent[0])
            nodes_angles.append((node_idx, angle))
        
        nodes_angles.sort(key=lambda x: x[1])
        tour.extend([x[0] for x in nodes_angles])
        
    # Handle any unassigned (rare)
    seen = set(tour)
    for i in range(1, n_points):
        if i not in seen:
            tour.append(i)
            
    return np.array(tour)
"""
    seeds.append({
        'algorithm': 'K-Means Clustering. Clusters customers first, sorts clusters angularly, and sorts customers within clusters.',
        'code': code_kmeans
    })

    # Seed 13: Nearest Insertion
    code_ni = """import numpy as np

def generate_giant_tour(coords, demands, dist_matrix):
    n = len(coords)
    unvisited = set(range(1, n))
    
    # Start with a triangle (Depot + 2 nearest)
    # Actually, giant tour just needs a sequence. 
    # Let's start with depot -> nearest -> depot
    
    nearest = min(unvisited, key=lambda x: dist_matrix[0, x])
    tour = [nearest]
    unvisited.remove(nearest)
    
    while unvisited:
        # Find (node_in_tour, node_unvisited) with min distance
        best_u = -1
        best_v = -1
        min_dist = float('inf')
        
        for u in tour:
            for v in unvisited:
                d = dist_matrix[u, v]
                if d < min_dist:
                    min_dist = d
                    best_u = u
                    best_v = v
                    
        # Insert v next to u
        # We need to decide whether to insert before or after u
        # In a giant tour context (linear), let's just insert after u
        idx = tour.index(best_u)
        tour.insert(idx + 1, best_v)
        unvisited.remove(best_v)
        
    return np.array(tour)
"""
    seeds.append({
        'algorithm': 'Nearest Insertion. Iteratively inserts the nearest unvisited node into the tour next to its closest visited neighbor.',
        'code': code_ni
    })

    return seeds
