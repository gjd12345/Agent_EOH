import os
import requests
import json
import re

class LibrarianAgent:
    """
    Librarian Agent for EoH.
    Structures and cleans up research notes.
    """
    def __init__(self, api_key, endpoint="https://api.deepseek.com", model="deepseek-chat"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model

    def organize_notes(self, notes_content: str) -> str:
        """
        Organizes existing research notes into a structured format.
        """
        if not notes_content or len(notes_content) < 50:
            return "No enough content to organize."

        prompt = f"""
You are a Senior Librarian Agent. Your goal is to structure and clean up research notes for a CVRP algorithm research project.

### Current Research Notes:
{notes_content}

### Your Task:
Organize the notes into a clear, professional Markdown document. 
Focus on these sections:
1. **SOTA Benchmark & Targets**: Best Known Solutions (BKS) and known lower bounds for key instances (e.g., A-n32-k5).
2. **Heuristic Strategy Library**: Summaries of algorithm ideas (e.g., ALNS, HGS, specific insertion/local search rules).
3. **Common Failure Patterns**: Record recurring errors or logic traps encountered.
4. **Experimental Insights**: Key findings from recent evolution runs.

### Requirements:
- Keep information concise and accurate.
- Use clean Markdown formatting.
- Remove redundant or outdated information.
- Provide the structured notes in a clean Markdown block.

Return ONLY the structured Markdown. No explanation.
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
            structured_content = response.json()["choices"][0]["message"]["content"]
            
            # Clean up if LLM returns it in a code block
            structured_content = re.sub(r'```markdown|```', '', structured_content).strip()
            return structured_content
        except Exception as e:
            return f"Librarian Agent error: {e}"

if __name__ == "__main__":
    librarian = LibrarianAgent(api_key="YOUR_KEY")
    test_notes = "# Notes\n- Finding 1: BKS is 1024\n- Code 1: def tour()..."
    print(librarian.organize_notes(test_notes))
