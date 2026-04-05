import os
import json
import numpy as np
import sys
import time
import importlib

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))

import prob
from eoh.utils.getParas import Paras
from eoh import EVOL

# 导入 V1 和 V2.4 的 Agent
from v1_workflow.master_agent import MasterEvolutionAgent
from v2_agent.react_master_agent import AutonomousEoHAgent
import v2_agent.react_tools as react_tools
import visualize_results

def load_config():
    config_path = os.path.join(current_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def run_v0_benchmark(instances):
    """V0: 只使用初始种群中的基准算法 (Nearest Neighbor, Sweep 等)"""
    print("\n" + "="*20 + " Running V0: Initial Seeds " + "="*20)
    from v0_baseline.heuristics_lib import get_seed_operators
    seeds = get_seed_operators()
    
    results = []
    eva = prob.Evaluation()
    
    for seed in seeds:
        code = seed['code']
        fitness = eva.evaluate(code)
        if fitness is not None:
            results.append(fitness)
            
    avg_fitness = np.mean(results) if results else float('inf')
    best_fitness = np.min(results) if results else float('inf')
    return {"avg_fitness": avg_fitness, "best_fitness": best_fitness, "none_rate": 0.0}

def run_v1_benchmark(deepseek_key, kimi_key, loops=1, gens=2):
    """V1: 固定工作流 (MasterEvolutionAgent)"""
    print("\n" + "="*20 + " Running V1: Fixed Workflow " + "="*20)
    # 为了对比公平，我们运行少量的 loop
    master = MasterEvolutionAgent(kimi_key, deepseek_key)
    # 我们手动提取 V1 运行后的结果，或者直接运行并分析
    master.run_pipeline(total_loops=loops, gens_per_loop=gens)
    
    # 分析结果 (从 v1_workflow 目录下的 results 中读取)
    # 注意：V1 和 V2.4 可能会共享结果目录，需要小心
    stats = react_tools.analyze_latest_results()
    return {
        "avg_fitness": stats['avg_dist'],
        "best_fitness": stats['best_fitness'],
        "none_rate": stats['none_rate']
    }

def run_v24_benchmark(deepseek_key, goal, loops=5):
    """V2.4: 自主 ReAct 智能体 + 协作增强"""
    print("\n" + "="*20 + " Running V2.4: ReAct Agent " + "="*20)
    agent = AutonomousEoHAgent(api_key=deepseek_key)
    agent.run(high_level_goal=goal, max_loops=loops)
    
    stats = react_tools.analyze_latest_results()
    return {
        "avg_fitness": stats['avg_dist'],
        "best_fitness": stats['best_fitness'],
        "none_rate": stats['none_rate']
    }

def main():
    config = load_config()
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY") or config.get("deepseek_api_key")
    kimi_key = os.environ.get("MOONSHOT_API_KEY") or config.get("moonshot_api_key")
    
    if not deepseek_key or not kimi_key:
        print("Error: API Keys missing.")
        return

    # 测试实例
    test_instances = ["A-n32-k5.vrp", "B-n31-k5.vrp", "P-n16-k8.vrp"]
    goal = f"Research SOTA for CVRP instances like {test_instances[0]}, then set a quantitative target and evolve a heuristic to match or exceed it."

    summary = {}

    # 1. V0 Benchmark
    summary["V0 (Seeds Only)"] = run_v0_benchmark(test_instances)

    # 2. V1 Benchmark
    summary["V1 (Workflow)"] = run_v1_benchmark(deepseek_key, kimi_key, loops=1, gens=2)

    # 3. V2.4 Benchmark
    summary["V2.4 (ReAct)"] = run_v24_benchmark(deepseek_key, goal, loops=5)

    # 打印对比报告
    print("\n" + "#"*50)
    print("      CVRP OPTIMIZATION BENCHMARK REPORT")
    print("#"*50)
    print(f"{'Version':<20} | {'Best Fitness':<15} | {'Avg Fitness':<15} | {'None Rate':<10}")
    print("-" * 65)
    for ver, stats in summary.items():
        print(f"{ver:<20} | {stats['best_fitness']:<15.2f} | {stats['avg_fitness']:<15.2f} | {stats['none_rate']:<10.2%}")
    print("#"*50)

    # 生成可视化对比图
    visualize_results.plot_performance_comparison(summary, title="CVRP Performance: V0 vs V1 vs V2.4")

if __name__ == "__main__":
    main()
