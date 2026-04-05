import os
import sys
import json
import numpy as np
import importlib
import time

# Ensure paths are correct
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
example_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if example_root not in sys.path:
    sys.path.insert(0, example_root)

from eoh import EVOL
from eoh.utils.getParas import Paras
import prob
from architect_agent import ArchitectAgent
from refine_agent import CodeRefinerAgent

class MasterEvolutionAgent:
    """
    Master Agent that orchestrates the entire evolutionary pipeline.
    It focuses on fixing 'None' results and automating feedback loops.
    """
    def __init__(self, kimi_key, deepseek_key):
        self.kimi_key = kimi_key
        self.deepseek_key = deepseek_key
        
        # 1. Initialize Sub-Agents
        self.arch_agent = ArchitectAgent(api_key=kimi_key)
        self.refine_agent = CodeRefinerAgent(
            api_endpoint="https://api.deepseek.com", 
            api_key=deepseek_key, 
            model="deepseek-chat"
        )
        self.paras = Paras()

    def run_pipeline(self, total_loops=5, gens_per_loop=2):
        print("Master Agent: Starting Automated Optimization Pipeline...")
        
        for loop in range(total_loops):
            print(f"\n{'='*20} Pipeline Loop {loop+1}/{total_loops} {'='*20}")
            
            # Step 1: Architect Designs/Refines PRM
            importlib.reload(prob)
            problem_instance = prob.Evaluation()
            
            # Step 2: Configure EoH
            seed_path = os.path.join(src_path, "eoh", "seeds", "seeds_cvrp.json")
            refined_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")
            current_seed = refined_seed_path if (loop > 0 and os.path.exists(refined_seed_path)) else seed_path

            self.paras.set_paras(
                method="eoh",
                problem=problem_instance,
                llm_api_endpoint="api.deepseek.com",
                llm_api_key=self.deepseek_key,
                llm_model="deepseek-chat",
                ec_pop_size=4,
                ec_n_pop=gens_per_loop,
                exp_n_proc=1,
                exp_use_seed=True,
                exp_seed_path=current_seed,
                eva_numba_decorator=False
            )

            # Step 3: Run Evolution
            evolution = EVOL(self.paras)
            evolution.run()

            # Step 4: Analyze Results & Fix 'None'
            stats = self._analyze_results(evolution)
            print(f"Master Agent: Loop {loop+1} Stats -> Best Fit: {stats['best_fitness']}, None Rate: {stats['none_rate']:.2%}")

            # Step 5: Refine & Fix Code
            self._refine_and_save(evolution, stats)

            # Step 6: Feedback to Architect for PRM Adjustment
            self.arch_agent.design_prm("CVRP adaptive optimization", feedback_stats=stats)

    def _analyze_results(self, evolution):
        output_base = evolution.paras.exp_output_path
        trajectory_file = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")
        
        best_f = float('inf')
        avg_d = 0
        none_count = 0
        total_count = 0
        
        # Get errors from the evaluation instance
        last_error = getattr(evolution.paras.problem, '_last_error', "None")
        last_traceback = getattr(evolution.paras.problem, '_last_traceback', "N/A")
        
        if os.path.exists(trajectory_file):
            with open(trajectory_file, "r", encoding='utf-8') as f:
                lines = f.readlines()
                recent_entries = [json.loads(line) for line in lines[-20:]]
                total_count = len(recent_entries)
                
                valid_entries = [e for e in recent_entries if e.get('cost') is not None]
                none_count = total_count - len(valid_entries)
                
                if valid_entries:
                    best_f = min(e['cost'] for e in valid_entries)
                    avg_d = np.mean([e['cost'] for e in valid_entries])

        return {
            "gen": total_count,
            "best_fitness": best_f,
            "avg_dist": avg_d,
            "none_rate": none_count / (total_count + 1e-6),
            "last_error": last_error,
            "last_traceback": last_traceback,
            "observation": "High None rate detected. Architect should simplify PRM, Refine should fix logic." if none_count / (total_count + 1e-6) > 0.3 else "Stable evolution."
        }

    def _refine_and_save(self, evolution, stats):
        output_base = evolution.paras.exp_output_path
        # Look for the last population file
        pops_dir = os.path.join(output_base, "results", "pops")
        pop_files = sorted([f for f in os.listdir(pops_dir) if f.startswith("population_generation_")])
        
        if not pop_files:
            return

        pop_file = os.path.join(pops_dir, pop_files[-1])
        refined_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")

        if os.path.exists(pop_file):
            with open(pop_file, 'r', encoding='utf-8') as f:
                population = json.load(f)
            
            if population:
                # Find the best valid individual, or the first one if all failed
                valid_inds = [ind for ind in population if ind.get('objective') is not None]
                best_ind = valid_inds[0] if valid_inds else population[0]
                
                # If the best code is still problematic or just needs polish
                refined_code, summary = self.refine_agent.refine_code(
                    best_ind['code'], 
                    best_ind.get('objective', 999999),
                    error_msg=stats['last_error'] if stats['none_rate'] > 0 else None,
                    traceback_msg=stats['last_traceback'] if stats['none_rate'] > 0 else None
                )
                
                if refined_code:
                    new_seed = [{
                        "algorithm": f"Refined (None-Fixed): {summary}",
                        "code": refined_code
                    }]
                    # Update seeds for next loop
                    with open(refined_seed_path, 'w', encoding='utf-8') as f:
                        json.dump(new_seed, f, indent=4, ensure_ascii=False)
                    print(f"Master Agent: Updated refined_seeds.json with None-fixed code.")

if __name__ == "__main__":
    # Kimi for Architecture, DeepSeek for Coding
    kimi_api = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_API_KEY") or ""
    deepseek_api = os.environ.get("DEEPSEEK_API_KEY") or ""
    
    master = MasterEvolutionAgent(kimi_api, deepseek_api)
    # Fast test: 2 loops, 1 generation each
    master.run_pipeline(total_loops=2, gens_per_loop=1)
