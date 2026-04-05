# HGS-ReAct: 基于多专家协作的自主 CVRP 启发式算法演化系统

本项目 (V2.7) 旨在利用大语言模型 (LLM) 的推理能力与 **EoH (Evolution of Heuristics)** 框架深度融合，构建一个具备“自主科学发现”能力的专家团队。系统通过 **ReAct (Reasoning-Acting)** 框架驱动，实现了车辆路径问题 (CVRP) 算法的联网调研、架构设计、静态审计、演化诊断、可视化报告及工业级部署。

***

## 🛠️ 环境要求 (Requirements)

- Python 3.8+
- `numpy`
- `requests`
- `scipy` (可选)

***

## 🚦 如何运行 (How to Run)

### V0: 基础演化 (Baseline)

```bash
python v0_baseline/runEoH.py
```

### V1: 自动化流水线 (Workflow)

```bash
python v1_workflow/master_agent.py
```

### V2.0版本: 自主 ReAct 智能体 (Agent)

```bash
python v2_agent/react_master_agent.py
```

### V3.0版本: 结构化流水线与可复盘账本 (Agent)

```bash
python v3_agent/react_master_agent.py
```

**新增产物（v3\_agent 独立）**:

# `v3_agent/state/tasks.json`: 5 阶段任务树（survey/design/evolve/validate/package）

- `v3_agent/state/project_truth.md`: 工程事实 + 论文叙事的共享真相面
- `v3_agent/state/session_context.md`: 会话上下文快照（启动必读）
- `v3_agent/logs/evolution_ledger.jsonl`: 一次进化（一次 EVOL 调用）一条记录
- `v3_agent/logs/review_log.md`: Reviewer 门禁记录

### 📊 性能对比测试 (Benchmark)

```bash
python v2_agent/benchmark_comparison.py
```

***

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
 ├── v3_agent/                   # V3 ReAct 智能体（与 v2 隔离：结构化任务/真相面/账本）
 │   ├── react_master_agent.py   # V3 智能体主程序
 │   ├── react_tools.py          # 工具箱封装（自动写入 state/logs）
 │   └── state/                  # tasks.json / project_truth.md / session_context.md
 ├── visualizations/             # 结果可视化输出
 ├── architect_agent.py          # 架构师：设计 PRM (基于统计数据)
 ├── prob.py                     # 核心问题定义与评估逻辑 (含 Split 算法)
 ├── prompts.py                  # LLM 提示词模板
 ├── refine_agent.py             # 调优专家：修复与优化代码 (DeepSeek)
 └── visualize_results.py        # 结果分析与可视化脚本
```

### 工作流程 (Workflows)

#### 基础准备：数据与基准 (Shared Data Preparation)

无论是哪个版本，首先需要准备实例数据和基准性能数据：

```bash
# 1. 下载 CVRPLib 基准实例
python v0_baseline/download_cvrplib.py

# 2. 生成合成训练数据 (SFT) - 可选
python v0_baseline/generate_synthetic_data.py

# 3. 生成性能基准数据 (DPO/RLHF)
python v0_baseline/generate_performance_dataset.py
```

#### V0: 基础演化 (Baseline EoH)

纯粹的 EoH 演化模式，适合初次运行。

```bash
python v0_baseline/runEoH.py
```

- **核心逻辑**: 加载 `data/` 实例 -> 评估初始种群 -> LLM 生成变体 -> 保存优胜算法。

#### V1: 自动化流水线 (Workflow Automation)

引入 Master Agent 驱动“分析-演化-精炼”的闭环。

```bash
python v1_workflow/master_agent.py
```

- **核心逻辑**: KIMI 设计 PRM -> DeepSeek 运行 EoH 演化 -> 分析结果 -> 自动修复 'None' 报错代码 -> 反馈循环。

#### V2.4: 自主 ReAct 智能体 (Intelligent ReAct Agent)

目前最强大的版本，具备联网调研、多角色协作与严谨质检能力。

```bash
python v2_agent/react_master_agent.py
```

- **核心逻辑**:
  1. **调研**: 通过 `web_search` 在 arXiv/GitHub 寻找灵感。
  2. **协作**: Architect 与 Coder 通过 `handoff.md` 同步设计意图。
  3. **演化**: 基于动态 PRM 策略生成高性能代码。
  4. **质检**: 调用 `run_comprehensive_evaluation` (QT 工具) 进行多实例交叉验证。

#### V3.0: 结构化流水线与可复盘账本 (Isolated V3 Agent)

在 V2 的能力基础上，新增“结构化任务树 + 最小共享真相面 + 一次进化一条账本 + 会话上下文快照”，并将所有状态/日志与 v2\_agent 隔离，便于复盘与论文写作。

```bash
python v3_agent/react_master_agent.py
```

#### � 性能量化对比 (Benchmark)

一键对比所有版本的性能表现：

```bash
python v2_agent/benchmark_comparison.py
```

- **产出**: 控制台对比表格 + `visualizations/performance_comparison_report.png`。

### V2.5: 后训练数据采集 (Post-training Data Collection)

- **核心逻辑**: 自动收集 (PRM 策略, 架构师思考, 演化轨迹) 三元组数据。
- **产出**: `v2_agent/training_data/prm_evolution_dataset.jsonl`。
- **用途**: 用于微调大模型，使其在没有外部反馈的情况下也能直接写出具备“良好算法品味”的 PRM。

### V2.6: 专家团队协同与科研自动化 (Expert Team & Research Automation)

- **核心逻辑**: 引入“分析-审计-整理”多专家角色，实现全流程科研自动化。
- **功能**: Master 驱动，Analyst 诊断瓶颈，Reviewer 拦截错误代码，Librarian 结构化知识。
- **价值**: 显著提升演化效率，实现种子库的自主动态增长。

### V2.7: 可视化报告与工业级部署 (Visualization & Deployment)

- **核心逻辑**: 增强成果展示与转化能力。
- **功能**: Visualizer 生成收敛曲线与路径图，Deployer 封装独立 Python 模块。
- **价值**: 增强研究的可解释性，实现从算法发现到生产应用的无缝闭环。

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

***

### 🤖 核心专家团队 (Agent Ecosystem)

- **Master Agent (总控专家)**: 采用 ReAct 循环，负责全局任务拆解、目标设定与跨 Agent 调度。
- **Librarian Agent (知识库管理员)**: 负责结构化管理 `research_notes.md`，从海量搜索结果中提炼 SOTA 榜单与算法算子库。
- **Architect Agent (算法架构师)**: 基于演化反馈，动态设计过程奖励模型 (PRM) 并注入评估环境，引导进化方向。
- **Reviewer Agent (质检专家)**: 执行代码门禁。在算法入库前进行静态扫描与 Mock 运行，拦截死循环与逻辑缺陷。
- **Analyst Agent (性能分析专家)**: 深度剖析演化轨迹，识别收敛瓶颈与种群多样性，为系统提供战略性调整建议。
- **Refiner Agent (调优专家)**: 针对性能不佳或报错的代码，利用逻辑推理能力进行最小化修复与精细化重构。
- **Visualizer Agent (可视化专家)**: 负责结果可视化。生成路径图、收敛曲线、对比图表，并自动嵌入到科研笔记中。
- **Deployer Agent (部署专家)**: 负责成果转化。将最佳算法封装为独立 Python 模块，生成接口文档并进行压力测试，确保研究成果可直接应用于生产环境。

### 🔄 自主科研工作流 (Autonomous Research Workflow)

1. **联网探索**: Master 联合 Librarian 通过 `web_search` 调研 SOTA (Best Known Solutions) 与最新论文思路。
2. **种子固化**: 发现优秀实现后，由 Reviewer 审计安全性，随后通过 `add_new_seed` 自动扩充初始种子库。
3. **策略注入**: Architect 根据调研结论设计 PRM，通过引导“算法品味”来缩小 LLM 的搜索空间。
4. **闭环演化**: 启动 EoH 演化流程，系统根据实时反馈（Fitness, Error Rate）自主决策下一步行动。
5. **诊断与纠偏**: 当性能陷入平台期，Analyst 介入诊断，触发 PRM 重构或 Refiner 介入，确保演化持续增益。
6. **可视化展示**: 演化完成后，由 Visualizer 生成直观的收敛曲线与路径地图，增强研究结果的可解释性。
7. **工业级部署**: 最终由 Deployer 将最优算法打包，实现从科研发现到工程应用的无缝衔接。

***

## 🖼️ 版本演进效果演示 (Version Evolution)

|              V0: 基础演化 (Baseline)              |              V1: 自动化流水线 (Workflow)             |             V2: ReAct 智能体 (Agent)             |
| :-------------------------------------------: | :--------------------------------------------: | :-------------------------------------------: |
| !\[V0]\(./docs/figures/v0\_baseline.png null) | !\[V1]\(./docs/figures/v1\_workflow\.png null) |   !\[V2]\(./docs/figures/v2\_agent.png null)  |
|          *基础贪心策略 (Nearest Neighbor)*          |                *全局启发式搜索 (Sweep)*               | *智能体自主优化 (Farthest Insertion + Local Search)* |

### 📈 性能量化对比 (Performance Benchmark)

下图展示了三个版本在不同 CVRP 实例上的总路径成本对比（数值越低代表性能越好）：

!\[Performance Comparison]\(./docs/figures/performance\_comparison.png null)

***

## 🚀 核心方案设计：以 CVRP 为例

CVRP (Capacitated Vehicle Routing Problem) 是 NP-Hard 问题。我们采用 **"Route-First, Cluster-Second" (先排序，后切分)** 的经典思路进行拆解：

1. **算子化拆分**: 我们只让 LLM 负责实现 `generate_giant_tour` 函数（生成所有客户的全局访问顺序）。这发挥了 LLM 在模式识别和空间聚类上的直觉优势，避免了其处理复杂容量约束时的幻觉。
2. **精确切分 (Split)**: LLM 生成的 Giant Tour 会被送入评估环境，由我们实现的基于 **动态规划 (Dynamic Programming)** 的 `optimal_split` 算法进行最优路径切分，确保不超载且距离最短。
3. **局部搜索 (Local Search)**: 在 Split 之后引入局部搜索（如 2-opt、跨路径移动），打破固定顺序的局限性，进一步降低总距离。
4. **闭环进化**: 环境返回精确的 `Cost` 给 LLM，作为下一轮进化的指标，形成自适应改进系统。

***

## 📌 大版本迭代 (Version History)

### V0.0: 数据基础与演化环境 (Data & Evolution Foundation)

- **核心逻辑**: 建立 CVRP 问题的数学模型与评估环境。
- **关键文件**:
  - [v0\_baseline/download\_cvrplib.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/download_cvrplib.py): 自动下载真实实例。
  - [v0\_baseline/runEoH.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/runEoH.py): 运行进化流程。
  - [prob.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/prob.py): 核心问题定义与评估逻辑。

### V1.0: 自动化流水线 (Workflow Automation)

- **核心逻辑**: 通过 Agent 驱动固定的“分析-演化-精炼”闭环。
- **关键文件**:
  - [v1\_workflow/master\_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v1_workflow/master_agent.py): V1 固定流水线主程序。
  - [v0\_baseline/generate\_synthetic\_data.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v0_baseline/generate_synthetic_data.py): 生成合成训练数据。

### V2.0: 自主 ReAct 智能体 (Intelligent ReAct Agent)

- **核心逻辑**: 引入 ReAct 循环，使系统能根据实时观察动态决策行动。
- **关键文件**:
  - [v2\_agent/react\_master\_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py): V2 智能体主程序。
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py): 智能体工具箱。

***

## ️ 环境增强 (V1 & V2 共用)

- **鲁棒性初始化**: 修复了种子算法加载时遇到 `None` 崩溃的问题。
- **深度错误捕获**: `prob.py` 能够捕获完整的 Traceback。
- **绝对路径管理**: 确保跨目录运行时的路径一致性。

***

**💡 开发提示**:

- 请确保在相应的 Agent 文件中配置了 API Key。
- V2 建议使用 DeepSeek-V3 或更高版本模型以获得最佳推理效果。

***

## 📜 更新日志与建议 (Update Log & Suggestions)

### V2.2: 增强型自主智能体 (Enhanced Autonomous Agent)

- **更新时间**: 2026-03-20
- **文件改动**:
  - [v2\_agent/config.json](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/config.json): 新增集中式 API 密钥管理。
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
    - 集成 `config.json` 加载逻辑。
    - 新增 `read_research_notes` 工具，赋予智能体“长期记忆”读取能力。
    - 新增 `visualize_best_solution` 工具，支持自动调用 [visualize\_results.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/visualize_results.py) 绘制 CVRP 路径图。
    - 优化 `analyze_latest_results`，支持在演化未启动时的鲁棒分析。
  - [v2\_agent/react\_master\_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py): 注册新工具并更新入口逻辑以使用配置。
  - [v2\_agent/research\_notes.md](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/research_notes.md): 预置 CVRP 领域知识库，引导智能体初期研究方向。
- **自主建议 (Autonomous Suggestions)**:
  3\. **多实例验证**: 目前智能体主要针对单实例优化，建议在 `react_tools.py` 中增加“多实例批处理评估”工具，以提升算法的泛化性能。
  4\. **错误自动修复**: V2 已具备看懂 Traceback 的能力，建议在 `react_master_agent.py` 的提示词中进一步强调"根据报错信息进行最小化修复"的策略。

### V2.3: 外部知识获取增强 (External Knowledge Acquisition)

- **更新时间**: 2026-03-21
- **文件改动**:
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
    - 增强 `web_search` docstring，添加 "Use this tool when..." 引导，明确何时应该使用外部搜索。
    - 新增 `fetch_paper_summary` 工具，支持从 arXiv 获取论文摘要、作者、发布时间等信息，自动保存到 research\_notes.md。
    - 新增 `read_github_repo` 工具，支持从 GitHub 获取 README 和 Python 源码，自动保存到 research\_notes.md。
    - 新增 `install_missing_package` 工具，支持智能体自主安装缺失的 Python 包（如遇到 ModuleNotFoundError 时自动调用 pip install）。
    - 修复 `visualize_best_solution`，移除对 `generate_performance_dataset` 的依赖，改为使用 `prob.Evaluation()` 直接读取实例。
  - [v2\_agent/react\_master\_agent.py](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py):
    - 在 system\_prompt 中增加外部知识重要性提示，强调当遇到瓶颈时应主动搜索。
    - 注册 `fetch_paper_summary`、`read_github_repo` 和 `install_missing_package` 三个新工具。
  - [v2\_agent/research\_notes.md](file:///c:/Users/24294/.vscode/EEOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/research_notes.md): 精简为基础概念，移除详细实现，迫使智能体主动搜索外部知识。
- **功能升级**:
  - 智能体现在具备真正的联网搜索能力，可从 arXiv 和 GitHub 获取最新论文和代码。
  - 所有搜索结果自动追加到 research\_notes.md，形成持续积累的知识库。
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

### V2.4: 工程化与多角色协作增强 (Engineering & Multi-Agent Collaboration)

- **更新时间**: 2026-03-22
- **文件改动**:
  - [v2\_agent/handoff.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/handoff.md): 新增交接文档，用于记录 Architect 到 Coder 的设计意图与技术约束。
  - [v2\_agent/SKILLS.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/SKILLS.md): 新增技能描述文件，实现工具调用的插件化管理。
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
    - 新增 `update_handoff` 和 `read_handoff` 工具，支持角色间的信息传递。
    - 新增 `run_comprehensive_evaluation` (QT 工具)，支持在多个代表性实例上进行全面评估并生成 Markdown 报告。
  - [v2\_agent/react\_master\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py):
    - 升级 System Prompt，支持 Memory, Plan, Research Notes, Handoff 四种知识源。
    - 实现动态加载 `SKILLS.md` 注入 Prompt，提升智能体对自身能力的认知。
- **功能升级**:
  - **Handoff 机制**: 建立了正式的角色间沟通渠道，确保设计意图（PRM 逻辑等）在不同 Agent 间准确传递。
- **QT (质量门禁)**: 引入了多实例交叉验证机制，算法不再只针对单一实例优化，提升了泛化性能。
- **技能插件化**: 工具描述与代码实现解耦，使得 Prompt 更加整洁且易于维护。

### V2.5: 数据闭环与训练数据采集 (Data Loop & Collection)

- **更新时间**: 2026-03-22
- **核心逻辑**: 实现演化数据的自动采集，用于大模型的后训练 (Post-training)。
- **产出**: `v2_agent/training_data/prm_evolution_dataset.jsonl`，用于微调模型以获取更佳的“算法品味”。

### V2.6: 专家团队协同与科研自动化 (Expert Team & Research Automation)

- **更新时间**: 2026-03-23
- **核心逻辑**: 引入了更细分的研究员角色，形成“分析-审计-整理”的科研全流程自动化。
- **文件改动**:
  - [analyst\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/analyst_agent.py): **分析专家**。深度剖析演化轨迹，诊断收敛瓶颈，为 Master 提供战略决策支持。
  - [reviewer\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/reviewer_agent.py): **质检专家**。对生成的代码进行静态扫描和 Mock 运行测试，拦截死循环和规范性错误。
  - [librarian\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/librarian_agent.py): **知识库管理员**。利用 LLM 将零散的 `research_notes.md` 提炼为结构化的知识库。
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
    - 集成 `run_deep_analysis` 工具。
    - 集成 `run_code_review` 工具，作为代码入库前的强制门禁。
    - 集成 `organize_research_notes` 工具，实现笔记自动格式化。
    - 增强 `add_new_seed`，支持智能体从外部搜索结果中提取并固化优秀算法。
- **功能升级**:
  - **全自动科研闭环**: 从联网搜索、代码提取、质检审计到演化优化，实现了全流程的闭环。
  - **种子库动态增长**: 智能体现在可以像人类研究员一样，在搜索到好论文或好代码后，将其手动（通过工具）转化为自己的种子库。
  - **高效率进化**: 通过 Reviewer Agent 拦截无效代码，节省了大量的硬件评估资源。

### V2.7: 可视化专家与部署专家 (Visualizer & Deployer Agents)

- **更新时间**: 2026-03-24
- **文件改动**:
  - [visualizer\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/visualizer_agent.py): **可视化专家**。负责生成收敛曲线、路径轨迹图，并将图片自动嵌入科研笔记。
  - [deployer\_agent.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/deployer_agent.py): **部署专家**。将最佳算法封装为独立的 Python 模块，生成 README 文档并进行压力测试。
  - [v2\_agent/react\_tools.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py):
    - 集成 `generate_visual_report` 工具。
    - 集成 `deploy_best_algorithm` 工具。
- **功能升级**:
  - **成果直观化**: 科研结论不再只是枯燥的 Fitness 数值，而是包含直观的可视化图表。
  - **工程化落地**: 实现了从演化算法到独立模块的自动化转换，支持工业级调用。

