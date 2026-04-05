import os
import matplotlib.pyplot as plt
import numpy as np
from v0_baseline.generate_performance_dataset import read_vrplib_instance
from prob import Evaluation

def plot_cvrp_solution(instance_name, coords, routes, cost, title_suffix=""):
    """
    Plots the CVRP solution.
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
            
        full_route = [0] + list(route) + [0]
        route_coords = coords[full_route]
        
        plt.plot(route_coords[:, 0], route_coords[:, 1], '-', 
                 color=colors[idx % len(colors)], linewidth=2, alpha=0.7)
        
    plt.title(f"CVRP Solution - {instance_name} {title_suffix}\nTotal Cost: {cost:.2f}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
    os.makedirs(output_dir, exist_ok=True)
    
    safe_title = title_suffix.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
    save_path = os.path.join(output_dir, f"{instance_name}_{safe_title}.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved visualization to {save_path}")

def plot_performance_comparison(summary_data, title="CVRP Performance Comparison"):
    """
    Plots a bar chart comparing different versions (V0, V1, V2.4).
    summary_data: dict { 'Version_Name': {'best_fitness': val, ...} }
    """
    versions = list(summary_data.keys())
    best_fitnesses = [data['best_fitness'] for data in summary_data.values()]
    avg_fitnesses = [data.get('avg_fitness', 0) for data in summary_data.values()]
    
    x = np.arange(len(versions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    rects1 = ax.bar(x - width/2, best_fitnesses, width, label='Best Fitness', color='#2ecc71')
    rects2 = ax.bar(x + width/2, avg_fitnesses, width, label='Avg Fitness', color='#3498db')
    
    ax.set_ylabel('Cost (Lower is Better)')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(versions)
    ax.legend()
    
    # Add labels on top of bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f'{height:.1f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    
    fig.tight_layout()
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "performance_comparison_report.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved performance comparison chart to {save_path}")

def run_and_visualize():
    """Default visualization for NN vs Sweep (V0 seeds)."""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v0_baseline", "data")
    target_instance = "A-n32-k5.vrp" 
    file_path = os.path.join(data_dir, target_instance)
    
    if not os.path.exists(file_path):
        files = [f for f in os.listdir(data_dir) if f.endswith(".vrp")]
        if not files: return
        target_instance = files[0]
        file_path = os.path.join(data_dir, target_instance)
        
    instance = read_vrplib_instance(file_path)
    eva = Evaluation()
    
    # Mock summary data for demonstration if running standalone
    summary_mock = {
        "V0 (Baseline)": {"best_fitness": 1250.4, "avg_fitness": 1420.3},
        "V1 (Workflow)": {"best_fitness": 1180.2, "avg_fitness": 1250.1},
        "V2.4 (ReAct)": {"best_fitness": 1023.9, "avg_fitness": 1105.5}
    }
    plot_performance_comparison(summary_mock)

if __name__ == "__main__":
    run_and_visualize()
