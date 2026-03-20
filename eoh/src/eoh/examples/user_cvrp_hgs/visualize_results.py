import os
import matplotlib.pyplot as plt
import numpy as np
from generate_performance_dataset import read_vrplib_instance, split_giant_tour
from prob import Evaluation

def plot_cvrp_solution(instance_name, coords, routes, cost, title_suffix=""):
    """
    Plots the CVRP solution.
    coords: N x 2 array of coordinates (index 0 is depot).
    routes: list of lists, where each inner list contains customer indices for one route.
    cost: total cost of the solution.
    """
    plt.figure(figsize=(10, 8))
    
    # Plot depot
    plt.scatter(coords[0, 0], coords[0, 1], c='red', marker='s', s=150, label='Depot', zorder=5)
    
    # Plot customers
    plt.scatter(coords[1:, 0], coords[1:, 1], c='blue', marker='o', s=30, label='Customers', zorder=4)
    
    # Colors for different routes
    colors = plt.cm.tab20(np.linspace(0, 1, max(10, len(routes))))
    
    # Plot routes
    for idx, route in enumerate(routes):
        if not route:
            continue
            
        # Add depot to start and end of route for plotting
        full_route = [0] + list(route) + [0]
        route_coords = coords[full_route]
        
        plt.plot(route_coords[:, 0], route_coords[:, 1], '-', 
                 color=colors[idx % len(colors)], linewidth=2, alpha=0.7)
        
    plt.title(f"CVRP Solution - {instance_name} {title_suffix}\nTotal Cost: {cost:.2f}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Save the plot
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
    os.makedirs(output_dir, exist_ok=True)
    
    safe_title = title_suffix.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
    save_path = os.path.join(output_dir, f"{instance_name}_{safe_title}.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved visualization to {save_path}")

def run_and_visualize():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    # Pick a specific instance to visualize, e.g., P-n16-k8.vrp or A-n32-k5.vrp
    target_instance = "P-n22-k8.vrp" 
    file_path = os.path.join(data_dir, target_instance)
    
    if not os.path.exists(file_path):
        print(f"Instance {target_instance} not found. Searching for alternatives...")
        files = [f for f in os.listdir(data_dir) if f.endswith(".vrp")]
        if not files:
            print("No .vrp files found in data directory.")
            return
        target_instance = files[0]
        file_path = os.path.join(data_dir, target_instance)
        
    print(f"Visualizing instance: {target_instance}")
    instance = read_vrplib_instance(file_path)
    coords = instance['coords']
    demands = instance['demands']
    dist_matrix = instance['dist_matrix']
    capacity = instance['capacity']
    
    eva = Evaluation()
    
    # Algorithm 1: Nearest Neighbor (Constructive)
    def generate_giant_tour_nn(coords, demands, dist_matrix):
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
        
    # Algorithm 2: Sweep Algorithm (Route-First)
    def generate_giant_tour_sweep(coords, demands, dist_matrix):
        n = len(coords)
        depot = coords[0]
        angles = []
        for i in range(1, n):
            dx = coords[i][0] - depot[0]
            dy = coords[i][1] - depot[1]
            angle = np.arctan2(dy, dx)
            angles.append((i, angle))
        angles.sort(key=lambda x: x[1])
        return np.array([x[0] for x in angles])

    algorithms = [
        ("Nearest_Neighbor", generate_giant_tour_nn),
        ("Sweep_Algorithm", generate_giant_tour_sweep)
    ]
    
    for name, alg_func in algorithms:
        # 1. Generate Giant Tour
        giant_tour = alg_func(coords, demands, dist_matrix)
        
        # 2. Optimal Split
        routes = eva.optimal_split(giant_tour, demands, dist_matrix, capacity)
        
        # 3. Local Search (Optional, but shows the full pipeline)
        # routes = eva.run_local_search(routes, dist_matrix, demands, capacity)
        
        # 4. Calculate final cost
        cost = eva.calculate_total_distance(routes, dist_matrix)
        
        # 5. Plot
        plot_cvrp_solution(target_instance, coords, routes, cost, title_suffix=name)

if __name__ == "__main__":
    run_and_visualize()
