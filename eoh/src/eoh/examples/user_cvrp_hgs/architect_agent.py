import os
import json
import requests
import re
import time
import random

# For data collection (Post-training)
from v2_agent.dataset_collector import collector as dataset_collector

class ArchitectAgent:
    """
    Architect Agent for EoH.
    This agent takes a high-level problem description and automatically designs 
    the Process Reward Model (PRM) by injecting code into prob.py.
    """
    def __init__(self, api_key, endpoint="api.moonshot.cn", model="moonshot-v1-8k"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.prob_file = os.path.join(os.path.dirname(__file__), "prob.py")

    def design_prm(self, problem_description, feedback_stats=None):
        print(f"Architect Agent: Designing/Adjusting PRM for '{problem_description}'...")
        
        feedback_context = ""
        if feedback_stats:
            none_info = f"- None/Failed Rate: {feedback_stats.get('none_rate', 'N/A')}\n- Last Error: {feedback_stats.get('last_error', 'None')}\n- Last Traceback: {feedback_stats.get('last_traceback', 'N/A')}"
            feedback_context = f"""
Current Evolution Feedback (Generation {feedback_stats.get('gen', 'N/A')}):
- Best Total Fitness: {feedback_stats.get('best_fitness', 'N/A')}
- Average Distance: {feedback_stats.get('avg_dist', 'N/A')}
{none_info}
- Observation: {feedback_stats.get('observation', 'N/A')}

IMPORTANT: 
1. If 'None/Failed Rate' is high, simplify the PRM code to avoid runtime errors (like index out of bounds or type errors).
2. If 'Last Error' indicates a PRM error, FIX the mathematical logic in your next design.
3. Ensure the code is robust against different tour lengths or empty arrays.
"""

        # 1. Prompt the LLM to design the PRM code
        prompt = f"""
You are an Algorithm Architect. Your goal is to design a Process Reward Model (PRM) for an evolutionary heuristic framework (EoH).
The problem is: {problem_description}

{feedback_context}

Current context:
In CVRP, we are evolving a 'Giant Tour' (a permutation of customers). 
We need to design a 'process_reward' (penalty) that guides the LLM to write better heuristics.

Available variables in the injection point:
- 'tour': The permutation of customer indices (1 to N).
- 'routes': The list of sub-routes after optimal split.
- 'instance': A dictionary containing 'coords', 'demands', 'dist_matrix', 'capacity'.
- 'dist': The final total distance (outcome).
- 'np': numpy is available.

Your Task:
Write a Python code snippet that calculates a variable named 'process_reward'. 
CRITICAL CONSTRAINTS:
1. This must be a raw code snippet, NOT a function definition.
2. DO NOT include any 'import' statements (numpy is already available as 'np').
3. DO NOT use 'return' statements.
3. The final value must be assigned to the variable 'process_reward'.
4. This value will be ADDED to the distance (lower is better, so 'process_reward' should be a penalty).
5. Use mathematical properties like Polar Angles, Locality, or Load Balance.

Return ONLY the Python code snippet. No explanation. No markdown code blocks.
Example:
relative_coords = instance['coords'][tour] - instance['coords'][0]
angles = np.arctan2(relative_coords[:, 1], relative_coords[:, 0])
process_reward = np.sum(np.abs(np.diff(angles))) * 10
"""

        # Call LLM (using Kimi/Moonshot API)
        url = f"https://{self.endpoint}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                res = requests.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if 'choices' in data:
                        content = data['choices'][0]['message']['content']
                        # Clean code block if LLM returns it
                        code_snippet = re.sub(r'```python|```', '', content).strip()
                        
                        # 2. Log for post-training dataset
                        dataset_collector.log_prm_design(
                            prm_code=code_snippet, 
                            reasoning=content, # Full reasoning (includes code)
                            problem_desc=problem_description
                        )
                        
                        # 3. Inject into prob.py
                        self._inject_into_prob(code_snippet)
                        return True
                    else:
                        print(f"Unexpected API Response format: {data}")
                        return False
                
                elif res.status_code in [429, 503]:
                    wait_time = (2 ** attempt) + 5 + random.uniform(0, 5)
                    print(f"API Overloaded or Rate Limited (Status {res.status_code}). Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API Error: Status {res.status_code}")
                    print(f"Response: {res.text}")
                    return False
                    
            except Exception as e:
                print(f"Architect Agent attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(2)
        
        return False

    def _inject_into_prob(self, code_snippet):
        with open(self.prob_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        in_placeholder = False
        for line in lines:
            if "--- Process Reward (PRM) Placeholder ---" in line:
                new_lines.append(line)
                new_lines.append("                    # [INJECTED BY AGENT]\n")
                # Indent the code snippet to match the loop
                indented_code = "\n".join(["                    " + l for l in code_snippet.split("\n")])
                new_lines.append(indented_code + "\n")
                in_placeholder = True
            elif "process_reward = 0" in line and in_placeholder:
                # Skip the old 0 assignment
                continue
            elif "# Composite Fitness" in line and in_placeholder:
                in_placeholder = False # End of injection area
                new_lines.append(line)
            elif not in_placeholder:
                new_lines.append(line)
        
        with open(self.prob_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("Architect Agent: Successfully injected designed PRM into prob.py")

if __name__ == "__main__":
    # Example usage with Kimi API:
    agent = ArchitectAgent(api_key="sk-YVrnwoeeoJezfY31vOZyWEAuutcDE0A5X9rzYcn8bcW8L1ch")
    agent.design_prm("CVRP where sweep-like polar sorting and load balance are mathematically critical.")
