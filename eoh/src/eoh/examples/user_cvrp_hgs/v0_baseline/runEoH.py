import sys
import os
import numpy as np
import json
import importlib
# Add the src directory to sys.path
# This ensures that 'eoh' is treated as a top-level package
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

# Parameter initialization #
paras = Paras() 

def run_evolution_with_feedback(total_loops=3, gens_per_loop=2):
    import os
    arch_api_key = os.environ.get("MOONSHOT_API_KEY", "")
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if not arch_api_key or arch_api_key == "YOUR_MOONSHOT_API_KEY":
        arch_api_key = os.environ.get("moonshot_api_key", "")
    if not deepseek_api_key or deepseek_api_key == "YOUR_DEEPSEEK_API_KEY":
        deepseek_api_key = os.environ.get("deepseek_api_key", "")

    if not arch_api_key:
        print("Warning: No Moonshot API key found.")
    if not deepseek_api_key:
        print("Warning: No DeepSeek API key found.")

    arch_agent = ArchitectAgent(api_key=arch_api_key)
    refine_agent = CodeRefinerAgent(api_endpoint="https://api.deepseek.com",
                                    api_key=deepseek_api_key,
                                    model="deepseek-chat")

    current_best_fitness = float('inf')

    for i in range(total_loops):
        print(f"\n=== Feedback Loop {i+1}/{total_loops} ===")

        importlib.reload(prob)
        problem_local = prob.Evaluation()

        seed_path = os.path.join(src_path, "eoh", "seeds", "seeds_cvrp.json")
        refined_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")

        current_seed = refined_seed_path if (i > 0 and os.path.exists(refined_seed_path)) else seed_path

        paras.set_paras(method = "eoh",
                        problem = problem_local,
                        llm_api_endpoint = "https://api.deepseek.com",
                        llm_api_key = deepseek_api_key,
                        llm_model = "deepseek-chat",
                        ec_pop_size = 4,
                        ec_n_pop = gens_per_loop,
                        exp_n_proc = 4,
                        exp_debug_mode = False,
                        exp_use_seed = True, 
                        exp_use_continue = False,
                        exp_seed_path = current_seed,
                        eva_numba_decorator = False)

        # 3. Run Evolution
        evolution = EVOL(paras)
        evolution.run()
        
        # 4. Refine the Best Code
        try:
            # Get output path from evolution instance to be accurate
            output_base = evolution.paras.exp_output_path
            pop_file = os.path.join(output_base, "results", "pops", f"population_generation_{gens_per_loop-1}.json")
            
            if os.path.exists(pop_file):
                with open(pop_file, 'r', encoding='utf-8') as f:
                    population = json.load(f)
                
                if population:
                    best_ind = population[0]
                    print(f"\n[Feedback] Best fitness this loop: {best_ind['objective']:.4f}")
                    
                    # Use RefineAgent to polish the best code
                    refined_code, summary = refine_agent.refine_code(best_ind['code'], best_ind['objective'])
                    
                    if refined_code:
                        print(f"[Feedback] Refinement Summary: {summary}")
                        # Save as a new seed for the next loop
                        new_seed = [{
                            "algorithm": f"Refined version of {best_ind.get('algorithm', 'best algorithm')}: {summary}",
                            "code": refined_code
                        }]
                        with open(refined_seed_path, 'w', encoding='utf-8') as f:
                            json.dump(new_seed, f, indent=4, ensure_ascii=False)
                        print(f"[Feedback] Refined code saved to {refined_seed_path} for next loop.")
            else:
                print(f"[Warning] Population file not found: {pop_file}")
        except Exception as e:
            print(f"Error in refinement step: {e}")

        # 5. Gather Stats for Architect Agent
        best_f = float('inf')
        avg_d = 0
        try:
            output_base = evolution.paras.exp_output_path
            trajectory_file = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")
            if os.path.exists(trajectory_file):
                with open(trajectory_file, "r", encoding='utf-8') as f:
                    lines = f.readlines()
                    # Get last few entries to see recent performance
                    recent_entries = [json.loads(line) for line in lines[-10:]]
                    valid_costs = [e['cost'] for e in recent_entries if e.get('cost') is not None]
                    if valid_costs:
                        best_f = min(valid_costs)
                        avg_d = np.mean(valid_costs)
        except Exception as e:
            print(f"Error parsing feedback stats: {e}")

        stats = {
            "gen": (i + 1) * gens_per_loop,
            "best_fitness": best_f,
            "avg_dist": avg_d,
            "observation": "Fitness is calculated based on Distance + Current PRM. If Distance is not decreasing, consider simplifying the PRM."
        }
        
        # 6. Agent Refines PRM based on results
        arch_agent.design_prm("CVRP dynamic weight balancing", feedback_stats=stats)

# run 
if __name__ == "__main__":
    run_evolution_with_feedback(total_loops=3, gens_per_loop=2)
