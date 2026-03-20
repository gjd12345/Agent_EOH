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
    def __init__(self, api_key, api_endpoint="https://api.deepseek.com", model="deepseek-chat"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.tools = {
            "run_evolution": react_tools.run_evolution,
            "analyze_latest_results": react_tools.analyze_latest_results,
            "design_new_prm": react_tools.design_new_prm,
            "refine_best_code": react_tools.refine_best_code,
            "web_search": react_tools.web_search,
            "fetch_paper_summary": react_tools.fetch_paper_summary,
            "read_github_repo": react_tools.read_github_repo,
            "read_research_notes": react_tools.read_research_notes,
            "visualize_best_solution": react_tools.visualize_best_solution,
            "install_missing_package": react_tools.install_missing_package,
            "finish": lambda: "Task finished."
        }

    def _get_tool_descriptions(self):
        return "\n".join([f"- {name}: {func.__doc__.strip() if func.__doc__ else 'No description available.'}" for name, func in self.tools.items()])

    def run(self, high_level_goal: str, max_loops=10):
        print(f"=== Starting Autonomous Agent with Goal: '{high_level_goal}' ===")
        
        system_prompt = f"""
You are an Autonomous AI Research Scientist specializing in Evolutionary Heuristics (EoH).
Your main goal is: {high_level_goal}

You operate in a loop of Thought, Action, and Observation (ReAct framework).
1.  **Thought**: You reason about the current situation and decide on the best next action. 
    - IMPORTANT: You have TWO types of knowledge sources:
      a) research_notes.md - Contains FOUNDATIONAL knowledge only. For RECENT developments,
         specific implementations, or ideas NOT in notes, use web_search.
      b) web_search - Retrieves papers, blog posts, and code from the internet.
    - If you need recent papers or code implementations, use web_search first.
    - After web_search, use fetch_paper_summary to dive deeper into interesting papers,
      or read_github_repo to examine code implementations.
    - IMPORTANT: If your current strategy is stagnating (no improvement after 2+ iterations),
      search for new ideas rather than repeating similar approaches.
2.  **Action**: You choose ONE tool to execute from the available list.
3.  **Observation**: You analyze the result from the tool and use it for your next thought.

Available Tools:
{self._get_tool_descriptions()}

Your response MUST be in this EXACT JSON format:
{{
    "thought": "Your reasoning and plan for the next action. If you decide to search, specify what query you will use.",
    "action": {{
        "tool_name": "name_of_the_tool_to_use",
        "args": {{ "arg1": "value1", "arg2": "value2" }}
    }}
}}

Let's begin.
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

        try:
            response = requests.post(f"{self.api_endpoint}/v1/chat/completions", json=payload, headers=headers, timeout=120)
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

    goal = "Find a CVRP heuristic that achieves a fitness score below 1800 while maintaining a zero 'None' failure rate."

    agent.run(high_level_goal=goal, max_loops=10)
