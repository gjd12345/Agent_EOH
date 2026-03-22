import os
import json
import datetime

class DatasetCollector:
    """
    Collector for PRM strategies and their corresponding evolution trajectories.
    Used for post-training / fine-tuning of LLMs.
    """
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "training_data")
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.current_prm_file = os.path.join(self.base_dir, "current_prm_metadata.json")

    def log_prm_design(self, prm_code, reasoning, problem_desc):
        """Logs a new PRM design from the Architect."""
        metadata = {
            "timestamp": datetime.datetime.now().isoformat(),
            "problem": problem_desc,
            "prm_code": prm_code,
            "architect_reasoning": reasoning,
            "paired": False
        }
        with open(self.current_prm_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        print(f"[DatasetCollector] Logged new PRM metadata to {self.current_prm_file}")

    def pair_with_trajectory(self, trajectory_stats):
        """Pairs the current PRM with the resulting evolution stats and saves to permanent dataset."""
        if not os.path.exists(self.current_prm_file):
            print("[DatasetCollector] Warning: No current PRM metadata found to pair.")
            return

        with open(self.current_prm_file, 'r', encoding='utf-8') as f:
            prm_data = json.load(f)

        # Merge with trajectory stats
        full_entry = {
            **prm_data,
            "trajectory_results": trajectory_stats,
            "paired": True,
            "paired_at": datetime.datetime.now().isoformat()
        }

        # Save to main dataset file
        dataset_file = os.path.join(self.base_dir, "prm_evolution_dataset.jsonl")
        with open(dataset_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(full_entry, ensure_ascii=False) + "\n")
        
        # Clean up current metadata
        os.remove(self.current_prm_file)
        print(f"[DatasetCollector] Successfully paired PRM with results and saved to {dataset_file}")

collector = DatasetCollector()
