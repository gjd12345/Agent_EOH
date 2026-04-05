# Agent_EOH: 基于EOH框架的代码自进化Agent

基于 EoH (Evolution of Heuristics) 框架的自主科研智能体系统，专注于 CVRP（ Capacitated Vehicle Routing Problem）等组合优化问题的算法自动设计。

---

## 🎯 项目概述

本项目实现了从 V0（基础演化）到 V2（ReAct 智能体）的完整演进路径，智能体能够：
- 自主设计并优化 CVRP 启发式算法
- 联网搜索最新论文和代码实现
- 自动修复代码错误
- 持续积累领域知识

---

## 🖼️ 版本效果演示 (Version Evolution)

| V0: 基础演化 (Baseline) | V1: 自动化流水线 (Workflow) | V2: ReAct 智能体 (Agent) |
| :---: | :---: | :---: |
| ![V0](./eoh/src/eoh/examples/user_cvrp_hgs/docs/figures/v0_baseline.png) | ![V1](./eoh/src/eoh/examples/user_cvrp_hgs/docs/figures/v1_workflow.png) | ![V2](./eoh/src/eoh/examples/user_cvrp_hgs/docs/figures/v2_agent.png) |
| *基础贪心策略 (Nearest Neighbor)* | *全局启发式搜索 (Sweep)* | *智能体自主优化 (Farthest Insertion + Local Search)* |

### 📈 性能量化对比 (Performance Benchmark)

下图展示了三个版本在不同 CVRP 实例上的总路径成本对比（数值越低代表性能越好）：

![Performance Comparison](./eoh/src/eoh/examples/user_cvrp_hgs/docs/figures/performance_comparison.png)

---

## 📂 项目结构

```
Agent_EOH/
├── eoh/                               # EoH 框架（Python 包）
│   ├── setup.py
│   └── src/eoh/
│       ├── llm/                       # LLM 接口与 API 适配层
│       ├── llm_local_server/          # 本地 LLM Server 启动脚本
│       ├── methods/                   # 演化/局部搜索/选择等方法实现
│       ├── problems/                  # 问题定义与评测（optimization / ML）
│       ├── utils/                     # 报告生成、结果处理、参数解析等
│       ├── test/                      # 运行/自测脚本
│       └── examples/
│           ├── user_cvrp_hgs/          # CVRP：V0→V3 的演进示例 ⭐
│           │   ├── v0_baseline/        # V0：基础演化
│           │   ├── v1_workflow/        # V1：自动化流水线
│           │   ├── v2_agent/           # V2：ReAct 自主智能体
│           │   └── v3_agent/           # V3：进一步增强版本
│           ├── user_genroute_go/       # GenRoute（Go）示例
│           └── user_insertships_go/    # InsertShips（Go）示例
├── examples/                          # 顶层示例（bp_online / tsp_construct 等）
├── baseline/                          # 其他基线（如 funsearch）
├── solomon_benchmarks/                # Solomon VRPTW 基准数据与脚本
├── docs/                              # 项目文档与图表
└── results/                           # 运行结果（通常不纳入版本控制）
```

### 🔑 关键入口

- CVRP（V2 ReAct 智能体）入口：`eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_master_agent.py`
- CVRP（V2 工具集合）：`eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/react_tools.py`
- CVRP 配置模板：`eoh/src/eoh/examples/user_cvrp_hgs/v2_agent/config.json.example`（复制为 `config.json` 后填入 Key）
- EoH 框架主逻辑入口：`eoh/src/eoh/eoh.py` 与 `eoh/src/eoh/methods/`

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/gjd12345/Agent_EOH.git
cd Agent_EOH/eoh/src/eoh/examples/user_cvrp_hgs
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
复制配置文件并填入你的 API Key：
```bash
cp v2_agent/config.json.example v2_agent/config.json
```

或在环境变量中设置：
```bash
export DEEPSEEK_API_KEY="your_key"
export MOONSHOT_API_KEY="your_key"
export TAVILY_API_KEY="your_key"
```

### 4. 运行 V2 智能体
```bash
cd v2_agent
python react_master_agent.py
```

---

## 📋 V2 智能体工具清单

| 工具 | 功能 |
|------|------|
| `run_evolution` | 运行 EoH 演化 |
| `analyze_latest_results` | 分析最新结果 |
| `design_new_prm` | 设计新的 PRM |
| `refine_best_code` | 精炼最优代码 |
| `web_search` | 联网搜索论文/代码 |
| `fetch_paper_summary` | 获取 arXiv 论文摘要 |
| `read_github_repo` | 读取 GitHub 仓库 |
| `read_research_notes` | 读取研究笔记 |
| `visualize_best_solution` | 可视化最优解 |
| `install_missing_package` | 自动安装缺失依赖 |

---

## 📖 详细文档

详见 [user_cvrp_hgs/README.md](./eoh/src/eoh/examples/user_cvrp_hgs/README.md)

---

## 🔗 相关链接

- [EoH 框架原始仓库](https://github.com/FeiLiu36/EoH)
- [LLM4AD 通用平台](https://github.com/Optima-CityU/llm4ad)
- [CVRPLib 基准实例](http://vrp.atd-lab.marstra.org/)

---

## 📄 License

MIT License
