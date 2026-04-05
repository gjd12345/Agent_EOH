"""
Autonomous EoH Agent using ReAct (Reasoning-Acting) Framework.
"""
import os
import sys
import json
import requests
from typing import Dict, Any

# Add paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import react_tools

class AutonomousEoHAgent:
    def __init__(self, api_key, api_endpoint="https://api.deepseek.com", model="deepseek-chat", name="Agent"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.name = name
        self.tools = {
            "run_evolution": react_tools.run_evolution,
            "analyze_latest_results": react_tools.analyze_latest_results,
            "run_deep_analysis": react_tools.run_deep_analysis,
            "design_new_prm": react_tools.design_new_prm,
            "refine_best_code": react_tools.refine_best_code,
            "update_research_notes": react_tools.update_research_notes,
            "update_memory": react_tools.update_memory,
            "update_plan": react_tools.update_plan,
            "read_memory": react_tools.read_memory,
            "read_plan": react_tools.read_plan,
            "web_search": react_tools.web_search,
            "fetch_paper_summary": react_tools.fetch_paper_summary,
            "read_github_repo": react_tools.read_github_repo,
            "read_research_notes": react_tools.read_research_notes,
            "visualize_best_solution": react_tools.visualize_best_solution,
            "generate_visual_report": react_tools.generate_visual_report,
            "deploy_best_algorithm": react_tools.deploy_best_algorithm,
            "run_comprehensive_evaluation": react_tools.run_comprehensive_evaluation,
            "run_code_review": react_tools.run_code_review,
            "organize_research_notes": react_tools.organize_research_notes,
            "update_handoff": react_tools.update_handoff,
            "read_handoff": react_tools.read_handoff,
            "add_new_seed": react_tools.add_new_seed,
            "install_missing_package": react_tools.install_missing_package,
            "finish": lambda: "Task finished."
        }

    def _get_tool_descriptions(self):
        return "\n".join([f"- {name}: {func.__doc__.strip() if func.__doc__ else 'No description available.'}" for name, func in self.tools.items()])

    def _get_skills_from_file(self):
        skills_path = os.path.join(os.path.dirname(__file__), "SKILLS.md")
        if os.path.exists(skills_path):
            with open(skills_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Tool Descriptions:\n" + self._get_tool_descriptions()

    def run(self, high_level_goal: str, max_loops=10):
        print(f"=== Starting Autonomous Agent ({self.name}) with Goal: '{high_level_goal}' ===")
        
        system_prompt = f"""
You are an Autonomous AI Research Scientist specializing in Evolutionary Heuristics (EoH).
Your primary mission is: {high_level_goal}

### 🧠 Autonomous Goal Setting & Strategy
- **Self-Discovery**: If your goal is broad (e.g., "improve performance"), your FIRST priority should be to use `read_research_notes` to see if information already exists. If not, use `web_search` to find the State-of-the-Art (SOTA) results and known lower bounds for the CVRP instances you are working on (e.g., A-n32-k5, B-n31-k5).
- **Strategic Analysis**: If the evolution process is stuck (no improvement for many generations) or the `none_rate` is high, call `run_deep_analysis`. This agent acts as your Senior Analyst to diagnose if the PRM is too restrictive or if the algorithm has converged prematurely.
- **Visual Evidence**: After a successful evolution run, use `generate_visual_report` to create convergence curves and path maps. This helps you "see" the progress and document it.
- **Quality Control**: Before using `add_new_seed` or after `refine_best_code`, you MUST call `run_code_review` to ensure the code is logically sound and doesn't contain infinite loops.
- **Final Deployment**: Once you have achieved your target fitness and verified the results, use `deploy_best_algorithm` to package the final research outcome into a production-ready module.
- **Dynamic Refinement**: Once you find SOTA results or lower bounds, update your `PLAN.md` with specific, quantitative targets (e.g., "Aim for Fitness < 1200 based on SOTA findings"). Distinguish between "Best Known Solution (BKS)" which is an achievable target, and "Theoretical Lower Bound" which is the absolute minimum possible.
- **Knowledge Extraction**: If you find a promising algorithm implementation during `web_search` or `read_github_repo`, your NEXT step should be to use `add_new_seed` to save it into the seed library. 
  - **CRITICAL**: The `code` argument for `add_new_seed` MUST be a complete Python string including `import numpy as np` and the full `def generate_giant_tour(coords, demands, dist_matrix):` definition. Do NOT provide just the logic inside the function.
- **Error Awareness**: If you observe a high `none_rate` (many `None` objectives), your IMMEDIATE priority is to use `analyze_latest_results` to get the `last_error` and `last_traceback`, then use `refine_best_code` to fix the underlying issue. Do NOT ignore `None` values; they indicate broken code logic or invalid tour generation.
- **Adaptive Research**: Don't just run evolution blindly. ALWAYS check `read_research_notes` first to reuse existing knowledge and avoid redundant searches. Search for existing algorithms (e.g., Clarke-Wright, Sweep, ALNS, HGS) and their PRM-like logic to use as inspiration for your `design_new_prm` action.

### 🔄 ReAct Framework (Thought -> Action -> Observation)
1.  **Thought**: Reason about the current situation. 
    - **Analyze**: Check your current best fitness vs. the SOTA you discovered.
    - **Strategy**: Decide if you need more knowledge (`web_search`), a better architecture (`design_new_prm`), or more evolution (`run_evolution`).
    - **State Management**: Always read `PLAN.md` and `MEMORY.md` first. Update them after every significant finding or failure.
2.  **Action**: Choose ONE tool.
3.  **Observation**: Analyze the tool's output.

Available Skills & Tools:
{self._get_skills_from_file()}

Your response MUST be in this EXACT JSON format:
{{
    "thought": "Your reasoning. Include findings from web_search or evolution here. If you found SOTA, state it clearly.",
    "action": {{
        "tool_name": "name_of_the_tool_to_use",
        "args": {{ "arg1": "value1", "arg2": "value2" }}
    }}
}}
"""
        
        history = []
        for i in range(max_loops):
            print(f"\n--- Loop {i+1}/{max_loops} ---")
            
            # 1. Construct prompt for LLM
            prompt = system_prompt
            if history:
                prompt += "\n\n--- History ---\n" + "\n".join(history)
            
            # 2. Get Thought and Action from LLM
            llm_response = self._call_llm(prompt)
            if not llm_response:
                print("Agent Error: Failed to get a valid response from LLM.")
                break

            thought = llm_response.get("thought")
            action = llm_response.get("action")
            
            if not thought or not action:
                print(f"Agent Error: Invalid format from LLM: {llm_response}")
                history.append(f"Observation: Your last response was not in the correct JSON format. Please correct it.")
                continue

            print(f"🤖 Thought: {thought}")
            history.append(f"Thought: {thought}")
            
            tool_name = action.get("tool_name")
            args = action.get("args", {})
            print(f"🛠️ Action: Calling tool '{tool_name}' with args: {args}")
            history.append(f"Action: {json.dumps(action)}")

            # 3. Execute Action
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**args)
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"
                
                print(f"👀 Observation: {result}")
                history.append(f"Observation: {result}")

                if tool_name == 'finish':
                    print("\n=== Agent has finished the task. ===")
                    break
            else:
                print(f"Agent Error: Tool '{tool_name}' not found.")
                history.append(f"Observation: The tool '{tool_name}' does not exist. Please choose from the available tools.")

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "response_format": { "type": "json_object" } # Enforce JSON output
        }

        endpoint = self.api_endpoint
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        
        try:
            response = requests.post(f"{endpoint}/v1/chat/completions", json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            # The response content is a JSON string, so we need to parse it.
            response_str = response.json()["choices"][0]["message"]["content"]
            return json.loads(response_str)
        except requests.RequestException as e:
            print(f"LLM API call failed: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Failed to parse LLM response: {e}")
            return None

if __name__ == "__main__":
    import os
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY") or config.get("deepseek_api_key", "")

    if not deepseek_api_key or deepseek_api_key == "YOUR_DEEPSEEK_API_KEY":
        print("Warning: No DeepSeek API key found. Please set DEEPSEEK_API_KEY environment variable or configure in config.json")

    agent = AutonomousEoHAgent(api_key=deepseek_api_key)

    goal = "Research SOTA results for CVRP instances (A-n32-k5, B-n31-k5) using web_search, then set a quantitative target and evolve a heuristic to achieve it."

    agent.run(high_level_goal=goal, max_loops=15)
