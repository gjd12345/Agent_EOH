# 用户 CVRP 启发式算法生成系统 (HGS)

本项目专注于利用大语言模型 (LLM) 研发高性能组合优化算法。本项目基于 **EoH (Evolution of Heuristics)** 框架，实现了车辆路径问题 (CVRP) 启发式算法的自主演化、分析、纠错与优化。

---

## 📂 项目架构与快速运行 (Detailed Architecture & Quick Start)

项目按功能演进分为三个阶段：数据基础、合成数据生成以及性能基准评估。

### 项目结构 (Project Structure)
```text
user_cvrp_hgs/ 
 ├── data/                       # 存放 .vrp 格式的实例文件 (从 CVRPLib 下载) 
 ├── results/                    # 演化过程结果存储 (轨迹、种群等)
 ├── v0_baseline/                # 基础演化与数据生成 (核心脚本集)
 │   ├── download_cvrplib.py     # 自动下载真实实例
 │   ├── generate_synthetic_data.py # 生成合成 SFT 训练数据
 │   ├── generate_performance_dataset.py # 评估算法性能并生成数据集
 │   ├── heuristics_lib.py       # 经典启发式算法库
 │   └── runEoH.py               # 运行进化流程的主入口
 ├── v1_workflow/                # 自动化流水线
 │   └── master_agent.py         # 驱动闭环演化
 ├── v2_agent/                   # 自主 ReAct 智能体
 │   ├── react_master_agent.py   # V2 智能体主程序
 │   └── react_tools.py          # 工具箱封装
 ├── visualizations/             # 结果可视化输出
 ├── architect_agent.py          # 架构师：设计 PRM (基于统计数据)
 ├── prob.py                     # 核心问题定义与评估逻辑 (含 Split 算法)
 ├── prompts.py                  # LLM 提示词模板
 ├── refine_agent.py             # 调优专家：修复与优化代码 (DeepSeek)
 └── visualize_results.py        # 结果分析与可视化脚本
```

### 工作流程 (Workflow)

#### 1. 数据准备 (Data Preparation)
首先，下载 CVRPLib 的基准测试实例。
```bash
python v0_baseline/download_cvrplib.py
```

#### 2. 生成合成训练数据 (Generate Synthetic Training Data - SFT)
```bash
python v0_baseline/generate_synthetic_data.py
```

#### 3. 生成性能基准数据 (Generate Performance Baseline - RLHF/DPO)
```bash
python v0_baseline/generate_performance_dataset.py
```

#### 4. 运行进化流程 (Run Evolution - EoH)
```bash
python v0_baseline/runEoH.py
```
*   **运行过程**:
    1. 加载 `data/` 中的真实实例。
    2. 评估初始种群的性能 (基于 `heuristics_lib.py`)。
    3. LLM 生成新的变体代码 (通过 Mutation 变异 / Crossover 交叉算子)。
    4. 在真实实例上评估新代码。
    5. 保存性能提升的算法。

### 运行结果示例 (Result Example)
运行 `generate_performance_dataset.py` 脚本后，会生成 `cvrp_performance_dataset_real.jsonl` 文件。为了避免 README 过长，这里只展示每条记录中的 `metadata` 片段示例：
```json
{
  "metadata": {
    "instance": "A-n32-k5.vrp",
    "n_customers": 31,
    "algorithm": "Nearest Neighbor. Greedily selects the closest unvisited customer.",
    "best_cost": 1023.8992597852659,
    "avg_cost": 1023.8992597852659,
    "num_runs": 1
  }
}
```

---

## 🚀 核心方案设计：以 CVRP 为例

CVRP (Capacitated Vehicle Routing Problem) 是 NP-Hard 问题。我们采用 **"Route-First, Cluster-Second" (先排序，后切分)** 的经典思路进行拆解：

1.  **算子化拆分**: 我们只让 LLM 负责实现 `generate_giant_tour` 函数（生成所有客户的全局访问顺序）。这发挥了 LLM 在模式识别和空间聚类上的直觉优势，避免了其处理复杂容量约束时的幻觉。
2.  **精确切分 (Split)**: LLM 生成的 Giant Tour 会被送入评估环境，由我们实现的基于 **动态规划 (Dynamic Programming)** 的 `optimal_split` 算法进行最优路径切分，确保不超载且距离最短。
3.  **局部搜索 (Local Search)**: 在 Split 之后引入局部搜索（如 2-opt、跨路径移动），打破固定顺序的局限性，进一步降低总距离。
4.  **闭环进化**: 环境返回精确的 `Cost` 给 LLM，作为下一轮进化的指标，形成自适应改进系统。

---

## 📌 版本迭代 (Version History)

### V0.0: 数据基础与演化环境 (Data & Evolution Foundation)
- **核心逻辑**: 建立 CVRP 问题的数学模型与评估环境。
- **关键文件**: 
  - [v0_baseline/download_cvrplib.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/download_cvrplib.py): 自动下载真实实例。
  - [v0_baseline/runEoH.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/runEoH.py): 运行进化流程。
  - [prob.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/prob.py): 核心问题定义与评估逻辑。

### V1.0: 自动化流水线 (Workflow Automation)
- **核心逻辑**: 通过 Agent 驱动固定的“分析-演化-精炼”闭环。
- **关键文件**:
  - [v1_workflow/master_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v1_workflow/master_agent.py): V1 固定流水线主程序。
  - [v0_baseline/generate_synthetic_data.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/generate_synthetic_data.py): 生成合成训练数据。

### V2.0: 自主 ReAct 智能体 (Intelligent ReAct Agent)
- **核心逻辑**: 引入 ReAct 循环，使系统能根据实时观察动态决策行动。
- **关键文件**:
  - [v2_agent/react_master_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py): V2 智能体主程序。
  - [v2_agent/react_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py): 智能体工具箱。

---

## 🛠️ 环境要求 (Requirements)
*   Python 3.8+
*   `numpy`
*   `requests`
*   `scipy` (可选)

---

## 🚦 如何运行

```bash
python v0_baseline/runEoH.py
```

---

## ️ 环境增强 (V1 & V2 共用)

-   **鲁棒性初始化**: 修复了种子算法加载时遇到 `None` 崩溃的问题。
-   **深度错误捕获**: `prob.py` 能够捕获完整的 Traceback。
-   **绝对路径管理**: 确保跨目录运行时的路径一致性。

---

**💡 开发提示**: 
- 请确保在相应的 Agent 文件中配置了 API Key。
- V2 建议使用 DeepSeek-V3 或更高版本模型以获得最佳推理效果。

---

## 📜 更新日志与建议 (Update Log & Suggestions)

### V2.2: 增强型自主智能体 (Enhanced Autonomous Agent)
- **更新时间**: 2026-03-20
- **文件改动**:
    - [v2_agent/config.json](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/config.json): 新增集中式 API 密钥管理。
    - [v2_agent/react_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py): 
        - 集成 `config.json` 加载逻辑。
        - 新增 `read_research_notes` 工具，赋予智能体“长期记忆”读取能力。
        - 新增 `visualize_best_solution` 工具，支持自动调用 [visualize_results.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/visualize_results.py) 绘制 CVRP 路径图。
        - 优化 `analyze_latest_results`，支持在演化未启动时的鲁棒分析。
    - [v2_agent/react_master_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py): 注册新工具并更新入口逻辑以使用配置。
    - [v2_agent/research_notes.md](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/research_notes.md): 预置 CVRP 领域知识库，引导智能体初期研究方向。

- **自主建议 (Autonomous Suggestions)**:
    3. **多实例验证**: 目前智能体主要针对单实例优化，建议在 `react_tools.py` 中增加“多实例批处理评估”工具，以提升算法的泛化性能。
    4. **错误自动修复**: V2 已具备看懂 Traceback 的能力，建议在 `react_master_agent.py` 的提示词中进一步强调"根据报错信息进行最小化修复"的策略。

### V2.3: 外部知识获取增强 (External Knowledge Acquisition)
- **更新时间**: 2026-03-21
- **文件改动**:
    - [v2_agent/react_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
        - 增强 `web_search` docstring，添加 "Use this tool when..." 引导，明确何时应该使用外部搜索。
        - 新增 `fetch_paper_summary` 工具，支持从 arXiv 获取论文摘要、作者、发布时间等信息，自动保存到 research_notes.md。
        - 新增 `read_github_repo` 工具，支持从 GitHub 获取 README 和 Python 源码，自动保存到 research_notes.md。
        - 新增 `install_missing_package` 工具，支持智能体自主安装缺失的 Python 包（如遇到 ModuleNotFoundError 时自动调用 pip install）。
        - 修复 `visualize_best_solution`，移除对 `generate_performance_dataset` 的依赖，改为使用 `prob.Evaluation()` 直接读取实例。
    - [v2_agent/react_master_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py):
        - 在 system_prompt 中增加外部知识重要性提示，强调当遇到瓶颈时应主动搜索。
        - 注册 `fetch_paper_summary`、`read_github_repo` 和 `install_missing_package` 三个新工具。
    - [v2_agent/research_notes.md](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/research_notes.md): 精简为基础概念，移除详细实现，迫使智能体主动搜索外部知识。

- **功能升级**:
    - 智能体现在具备真正的联网搜索能力，可从 arXiv 和 GitHub 获取最新论文和代码。
    - 所有搜索结果自动追加到 research_notes.md，形成持续积累的知识库。
    - 智能体可自主判断何时需要外部知识，并在遇到性能瓶颈时主动搜索新思路。
    - 智能体具备自动安装缺失依赖的能力，提升了自主性和鲁棒性。

- **新工作流示例**:
    ```
    遇到瓶颈（如 ALNS 实现细节不明）
        ↓
    Thought: 需要搜索 ALNS 最新实现
        ↓
    Action: web_search | query: "ALNS CVRP implementation github"
        ↓
    Observation: 发现相关 GitHub 仓库
        ↓
    Action: read_github_repo | repo_url: "https://github.com/..."
        ↓
    Action: fetch_paper_summary | paper_url: "https://arxiv.org/abs/..."

    遇到 ModuleNotFoundError
        ↓
    Thought: 缺少必要的包，需要安装
        ↓
    Action: install_missing_package | package_name: "matplotlib"
    ```
