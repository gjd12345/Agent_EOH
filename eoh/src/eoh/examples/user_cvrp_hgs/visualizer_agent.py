import os
import matplotlib.pyplot as plt
import numpy as np
import json
import re

class VisualizerAgent:
    """
    Visualizer Agent for EoH.
    Responsible for generating plots, convergence curves, and embedding them into reports.
    """
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_convergence_curve(self, trajectory_file: str, instance_name: str = "CVRP") -> str:
        """
        Generates a convergence curve (Fitness vs. Generation) from trajectory.jsonl.
        """
        if not os.path.exists(trajectory_file):
            return "Failed: Trajectory file not found."

        generations = []
        best_fitnesses = []
        current_best = float('inf')

        try:
            with open(trajectory_file, "r", encoding='utf-8') as f:
                for i, line in enumerate(f):
                    data = json.loads(line)
                    cost = data.get('cost')
                    if cost is not None:
                        current_best = min(current_best, cost)
                    generations.append(i + 1)
                    best_fitnesses.append(current_best if current_best != float('inf') else None)

            # Filter out None values for plotting
            valid_indices = [i for i, v in enumerate(best_fitnesses) if v is not None]
            x = [generations[i] for i in valid_indices]
            y = [best_fitnesses[i] for i in valid_indices]

            plt.figure(figsize=(10, 6))
            plt.plot(x, y, marker='o', linestyle='-', color='#e67e22', markersize=4, label='Best Fitness')
            plt.title(f"Evolution Convergence Curve - {instance_name}")
            plt.xlabel("Generation (Individual Index)")
            plt.ylabel("Cost (Lower is Better)")
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()

            save_path = os.path.join(self.output_dir, f"convergence_{instance_name}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        except Exception as e:
            return f"Error generating convergence curve: {e}"

    def embed_visuals_to_notes(self, image_paths: list, notes_path: str, section: str = "Visual Reports") -> str:
        """
        Embeds image links into research_notes.md.
        """
        if not os.path.exists(notes_path):
            return "Notes file not found."

        try:
            with open(notes_path, "a", encoding="utf-8") as f:
                f.write(f"\n## 🖼️ {section}\n")
                for path in image_paths:
                    rel_path = os.path.relpath(path, os.path.dirname(notes_path))
                    # Use markdown image syntax
                    f.write(f"![{os.path.basename(path)}]({rel_path})\n\n")
            return "Successfully embedded visuals into research notes."
        except Exception as e:
            return f"Error embedding visuals: {e}"

if __name__ == "__main__":
    viz = VisualizerAgent()
    # Test would go here if we had a sample trajectory file
