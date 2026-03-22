import json
import os
import requests
import numpy as np

class AnalystAgent:
    """
    Analyst Agent for EoH.
    This agent analyzes the evolution trajectory, population diversity, 
    and performance bottlenecks to provide strategic advice to the Master Agent.
    """
    def __init__(self, api_key, endpoint="https://api.deepseek.com", model="deepseek-chat"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model

    def analyze_trajectory(self, trajectory_data: list, current_prm: str = None) -> str:
        """
        Analyzes the trajectory of the evolutionary process.
        """
        if not trajectory_data:
            return "No trajectory data available for analysis."

        # Basic stats for context
        best_fitness = min([e['cost'] for e in trajectory_data if e.get('cost') is not None], default=float('inf'))
        none_count = sum(1 for e in trajectory_data if e.get('cost') is None)
        total_count = len(trajectory_data)
        none_rate = none_count / total_count if total_count > 0 else 0

        # Extract last few entries to see trends
        recent_entries = trajectory_data[-10:]
        recent_fitness = [e['cost'] for e in recent_entries if e.get('cost') is not None]
        
        prompt = f"""
You are a Senior Algorithm Analyst. Your goal is to analyze the performance of an Evolutionary Heuristics (EoH) process for CVRP.

### 📊 Current Stats
- **Total Generations/Individuals**: {total_count}
- **Global Best Fitness**: {best_fitness}
- **None/Failure Rate**: {none_rate:.2%}(indicating code crashes or constraint violations)
- **Current PRM (Process Reward Model)**: 
```python
{current_prm if current_prm else "Standard (Distance only)"}
```

### 📉 Recent Trend (Last 10 individuals)
Fitness values: {recent_fitness}

### 🎯 Your Task
Provide a deep analysis and strategic advice. Answer the following:
1. **Convergence Analysis**: Is the algorithm converging? Is it stuck in a local optimum?
2. **Diversity & Exploration**: Is the algorithm exploring new areas or just making minor tweaks?
3. **PRM Effectiveness**: Is the current PRM guiding the evolution effectively? Or is it too restrictive/too loose?
4. **Actionable Recommendations**: Should we:
   - Continue evolution?
   - Redesign the PRM (Architect Agent)?
   - Refine the best code (Refine Agent)?
   - Search for new inspiration (Web Search)?
   - Change population size or generations?

Keep your response concise and focused on ACTIONABLE insights.
"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            response = requests.post(f"{self.endpoint}/v1/chat/completions", json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Analyst Agent error: {e}"

if __name__ == "__main__":
    # Test
    analyst = AnalystAgent(api_key="YOUR_KEY")
    print(analyst.analyze_trajectory([{"cost": 1000}, {"cost": 950}, {"cost": 950}], "process_reward = 0"))
