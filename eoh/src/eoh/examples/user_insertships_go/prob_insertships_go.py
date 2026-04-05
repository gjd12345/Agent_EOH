import json
import os
import re
import shutil
import subprocess
import tempfile
import traceback
import warnings

from prompts_insertships_go import GetPrompts


def _find_upwards_dir(start_dir: str, target_dir_name: str, max_depth: int = 10) -> str | None:
    cur = os.path.abspath(start_dir)
    for _ in range(max_depth):
        candidate = os.path.join(cur, target_dir_name)
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


def _parse_final_cost(output: str) -> float | None:
    m = re.search(r"final cost\s+(-?\d+(?:\.\d+)?)", output)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _replace_insertships(main_go_path: str, new_method: str) -> None:
    with open(main_go_path, "r", encoding="utf-8") as f:
        s = f.read()
    pat = r"func\s+InsertShips\s*\(\s*dispatch\s+Dispatch\s*,\s*oris\s*,\s*dess\s*\[\]Station\s*,\s*total_ship\s+int\s*\)\s*Dispatch\s*\{[\s\S]*?\n\}"
    m = re.search(pat, s)
    if not m:
        raise ValueError("InsertShips method not found in main.go")
    s2 = s[: m.start()] + new_method.strip() + "\n" + s[m.end() :]
    with open(main_go_path, "w", encoding="utf-8") as f:
        f.write(s2)

def _safe_write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class Evaluation:
    def __init__(
        self,
        sim_time_multi: int = 10,
        max_instances: int = 1,
        per_instance_penalty: float = 1e9,
        build_timeout_s: int = 60,
        run_timeout_s: int = 15,
    ):
        self.prompts = GetPrompts()
        self._last_error = None
        self._last_traceback = None

        base_dir = os.path.dirname(__file__)
        archive_dir = _find_upwards_dir(base_dir, "Archive_extracted", max_depth=12)
        if archive_dir is None:
            archive_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", ".."))
        self.archive_dir = os.path.abspath(archive_dir)

        self.solomon_dir = os.path.join(self.archive_dir, "solomon_benchmark")
        self.sim_time_multi = int(sim_time_multi)
        self.max_instances = int(max_instances)
        self.per_instance_penalty = float(per_instance_penalty)
        self.build_timeout_s = int(build_timeout_s)
        self.run_timeout_s = int(run_timeout_s)

        all_files = sorted([f for f in os.listdir(self.solomon_dir) if f.lower().endswith(".json")])
        self.instance_files = [os.path.join(self.solomon_dir, f) for f in all_files[: self.max_instances]]

        self.go_main = os.path.join(self.archive_dir, "main.go")
        self.go_routing = os.path.join(self.archive_dir, "routing.go")
        self.go_mod = os.path.join(self.archive_dir, "go.mod")
        self.go_sum = os.path.join(self.archive_dir, "go.sum")

    def _build_and_run(self, insertships_method_go: str) -> float | None:
        tmp = tempfile.mkdtemp(prefix="eoh_insertships_go_")
        try:
            shutil.copy2(self.go_main, os.path.join(tmp, "main.go"))
            shutil.copy2(self.go_routing, os.path.join(tmp, "routing.go"))
            shutil.copy2(self.go_mod, os.path.join(tmp, "go.mod"))
            if os.path.exists(self.go_sum):
                shutil.copy2(self.go_sum, os.path.join(tmp, "go.sum"))

            main_go_path = os.path.join(tmp, "main.go")
            _replace_insertships(main_go_path, insertships_method_go)

            build = subprocess.run(
                ["go", "build", "-o", "mainbin.exe", "."],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=self.build_timeout_s,
                check=False,
            )
            if build.returncode != 0:
                self._last_error = "Go build failed"
                self._last_traceback = (build.stdout or "") + "\n" + (build.stderr or "")
                return None

            import concurrent.futures
            total = 0.0
            details = []
            
            def _run_single_instance(inst_path: str) -> dict:
                run = subprocess.run(
                    [os.path.join(tmp, "mainbin.exe"), inst_path, str(self.sim_time_multi)],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                    timeout=self.run_timeout_s,
                    check=False,
                )
                out = (run.stdout or "") + "\n" + (run.stderr or "")
                cost = _parse_final_cost(out)
                name = os.path.basename(inst_path)
                return {"instance": name, "cost": cost, "returncode": run.returncode}

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(_run_single_instance, self.instance_files))
                
            for res in results:
                details.append(res)
                if res["cost"] is None or res["cost"] < 0:
                    total += self.per_instance_penalty
                else:
                    total += float(res["cost"])
            self._last_traceback = json.dumps(details, ensure_ascii=False)
            return total / max(len(self.instance_files), 1)
        finally:
            try:
                shutil.rmtree(tmp, ignore_errors=True)
            except Exception:
                pass

    def evaluate(self, code_string):
        self._last_error = None
        self._last_traceback = None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                if "func" not in code_string or "InsertShips" not in code_string:
                    self._last_error = "Missing InsertShips method definition"
                    return self.per_instance_penalty

                fitness = self._build_and_run(code_string)
                if fitness is None:
                    return self.per_instance_penalty
                return float(fitness)
        except Exception as e:
            self._last_error = f"General error: {str(e)}"
            self._last_traceback = traceback.format_exc()
            return self.per_instance_penalty
