# Agent Skills (智能体技能插件)
- This file defines the available tools for the ReAct agent in a structured way.

## Core Evolution Skills
- **run_evolution**: 运行 EoH 进化流程。参数: `generations` (int), `seed_path` (str, optional)。
- **analyze_latest_results**: 分析最新演化轨迹，提取 Fitness、错误率和最佳代码。
- **run_deep_analysis**: 调用分析专家 (Analyst Agent) 对演化过程进行深度诊断。使用场景: 当性能遇到瓶颈、不收敛或错误率持续走高时使用。
- **design_new_prm**: 设计过程奖励模型。参数: `problem_description` (str), `feedback_stats` (dict, 必须包含 'best_fitness', 'none_rate' 等键)。
- **refine_best_code**: 调用调优智能体修复代码。参数: `best_code` (str), `objective` (float), `error_msg` (str), `traceback_msg` (str)。
- **run_code_review**: 调用质检专家 (Reviewer Agent) 对代码进行静态扫描和 Mock 测试。参数: `code` (str, optional)。如果未提供 code，则自动审查最新的最佳代码。使用场景: 在将新代码加入种子库或运行大规模演化前使用。
- **add_new_seed**: 手动添加算法到种子库。参数: `algorithm_name` (str), `code` (str)。使用场景: 当通过 `web_search` 或 `read_github_repo` 发现优秀算法实现时使用。

## Research & Knowledge Skills
- **web_search**: 使用 Tavily API 搜索互联网，自动保存到 research_notes.md。
- **fetch_paper_summary**: 抓取并总结 arXiv 论文摘要。
- **read_github_repo**: 读取 GitHub 仓库的 README 和核心代码。
- **read_research_notes**: 读取科研笔记以回顾之前的发现。
- **organize_research_notes**: 调用知识库管理员 (Librarian Agent) 对科研笔记进行结构化整理。使用场景: 定期整理笔记以提高检索效率。

## State & Collaboration Skills
- **update_memory**: 更新 MEMORY.md。参数: `finding` (str, opt), `failure` (str, opt), `strategy` (str, opt)。
- **update_plan**: 更新 PLAN.md。参数: `goal` (str, opt), `task_completed` (str, opt), `new_task` (str, opt)。
- **update_handoff**: Agent 间交接。参数: `content` (str), `from_agent` (str), `to_agent` (str)。
- **read_memory**: 读取长期记忆。
- **read_plan**: 读取战略计划。
- **read_handoff**: 读取交接文档。

## Quality Control (QT) Skills
- **run_comprehensive_evaluation**: 在多个代表性实例上进行全面评估并生成性能报告。
- **visualize_best_solution**: 在特定实例上运行并生成路径可视化图。
- **generate_visual_report**: 调用可视化专家 (Visualizer Agent) 生成收敛曲线和路径图，并自动嵌入到科研笔记中。
- **deploy_best_algorithm**: 调用部署专家 (Deployer Agent) 将最佳算法打包为独立模块并进行压力测试。

## System Utility Skills
- **install_missing_package**: 自主安装缺失的 Python 包。
- **finish**: 标记任务已完成。
