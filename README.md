# Agent_EOH: 自主科研智能体系统

基于 EoH (Evolution of Heuristics) 框架的自主科研智能体系统，专注于 CVRP（ Capacitated Vehicle Routing Problem）组合优化问题的算法自动设计。

---

## 🎯 项目概述

本项目实现了从 V0（基础演化）到 V2（ReAct 智能体）的完整演进路径，智能体能够：
- 自主设计并优化 CVRP 启发式算法
- 联网搜索最新论文和代码实现
- 自动修复代码错误
- 持续积累领域知识

---

## 📂 项目结构

```
Agent_EOH/
└── eoh/src/eoh/examples/user_cvrp_hgs/
    ├── v0_baseline/           # V0: 基础演化框架
    ├── v1_workflow/           # V1: 自动化流水线
    ├── v2_agent/              # V2: ReAct 自主智能体 ⭐
    │   ├── react_master_agent.py    # 智能体主程序
    │   ├── react_tools.py           # 工具箱
    │   ├── research_notes.md        # 知识积累
    │   └── config.json.example      # 配置模板
    ├── data/                  # CVRP 实例数据
    └── README.md              # 详细文档
```

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
