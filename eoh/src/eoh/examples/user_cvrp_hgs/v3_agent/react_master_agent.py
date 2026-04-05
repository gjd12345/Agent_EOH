import os
import sys
import json
import requests
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
example_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if example_root not in sys.path:
    sys.path.insert(0, example_root)

import react_tools


class AutonomousEoHAgent:
    def __init__(self, api_key, api_endpoint="https://api.deepseek.com", model="deepseek-chat", name="Agent"):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.model = model
        self.name = name
        self.tools = {
            "sync_state": react_tools.sync_state,
            "read_tasks": react_tools.read_tasks,
            "set_active_task": react_tools.set_active_task,
            "update_task_status": react_tools.update_task_status,
            "read_session_context": react_tools.read_session_context,
            "append_project_truth_fact": react_tools.append_project_truth_fact,
            "append_project_truth_paper": react_tools.append_project_truth_paper,
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

    def _truncate_text(self, text: str, max_chars: int) -> str:
        if text is None:
            return ""
        text = str(text)
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} chars]"

    def _append_trace(self, content: str) -> None:
        try:
            trace_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(trace_dir, exist_ok=True)
            trace_path = os.path.join(trace_dir, "agent_trace.md")
            with open(trace_path, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            return

    def _compact_history(self, history: list, max_chars: int) -> list:
        if not history:
            return []
        joined = "\n".join(history)
        if len(joined) <= max_chars:
            return history
        keep_tail = []
        cur = 0
        for item in reversed(history):
            item_len = len(item) + 1
            if cur+item_len > max_chars:
                break
            keep_tail.append(item)
            cur += item_len
        keep_tail = list(reversed(keep_tail))
        dropped = len(history) - len(keep_tail)
        header = f"History was compacted; dropped {dropped} earlier entries. Rely on state files (tasks.json, project_truth.md, session_context.md, ledgers) for full context."
        return [header] + keep_tail

    def run(self, high_level_goal: str, max_loops=10):
        react_tools.sync_state()
        print(f"=== Starting Autonomous Agent ({self.name}) with Goal: '{high_level_goal}' ===")

        history = []
        history_budget_chars = 6000
        observation_budget_chars = 1500
        for i in range(max_loops):
            print(f"\n--- Loop {i+1}/{max_loops} ---")
            try:
                session_context = react_tools.read_session_context()
            except Exception:
                session_context = ""
            skills = self._get_skills_from_file()

            prompt = f"""
You are an Autonomous AI Research Scientist specializing in Evolutionary Heuristics (EoH) for CVRP.
Your primary mission is: {high_level_goal}

### Session Context (Read First)
{session_context}

### Context Control Rules (Strict)
- Do NOT rely on chat history for long-term memory. Use state files via tools.
- Keep args minimal; prefer task_id/run_id references over pasting big blobs.
- For large outputs, store summaries to project_truth/research_notes instead of re-printing.

### Operating Rules
- Always keep state consistent: use sync_state if files are missing or out of date.
- Use read_tasks to understand currentStage and activeTaskId, then set_active_task explicitly before major actions.
- After any significant action, append_project_truth_fact (engineering facts) and append_project_truth_paper (paper narrative) when applicable.
- Before using add_new_seed or after refine_best_code, run run_code_review.

### ReAct Framework (Thought -> Action -> Observation)
1. Thought: reason about the current state and choose the next single action.
2. Action: choose ONE tool.
3. Observation: analyze the tool's output.

Available Skills & Tools:
{skills}

Output must be valid JSON (double quotes, no trailing commas, no comments), EXACT format:
{{
  "thought": "string",
  "action": {{
    "tool_name": "string",
    "args": {{}}
  }}
}}
"""
            if history:
                compacted = self._compact_history(history, history_budget_chars)
                prompt += "\n\n--- Recent History (Compacted) ---\n" + "\n".join(compacted)

            llm_response = self._call_llm(prompt)
            if not llm_response:
                print("Agent Error: Failed to get a valid response from LLM.")
                break

            thought = llm_response.get("thought")
            action = llm_response.get("action")

            if not thought or not action:
                print(f"Agent Error: Invalid format from LLM: {llm_response}")
                history.append("Observation: Your last response was not in the correct JSON format. Please correct it.")
                continue

            print(f"🤖 Thought: {thought}")
            history.append(f"Thought: {thought}")

            tool_name = action.get("tool_name")
            args = action.get("args", {})
            print(f"🛠️ Action: Calling tool '{tool_name}' with args: {args}")
            history.append(f"Action: {json.dumps(action, ensure_ascii=False)}")

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**args)
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"

                print(f"👀 Observation: {result}")
                obs_short = self._truncate_text(result, observation_budget_chars)
                history.append(f"Observation: {obs_short}")
                self._append_trace(
                    f"\n## Loop {i+1}\n\n"
                    f"### Thought\n{thought}\n\n"
                    f"### Action\n{json.dumps(action, ensure_ascii=False)}\n\n"
                    f"### Observation (truncated)\n{obs_short}\n"
                )

                if tool_name == "finish":
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
            "response_format": {"type": "json_object"}
        }

        endpoint = self.api_endpoint
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"

        try:
            response = requests.post(f"{endpoint}/v1/chat/completions", json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            response_str = response.json()["choices"][0]["message"]["content"]
            return json.loads(response_str)
        except requests.RequestException as e:
            print(f"LLM API call failed: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Failed to parse LLM response: {e}")
            return None


if __name__ == "__main__":
    v3_config_path = os.path.join(os.path.dirname(__file__), "config.json")
    v2_config_fallback_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v2_agent", "config.json"))

    config = {}
    if os.path.exists(v3_config_path):
        with open(v3_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    elif os.path.exists(v2_config_fallback_path):
        with open(v2_config_fallback_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY") or config.get("deepseek_api_key", "")

    if not deepseek_api_key or deepseek_api_key == "YOUR_DEEPSEEK_API_KEY":
        print("Warning: No DeepSeek API key found. Please set DEEPSEEK_API_KEY environment variable or configure in config.json")
        raise SystemExit(1)

    agent = AutonomousEoHAgent(api_key=deepseek_api_key, name="V3-Agent")

    goal = "Use tasks.json to track the 5-stage pipeline (survey/design/evolve/validate/package), run EoH evolution with structured logging, and produce paper-ready notes."
    agent.run(high_level_goal=goal, max_loops=15)
