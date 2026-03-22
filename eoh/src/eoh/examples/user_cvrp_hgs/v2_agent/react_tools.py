"""
This file contains the 'toolbox' for the Autonomous EoH Agent.
Each function here is a 'tool' that the ReAct agent can decide to use.
"""
import os
import sys
import json
import numpy as np
import importlib
import requests
import datetime
import subprocess

# Ensure paths are correct for standalone execution
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
from analyst_agent import AnalystAgent
from reviewer_agent import ReviewerAgent
from librarian_agent import LibrarianAgent
from visualizer_agent import VisualizerAgent
from deployer_agent import DeployerAgent
from v2_agent.dataset_collector import collector as dataset_collector

# --- Global State Management ---
# This is a simple way to pass state (the EVOL instance) between tools.
_last_evolution_instance = None

# --- Configuration Management ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_env_key(env_name, config_key, fallback=""):
    return os.environ.get(env_name) or os.environ.get(config_key, fallback)

# --- Agent Instances (Singleton-like) ---
_architect_agent = None
_refine_agent = None
_analyst_agent = None
_reviewer_agent = None
_librarian_agent = None
_visualizer_agent = None
_deployer_agent = None

def get_architect_agent():
    global _architect_agent
    if _architect_agent is None:
        config = load_config()
        # KIMI (Moonshot) for Architect: High-level strategy design
        key = get_env_key("MOONSHOT_API_KEY", "moonshot_api_key")
        if not key or key == "YOUR_MOONSHOT_API_KEY":
            key = config.get("moonshot_api_key", "")
        _architect_agent = ArchitectAgent(api_key=key, endpoint="api.moonshot.cn", model="moonshot-v1-8k")
    return _architect_agent

def get_refine_agent():
    global _refine_agent
    if _refine_agent is None:
        config = load_config()
        # DeepSeek for Code Refiner: Logical reasoning and code fixing
        key = get_env_key("DEEPSEEK_API_KEY", "deepseek_api_key")
        if not key or key == "YOUR_DEEPSEEK_API_KEY":
            key = config.get("deepseek_api_key", "")
        _refine_agent = CodeRefinerAgent(
            api_endpoint="https://api.deepseek.com",
            api_key=key,
            model="deepseek-chat"
        )
    return _refine_agent

def get_analyst_agent():
    global _analyst_agent
    if _analyst_agent is None:
        config = load_config()
        key = get_env_key("DEEPSEEK_API_KEY", "deepseek_api_key")
        if not key or key == "YOUR_DEEPSEEK_API_KEY":
            key = config.get("deepseek_api_key", "")
        _analyst_agent = AnalystAgent(api_key=key)
    return _analyst_agent

def get_reviewer_agent():
    global _reviewer_agent
    if _reviewer_agent is None:
        _reviewer_agent = ReviewerAgent()
    return _reviewer_agent

def get_librarian_agent():
    global _librarian_agent
    if _librarian_agent is None:
        config = load_config()
        key = get_env_key("DEEPSEEK_API_KEY", "deepseek_api_key")
        if not key or key == "YOUR_DEEPSEEK_API_KEY":
            key = config.get("deepseek_api_key", "")
        _librarian_agent = LibrarianAgent(api_key=key)
    return _librarian_agent

def get_visualizer_agent():
    global _visualizer_agent
    if _visualizer_agent is None:
        _visualizer_agent = VisualizerAgent()
    return _visualizer_agent

def get_deployer_agent():
    global _deployer_agent
    if _deployer_agent is None:
        _deployer_agent = DeployerAgent()
    return _deployer_agent

# --- Tool Definitions ---

def run_evolution(generations: int, seed_path: str = None) -> str:
    """
    Runs the EoH evolutionary process for a specified number of generations.
    
    Args:
        generations (int): The number of generations to run the evolution for.
        seed_path (str, optional): Path to a specific seed file. If None, uses default.

    Returns:
        str: A summary of the evolution results.
    """
    print(f"\n[Tool] Running evolution for {generations} generation(s)...")
    global _last_evolution_instance
    paras = Paras()
    importlib.reload(prob)
    problem_instance = prob.Evaluation()

    # Robust seed path handling
    if seed_path and os.path.exists(seed_path):
        current_seed_path = os.path.abspath(seed_path)
        print(f"Using provided seed file: {current_seed_path}")
    else:
        current_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")
        if not os.path.exists(current_seed_path):
            current_seed_path = os.path.join(src_path, "eoh", "seeds", "seeds_cvrp.json")
        current_seed_path = os.path.abspath(current_seed_path)
        print(f"Using default or refined seed file: {current_seed_path}")

    config = load_config()
    key = get_env_key("DEEPSEEK_API_KEY", "deepseek_api_key")
    if not key or key == "YOUR_DEEPSEEK_API_KEY":
        key = config.get("deepseek_api_key", "")

    paras.set_paras(
        method="eoh",
        problem=problem_instance,
        llm_api_endpoint="api.deepseek.com",
        llm_api_key=key,
        llm_model="deepseek-chat",
        ec_pop_size=4,
        ec_n_pop=generations,
        exp_n_proc=1,
        exp_use_seed=True,
        exp_seed_path=current_seed_path,
        eva_numba_decorator=False
    )

    evolution = EVOL(paras)
    _last_evolution_instance = evolution # Save instance for other tools
    evolution.run()
    
    stats = analyze_latest_results()
    
    # Log for post-training dataset: pair PRM with this trajectory
    dataset_collector.pair_with_trajectory(stats)
    
    return f"Evolution finished. Stats: {json.dumps(stats)}"

def analyze_latest_results() -> dict:
    """
    Analyzes the trajectory.jsonl from the latest run to get performance stats.

    Returns:
        dict: A dictionary containing performance statistics.
    """
    print("\n[Tool] Analyzing latest results...")
    global _last_evolution_instance
    if not _last_evolution_instance:
        # Fallback to searching for the file manually if the instance is lost
        output_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    else:
        output_base = _last_evolution_instance.paras.exp_output_path
    
    trajectory_file = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")
    
    stats = {
        "gen": 0, "best_fitness": float('inf'), "avg_dist": 0,
        "none_rate": 0, "last_error": "None", "last_traceback": "N/A",
        "best_code": ""
    }

    if _last_evolution_instance:
        problem = _last_evolution_instance.paras.problem
        stats.update({
            "last_error": getattr(problem, '_last_error', "None"),
            "last_traceback": getattr(problem, '_last_traceback', "N/A")
        })
    else:
        # If no active instance, create a temporary one to check current error state
        temp_prob = prob.Evaluation()
        stats.update({
            "last_error": getattr(temp_prob, '_last_error', "None"),
            "last_traceback": getattr(temp_prob, '_last_traceback', "N/A")
        })

    if os.path.exists(trajectory_file):
        with open(trajectory_file, "r", encoding='utf-8') as f:
            lines = f.readlines()
            if not lines: return stats

            entries = [json.loads(line) for line in lines]
            valid_entries = [e for e in entries if e.get('cost') is not None]
            
            stats["gen"] = len(entries)
            stats["none_rate"] = (len(entries) - len(valid_entries)) / len(entries)
            
            if valid_entries:
                best_entry = min(valid_entries, key=lambda e: e['cost'])
                stats["best_fitness"] = best_entry['cost']
                stats["avg_dist"] = np.mean([e['cost'] for e in valid_entries])
                stats["best_code"] = best_entry.get('code', '')
    
    return stats

def design_new_prm(problem_description: str, feedback_stats: dict) -> str:
    """
    Calls the Architect Agent to design a new Process Reward Model (PRM).

    Args:
        problem_description (str): High-level description of the problem (e.g., 'CVRP').
        feedback_stats (dict): Statistics from the last run to guide the agent. 
                               Expected keys: 'best_fitness', 'avg_dist', 'none_rate', 
                               'last_error', 'last_traceback', 'best_code'.
                               Example: {"best_fitness": 1200.5, "none_rate": 0.1, ...}

    Returns:
        str: A confirmation message.
    """
    print("\n[Tool] Designing new PRM...")
    agent = get_architect_agent()
    success = agent.design_prm(problem_description, feedback_stats)
    if success:
        return "New PRM designed and injected successfully into prob.py."
    else:
        return "Failed to design new PRM. Check agent logs."

def refine_best_code(best_code: str, objective: float, error_msg: str, traceback_msg: str) -> str:
    """
    Calls the Refine Agent to fix or improve the best code from the last run.

    Args:
        best_code (str): The code of the best individual.
        objective (float): The objective score of the best individual.
        error_msg (str): The error message if the code failed.
        traceback_msg (str): The traceback if the code failed.

    Returns:
        str: Path to the new refined seed file, or an error message.
    """
    print("\n[Tool] Refining best code...")
    if not best_code:
        return "Refinement failed: No code provided."

    agent = get_refine_agent()
    refined_code, summary = agent.refine_code(
        original_code=best_code,
        objective=objective,
        error_msg=error_msg,
        traceback_msg=traceback_msg
    )

    if refined_code:
        # --- Quality Check BEFORE Saving ---
        reviewer = get_reviewer_agent()
        review = reviewer.review_code(refined_code)
        if not review["is_pass"]:
            return f"Refinement rejected: The generated code failed review. Issues: {', '.join(review['issues'])}"

        refined_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")
        
        # Load existing seeds to avoid overwriting the entire library
        seeds = []
        if os.path.exists(refined_seed_path):
            try:
                with open(refined_seed_path, 'r', encoding='utf-8') as f:
                    seeds = json.load(f)
            except Exception:
                seeds = []
        
        new_seed = {
            "algorithm": f"React-Refined: {summary}",
            "code": refined_code
        }
        
        # Append and keep only the top N seeds to avoid bloat (optional, but good for focus)
        seeds.append(new_seed)
        if len(seeds) > 10:
            seeds = seeds[-10:] # Keep the last 10 refined/original seeds
            
        with open(refined_seed_path, 'w', encoding='utf-8') as f:
            json.dump(seeds, f, indent=4, ensure_ascii=False)
        return f"Code refined and added to {refined_seed_path}. Current library size: {len(seeds)}"
    else:
        return "Code refinement failed. Check agent logs."

def update_research_notes(content: str, section: str = "New Findings") -> str:
    """
    Updates the research_notes.md with new findings, observations, or failed attempts.
    This serves as the agent's long-term memory.

    Args:
        content (str): The new information to add to the notes.
        section (str): The section header under which to add the information.

    Returns:
        str: A confirmation message.
    """
    print(f"\n[Tool] Updating research notes under section '{section}'...")
    notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
    
    try:
        if not os.path.exists(notes_path):
            with open(notes_path, "w", encoding='utf-8') as f:
                f.write("# CVRP Research Notes\n\n")
        
        with open(notes_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find if section exists
        section_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == f"## {section}":
                section_idx = i
                break
        
        if section_idx != -1:
            # Insert after the header
            lines.insert(section_idx + 1, f"- {content}\n")
        else:
            # Append new section at the end
            if lines and not lines[-1].endswith("\n"):
                lines.append("\n")
            lines.append(f"\n## {section}\n")
            lines.append(f"- {content}\n")
        
        with open(notes_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
            
        return f"Successfully updated research notes in section '{section}'."
    except Exception as e:
        return f"Error updating research notes: {e}"

def update_memory(finding: str = None, failure: str = None, strategy: str = None) -> str:
    """
    Updates MEMORY.md with new key findings, failed attempts, or successful strategies.
    
    Args:
        finding (str, optional): A new key finding.
        failure (str, optional): A new failed attempt.
        strategy (str, optional): A new successful strategy.
    """
    print("\n[Tool] Updating MEMORY.md...")
    memory_path = os.path.join(os.path.dirname(__file__), "MEMORY.md")
    
    try:
        with open(memory_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        def insert_under_section(section_header, content):
            for i, line in enumerate(lines):
                if line.strip() == f"## {section_header}":
                    lines.insert(i + 1, f"- {content}\n")
                    return True
            return False

        if finding: insert_under_section("Key Findings", finding)
        if failure: insert_under_section("Failed Attempts", failure)
        if strategy: insert_under_section("Successful Strategies", strategy)
        
        with open(memory_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
        return "MEMORY.md updated successfully."
    except Exception as e:
        return f"Error updating MEMORY.md: {e}"

def update_plan(goal: str = None, task_completed: str = None, new_task: str = None) -> str:
    """
    Updates PLAN.md to reflect the current goal, completed tasks, and new tasks.
    
    Args:
        goal (str, optional): A short string summarizing the overall goal (e.g., 'Evolve a better CVRP heuristic').
        task_completed (str, optional): The name of a task that has been finished. 
                                        Matches existing lines in PLAN.md like '- [ ] task_name'.
        new_task (str, optional): A new sub-task description to add to the '## Current Sub-tasks' section.
                                  Example: 'Run 10 generations with new PRM'.
    """
    print("\n[Tool] Updating PLAN.md...")
    plan_path = os.path.join(os.path.dirname(__file__), "PLAN.md")
    
    try:
        with open(plan_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        if goal:
            for i, line in enumerate(lines):
                if line.strip() == "## Current Goal":
                    lines[i+1] = f"- {goal}\n"
                    break
        
        if task_completed:
            for i, line in enumerate(lines):
                if f"[ ] {task_completed}" in line:
                    lines[i] = line.replace("[ ]", "[x]")
                    break
        
        if new_task:
            for i, line in enumerate(lines):
                if line.strip() == "## Current Sub-tasks":
                    lines.insert(i + 1, f"- [ ] {new_task}\n")
                    break
                    
        with open(plan_path, "w", encoding='utf-8') as f:
            f.writelines(lines)
        return "PLAN.md updated successfully."
    except Exception as e:
        return f"Error updating PLAN.md: {e}"

def read_memory() -> str:
    """Reads the current MEMORY.md file."""
    path = os.path.join(os.path.dirname(__file__), "MEMORY.md")
    with open(path, "r", encoding='utf-8') as f:
        return f.read()

def read_plan() -> str:
    """Reads the current PLAN.md file."""
    path = os.path.join(os.path.dirname(__file__), "PLAN.md")
    with open(path, "r", encoding='utf-8') as f:
        return f.read()

import requests
import datetime
import subprocess

def update_handoff(content: str, from_agent: str, to_agent: str) -> str:
    """
    Updates the handoff.md with information for the next agent.
    
    Args:
        content (str): The information to pass.
        from_agent (str): The role of the agent sending the info.
        to_agent (str): The role of the agent receiving the info.
    """
    print(f"\n[Tool] Updating handoff from {from_agent} to {to_agent}...")
    handoff_path = os.path.join(os.path.dirname(__file__), "handoff.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"\n### 🔄 Handoff: {from_agent} -> {to_agent}\n"
    md_content += f"*Timestamp: {timestamp}*\n\n"
    md_content += f"{content}\n\n---\n"
    
    try:
        with open(handoff_path, "a", encoding="utf-8") as f:
            f.write(md_content)
        return f"Handoff updated successfully in {handoff_path}."
    except Exception as e:
        return f"Error updating handoff: {e}"

def read_handoff() -> str:
    """Reads the current handoff.md file."""
    path = os.path.join(os.path.dirname(__file__), "handoff.md")
    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            return f.read()
    return "No handoff information found."

def run_comprehensive_evaluation(instance_list: list = None) -> str:
    """
    Quality Control (QT) Tool: Evaluates the best code across multiple CVRP instances.
    
    Args:
        instance_list (list, optional): List of .vrp file names. If None, uses a default set.
    """
    print("\n[Tool] Running comprehensive evaluation (QT)...")
    stats = analyze_latest_results()
    best_code = stats.get("best_code")
    if not best_code:
        return "Evaluation failed: No best code found. Run evolution first."
        
    if instance_list is None:
        instance_list = ["A-n32-k5.vrp", "B-n31-k5.vrp", "P-n16-k8.vrp"]
        
    data_dir = os.path.join(os.path.dirname(__file__), "..", "v0_baseline", "data")
    report = "# 📊 Comprehensive Evaluation Report\n\n"
    report += f"**Base Best Fitness**: {stats.get('best_fitness', 'N/A')}\n\n"
    report += "| Instance | Cost | Status |\n| :--- | :--- | :--- |\n"
    
    results = []
    for inst_name in instance_list:
        file_path = os.path.join(data_dir, inst_name)
        if not os.path.exists(file_path):
            report += f"| {inst_name} | N/A | File not found |\n"
            continue
            
        try:
            eva = prob.Evaluation()
            instance = eva.read_vrplib_instance(file_path)
            
            local_vars = {}
            exec(best_code, globals(), local_vars)
            
            # Find the callable function (heuristic)
            alg_func = None
            for key, value in local_vars.items():
                if callable(value):
                    alg_func = value
                    break
            
            if not alg_func:
                report += f"| {inst_name} | N/A | No callable function |\n"
                continue
                
            giant_tour = alg_func(instance['coords'], instance['demands'], instance['dist_matrix'])
            routes = eva.optimal_split(giant_tour, instance['demands'], instance['dist_matrix'], instance['capacity'])
            cost = eva.calculate_total_distance(routes, instance['dist_matrix'])
            
            report += f"| {inst_name} | {cost:.2f} | Success |\n"
            results.append(cost)
        except Exception as e:
            report += f"| {inst_name} | N/A | Error: {str(e)[:20]}... |\n"
            
    if results:
        avg_cost = np.mean(results)
        report += f"\n**Average Cost Across Instances**: {avg_cost:.2f}\n"
        
    # Save report to research_notes.md
    update_research_notes(report, section="Evaluation Reports")
    return report

def web_search(query: str) -> str:
    """
    Searches the web for high-quality information about optimization algorithms, 
    papers, or code snippets using the Tavily Search API.
    The results are automatically saved to 'research_notes.md'.
    
    Use this tool when:
    - You need recent papers, blog posts, or code repositories about CVRP, 
      evolutionary algorithms, or related topics NOT covered in your research notes.
    - You encounter an error or performance plateau and need external ideas 
      to design new heuristics.
    - You want to implement a specific method (e.g., ALNS, LNS, tabu search) 
      but your notes don't have implementation details.
    
    Args:
        query (str): The search query (e.g., "ALNS for CVRP implementation", 
                     "state-of-the-art CVRP heuristics 2024").
    Returns:
        str: A summary of search results.
    """
    print(f"\n[Tool] Searching web for: '{query}'...")

    config = load_config()
    tavily_api_key = get_env_key("TAVILY_API_KEY", "tavily_api_key")
    if not tavily_api_key or tavily_api_key == "YOUR_TAVILY_API_KEY":
        tavily_api_key = config.get("tavily_api_key", "")

    if not tavily_api_key:
        return "Web search unavailable: No Tavily API key found. Please set TAVILY_API_KEY environment variable or configure in config.json."

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": 5
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if not results:
            return "No search results found."
        
        # Prepare Markdown content
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md_content = f"\n## 🔍 Research: {query}\n"
        md_content += f"*Timestamp: {timestamp}*\n\n"
        
        summary = "Search Results:\n"
        for i, res in enumerate(results):
            title = res.get('title', 'No Title')
            link = res.get('url', '#')
            content = res.get('content', 'No Content available.')
            
            # Add to Markdown file
            md_content += f"### {i+1}. [{title}]({link})\n"
            md_content += f"{content}\n\n"
            
            # Add to Agent's observation summary
            summary += f"{i+1}. {title}\n   URL: {link}\n   Snippet: {content[:300]}...\n\n"
        
        # Save to research_notes.md (Append mode)
        notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
        with open(notes_path, "a", encoding="utf-8") as f:
            f.write(md_content)
            f.write("\n---\n")
            
        return f"{summary}\n\nNote: Full search results have been saved to {notes_path} for future reference."
    except Exception as e:
        return f"Web search failed: {e}. Please check your API key or connection."

def fetch_paper_summary(paper_url: str) -> str:
    """
    Fetches and summarizes an academic paper URL.
    Use this after web_search returns interesting papers you want to explore deeper.
    
    Args:
        paper_url (str): URL to an arXiv paper (e.g., https://arxiv.org/abs/2103.00093).
    Returns:
        str: A summary of the paper's key ideas and methods.
    """
    print(f"\n[Tool] Fetching paper summary: {paper_url}...")
    
    import re
    import datetime
    
    arxiv_abs_match = re.match(r'https?://arxiv\.org/abs/(\d+\.\d+)', paper_url)
    arxiv_pdf_match = re.match(r'https?://arxiv\.org/pdf/(\d+\.\d+)', paper_url)
    
    if arxiv_abs_match or arxiv_pdf_match:
        arxiv_id = (arxiv_abs_match or arxiv_pdf_match).group(1)
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
            
            entry = root.find('atom:entry', ns)
            if entry is None:
                return "Failed to parse arXiv response."
            
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            authors = entry.findall('atom:author/atom:name', ns)
            published = entry.find('atom:published', ns)
            
            title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown"
            summary_text = summary.text.strip() if summary is not None else ""
            authors_text = ", ".join([a.text for a in authors]) if authors else "Unknown"
            published_text = published.text[:10] if published is not None else "Unknown"
            
            summary_short = summary_text[:800] + "..." if len(summary_text) > 800 else summary_text
            summary_short = summary_short.replace('\n', ' ')
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            md_content = f"\n## 📄 Paper: {title_text}\n"
            md_content += f"*Fetched: {timestamp}*\n\n"
            md_content += f"- **Authors**: {authors_text}\n"
            md_content += f"- **Published**: {published_text}\n"
            md_content += f"- **URL**: {paper_url}\n\n"
            md_content += f"### Abstract\n{summary_text}\n\n"
            
            notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
            with open(notes_path, "a", encoding="utf-8") as f:
                f.write(md_content)
                f.write("\n---\n")
            
            return f"""## Paper Summary

**Title**: {title_text}
**Authors**: {authors_text}
**Published**: {published_text}
**URL**: {paper_url}

### Abstract (truncated)
{summary_short}

Full paper info has been saved to research_notes.md for future reference."""
        except Exception as e:
            return f"Failed to fetch paper: {e}"
    
    return f"Unsupported paper URL format. Please provide an arXiv URL (e.g., https://arxiv.org/abs/2103.00093)."

def read_github_repo(repo_url: str) -> str:
    """
    Reads the README and key source files from a GitHub repository.
    Use this when web_search returns promising code implementations.
    
    Args:
        repo_url (str): URL to a GitHub repository (e.g., https://github.com/owner/repo).
    Returns:
        str: README content and key code snippets.
    """
    print(f"\n[Tool] Reading GitHub repo: {repo_url}...")
    
    import re
    import base64
    
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)/?', repo_url)
    if not match:
        return "Invalid GitHub repository URL. Use format: https://github.com/owner/repo"
    
    owner, repo = match.group(1), match.group(2).rstrip('/')
    repo = repo.split('?')[0].split('#')[0]
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    result = f"# GitHub Repository: {owner}/{repo}\n\n"
    
    try:
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        resp = requests.get(readme_url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            content = base64.b64decode(resp.json()['content']).decode('utf-8', errors='ignore')
            result += f"## README\n{content[:4000]}\n\n"
        else:
            result += "## README\n(No README found)\n\n"
        
        contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        resp = requests.get(contents_url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            items = resp.json()
            py_files = [f for f in items if f['type'] == 'file' and f['name'].endswith('.py')]
            
            for f in py_files[:3]:
                file_resp = requests.get(f['url'], headers=headers, timeout=30)
                if file_resp.status_code == 200:
                    content = base64.b64decode(file_resp.json()['content']).decode('utf-8', errors='ignore')
                    result += f"## {f['name']}\n```python\n{content[:2000]}\n```\n\n"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md_content = f"\n## 💻 Code: {owner}/{repo}\n"
        md_content += f"*Fetched: {timestamp}*\n"
        md_content += f"- **URL**: {repo_url}\n\n"
        md_content += result.replace("#", "##")
        
        notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
        with open(notes_path, "a", encoding="utf-8") as f:
            f.write(md_content)
            f.write("\n---\n")
        
        return result + f"\nFull repository info has been saved to research_notes.md for future reference."
        
    except Exception as e:
        return f"Failed to read GitHub repository: {e}"

def read_research_notes() -> str:
    """
    Reads the content of research_notes.md to recall information from previous web searches.

    Returns:
        str: The content of the research notes or an error message.
    """
    print("\n[Tool] Reading research notes...")
    notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
    if os.path.exists(notes_path):
        with open(notes_path, "r", encoding="utf-8") as f:
            # Return the last 2000 characters to avoid context overflow if it's too long
            content = f.read()
            if len(content) > 3000:
                return f"... [Truncated] ...\n{content[-3000:]}"
            return content
    return "No research notes found yet. Use 'web_search' first."

def add_new_seed(algorithm_name: str, code: str) -> str:
    """
    Manually adds a new algorithm to the refined_seeds.json seed library.
    Use this when you find a good implementation from 'web_search' or 'read_github_repo'.

    Args:
        algorithm_name (str): A descriptive name for the algorithm.
        code (str): The FULL Python code including 'import numpy as np' and 
                    'def generate_giant_tour(coords, demands, dist_matrix):' definition.
    """
    print(f"\n[Tool] Adding new seed: {algorithm_name}...")
    
    # --- Quality Check BEFORE Saving ---
    reviewer = get_reviewer_agent()
    review = reviewer.review_code(code)
    if not review["is_pass"]:
        return f"Seed rejected: The provided code failed review. Issues: {', '.join(review['issues'])}. Make sure you include the FULL function definition and necessary imports."

    refined_seed_path = os.path.join(os.path.dirname(__file__), "refined_seeds.json")
    
    seeds = []
    if os.path.exists(refined_seed_path):
        try:
            with open(refined_seed_path, 'r', encoding='utf-8') as f:
                seeds = json.load(f)
        except Exception:
            seeds = []
    
    new_seed = {
        "algorithm": algorithm_name,
        "code": code
    }
    
    seeds.append(new_seed)
    if len(seeds) > 10:
        seeds = seeds[-10:]
        
    with open(refined_seed_path, 'w', encoding='utf-8') as f:
        json.dump(seeds, f, indent=4, ensure_ascii=False)
    
    return f"Algorithm '{algorithm_name}' added to {refined_seed_path}. Current library size: {len(seeds)}"

def run_deep_analysis() -> str:
    """
    Calls the Analyst Agent to perform a deep analysis of the latest evolution trajectory.
    Use this when you are unsure why performance is plateauing or when none_rate is high.
    """
    print("\n[Tool] Running deep analysis...")
    
    # 1. Load trajectory
    output_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    trajectory_file = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")
    
    if not os.path.exists(trajectory_file):
        return "Analysis failed: No trajectory.jsonl found. Run evolution first."

    trajectory_data = []
    with open(trajectory_file, "r", encoding='utf-8') as f:
        for line in f:
            trajectory_data.append(json.loads(line))

    # 2. Extract current PRM from prob.py
    prob_path = os.path.join(output_base, "prob.py")
    current_prm = ""
    try:
        with open(prob_path, 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            match = re.search(r'# \[INJECTED BY AGENT\]\n\s*(.*?)\n\s*# Composite Fitness', content, re.DOTALL)
            if match:
                current_prm = match.group(1).strip()
    except Exception:
        current_prm = "Unknown (Error reading prob.py)"

    # 3. Call Analyst Agent
    agent = get_analyst_agent()
    analysis_report = agent.analyze_trajectory(trajectory_data, current_prm)
    
    # Save to research notes
    update_research_notes(analysis_report, section="Deep Analysis Reports")
    
    return analysis_report

def run_code_review(code: str = None) -> str:
    """
    Calls the Reviewer Agent to check code for syntax errors, infinite loops, and CVRP spec compliance.
    Use this BEFORE adding a new seed or after refining code to ensure it's safe to run.
    
    Args:
        code (str, optional): The Python code to review. If None, reviews the best code from the latest run.
    """
    print("\n[Tool] Running code review...")
    
    if code is None:
        print("No code provided, fetching the best code from latest results...")
        stats = analyze_latest_results()
        code = stats.get("best_code")
        if not code:
            return "Code review failed: No code provided and no best code found in latest results."

    reviewer = get_reviewer_agent()
    review_results = reviewer.review_code(code)
    
    status = "PASS" if review_results["is_pass"] else "FAIL"
    report = f"### 🛡️ Code Review Report: {status}\n"
    
    if review_results["issues"]:
        report += "\n**Issues Found:**\n"
        for issue in review_results["issues"]:
            report += f"- {issue}\n"
            
    if review_results["suggestions"]:
        report += "\n**Suggestions:**\n"
        for sug in review_results["suggestions"]:
            report += f"- {sug}\n"
            
    if review_results["is_pass"]:
        report += "\nCode passed all static and mock execution checks."
        
    return report

def organize_research_notes() -> str:
    """
    Calls the Librarian Agent to structure and clean up the research_notes.md file.
    Use this periodically to keep your research organized.
    """
    print("\n[Tool] Organizing research notes...")
    notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
    
    if not os.path.exists(notes_path):
        return "No research notes found to organize."
        
    with open(notes_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    librarian = get_librarian_agent()
    structured_content = librarian.organize_notes(content)
    
    if "Librarian Agent error" in structured_content:
        return structured_content
        
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(structured_content)
        
    return "Research notes have been structured and cleaned up successfully."

def generate_visual_report() -> str:
    """
    Calls the Visualizer Agent to generate convergence curves and path maps.
    Then embeds these images into the research_notes.md file.
    """
    print("\n[Tool] Generating visual report...")
    output_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    trajectory_file = os.path.join(output_base, "results", "trajectory", "trajectory.jsonl")
    notes_path = os.path.join(os.path.dirname(__file__), "research_notes.md")
    
    viz = get_visualizer_agent()
    
    # 1. Convergence Curve
    conv_path = viz.generate_convergence_curve(trajectory_file)
    
    # 2. Path Map (using existing tool logic or helper)
    # We can also call visualize_best_solution internally
    best_viz_msg = visualize_best_solution()
    
    # Extract path from message
    import re
    path_match = re.search(r'generated at: (.*)\nCost', best_viz_msg)
    
    images_to_embed = []
    if os.path.exists(conv_path): images_to_embed.append(conv_path)
    if path_match: images_to_embed.append(path_match.group(1).strip())
    
    if images_to_embed:
        msg = viz.embed_visuals_to_notes(images_to_embed, notes_path)
        return f"Visual report generated. {msg}"
    return "Failed to generate visual report: No images created."

def deploy_best_algorithm() -> str:
    """
    Calls the Deployer Agent to package the best algorithm into a standalone module.
    Performs stress tests and generates interface documentation.
    """
    print("\n[Tool] Deploying best algorithm...")
    stats = analyze_latest_results()
    best_code = stats.get("best_code")
    if not best_code:
        return "Deployment failed: No best code found. Run evolution first."
        
    deployer = get_deployer_agent()
    
    # 1. Package
    module_path = deployer.package_algorithm(best_code)
    
    # 2. Stress Test
    test_result = deployer.run_stress_test(module_path)
    
    return f"Algorithm deployed successfully: {module_path}\n{test_result}"

def install_missing_package(package_name: str) -> str:
    """
    Attempts to install a missing Python package using pip.
    Use this when you encounter 'ModuleNotFoundError' for a required package.

    Args:
        package_name (str): The name of the package to install (e.g., "matplotlib", "scipy").

    Returns:
        str: Confirmation or error message about the installation.
    """
    print(f"\n[Tool] Attempting to install missing package: {package_name}...")
    import subprocess
    import sys

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return f"Successfully installed {package_name}. You can now retry the previous action."
        else:
            return f"Failed to install {package_name}. Error: {result.stderr[-500:]}"
    except Exception as e:
        return f"Installation failed: {e}"

def visualize_best_solution(instance_name: str = "P-n22-k8.vrp") -> str:
    """
    Runs the best generated code on a specific CVRP instance and creates a visual plot.

    Args:
        instance_name (str): The name of the .vrp instance to visualize.

    Returns:
        str: Confirmation message with the path to the generated image.
    """
    print(f"\n[Tool] Visualizing best solution on {instance_name}...")
    
    stats = analyze_latest_results()
    best_code = stats.get("best_code")
    if not best_code:
        return "No best code found to visualize. Run evolution first."

    # Use prob module for reading instances and evaluating
    data_dir = os.path.join(os.path.dirname(__file__), "..", "v0_baseline", "data")
    file_path = os.path.join(data_dir, instance_name)
    
    if not os.path.exists(file_path):
        return f"Instance {instance_name} not found in {data_dir}"

    try:
        eva = prob.Evaluation()
        instance = eva.read_vrplib_instance(file_path)
        
        local_vars = {}
        exec(best_code, globals(), local_vars)
        
        func_name = None
        for key, value in local_vars.items():
            if callable(value):
                func_name = key
                break
        
        if not func_name:
            return "Failed to find a callable function in the best code."

        alg_func = local_vars[func_name]
        giant_tour = alg_func(instance['coords'], instance['demands'], instance['dist_matrix'])
        
        eva = prob.Evaluation()
        routes = eva.optimal_split(giant_tour, instance['demands'], instance['dist_matrix'], instance['capacity'])
        cost = eva.calculate_total_distance(routes, instance['dist_matrix'])
        
        try:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            import visualize_results
            visualize_results.plot_cvrp_solution(instance_name, instance['coords'], routes, cost, title_suffix="Agent_Optimized")
            save_path = os.path.join(os.path.dirname(__file__), "..", "visualizations", f"{instance_name}_Agent_Optimized.png")
            return f"Visualization generated at: {save_path}\nCost: {cost:.2f}"
        except ImportError:
            return f"No visualization library available. Computed cost: {cost:.2f}"
    except Exception as e:
        return f"Visualization failed: {e}"
