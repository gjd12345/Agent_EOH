# V3 Agent Skills & Tools

本目录是 v3_agent 的技能清单与运行约定（与 v2_agent 隔离）。

## 关键产物（v3_agent 独立）

- `state/tasks.json`：唯一任务真相源（阶段/任务/状态/依赖）
- `state/project_truth.md`：共享真相面（工程事实 + 论文叙事）
- `state/session_context.md`：会话上下文快照（启动必读）
- `logs/evolution_ledger.jsonl`：一次进化（一次 EVOL 调用）一条记录
- `logs/review_log.md`：Reviewer 门禁记录
- `training_data/`：PRM↔轨迹配对数据集（用于后训练）

## 状态工具（建议优先使用）

- `sync_state()`：初始化/修复 state 与 logs，并刷新 session_context
- `read_tasks()`：读取 tasks.json
- `set_active_task(task_id, stage=None)`：设置 activeTaskId（可选切换 currentStage）
- `update_task_status(task_id, status, notes="")`：更新任务状态
- `read_session_context()`：读取 session_context.md
- `append_project_truth_fact(...)`：追加工程事实日志
- `append_project_truth_paper(...)`：追加论文叙事日志

## 演化与质检（会自动落盘）

- `run_evolution(generations, seed_path=None, task_id=None)`：运行演化，并写入 tasks.json/project_truth/evolution_ledger
- `run_code_review(code=None, task_id=None)`：运行静态+mock 门禁，并写入 review_log/project_truth

## 其他工具

其余工具与 v2_agent 基本一致（调研/PRM/分析/可视化/部署/种子维护等），但会写入 v3_agent 自己的文件。
