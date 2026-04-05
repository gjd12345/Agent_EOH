# user_genroute_go：修改与运行结果报告

## 1. 目标与基准

- 目标：用 EoH 的 v2_agent（ReAct + planning-first）在不直接修改 `Archive_extracted` 源码的前提下，评估/进化 Go 算子 `func (assign *Assign) GenRoute()`，并尝试在 Solomon `rc101–rc108` 上超过基准。
- 基准文件： [final_result.txt](file:///c:/Users/24294/.trae/Agent_EOH/Archive_extracted/final_result.txt)
  - 基准平均（rc101–rc108）：`206.415358`

## 2. 本次新增/修改内容

### 2.1 v2_agent 目录结构完善（planning-first）

在 `eoh/src/eoh/examples/user_genroute_go/v2_agent` 新增/完善：

- 规划文件： [PLAN.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/PLAN.md)
- 记忆文件： [MEMORY.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/MEMORY.md)
- 技能说明： [SKILLS.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/SKILLS.md)
- v2_agent 工具集合： [react_tools_genroute.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/react_tools_genroute.py)
  - 新增：`read_plan/update_plan/read_memory/update_memory/read_research_notes`
  - 新增：`run_code_review`（支持直接传 `code`，或 `seed_path+seed_index`）
  - 新增：`add_new_seed`（把新的 Go GenRoute seed 追加进 `seeds_genroute_go.json`）
  - 新增：`run_deep_analysis`（卡住/惩罚过多时给诊断建议）
  - 已有：`web_search`（Tavily→追加到 research_notes.md）
  - 已有：`generate_seeds_from_research`（web_search→产出 research seed JSON）
  - 已有：`run_comprehensive_evaluation/write_report`（对齐基准输出对比表）
- v2_agent 主控： [react_master_agent_genroute.py](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/react_master_agent_genroute.py)
  - system_prompt 升级为与 `user_cvrp_hgs` 相同风格：强制“先读 PLAN/MEMORY→检索→seed→code review→进化→全量评估→写报告→更新 plan/memory”

### 2.2 研究与 seed 管理

- 研究笔记（web_search 追加写入）： [research_notes.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/research_notes.md)
- 研究驱动的 seed 文件（自动生成）： [seeds_genroute_go_research.json](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/seeds_genroute_go_research.json)
  - 包含：基准 seed + 变体 seed + “Research-guided seed（在 algorithm 字段写入 query/links/notes 路径）”

## 3. 运行流程与命令

### 3.1 直接执行（planning-first v2_agent）

在目录 `eoh/src/eoh/examples/user_genroute_go` 下：

```bash
python v2_agent/react_master_agent_genroute.py --max-loops 8 --goal "Follow the strategy strictly: 1) read_plan; 2) read_memory; 3) read_research_notes; if missing then web_search ...; 4) generate_seeds_from_research ...; 5) run_code_review seed_path='v2_agent/seeds_genroute_go_research.json' seed_index=4; 6) run_evolution generations=2 max_instances=8 sim_time_multi=1000000 seed_path='v2_agent/seeds_genroute_go_research.json' pop_size=4; 7) run_comprehensive_evaluation sim_time_multi=1000000; 8) write_report sim_time_multi=1000000; 9) update_memory ...; 10) finish"
```

对应日志文件：
- [full_v2_genroute_planning2.log](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/run_logs/full_v2_genroute_planning2.log)

### 3.2 生成研究 seed + 完整评估（非 planning 版的一次完整 run）

对应日志：
- [full_v2_genroute.log](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/run_logs/full_v2_genroute.log)

## 4. 运行结果与对比

### 4.1 关键结论

- v2_agent 能完成“检索→seed→code review→进化→评估→报告→回写 plan/memory”的完整闭环。
- 在当前算子目标 **仅为 `GenRoute`** 的情况下，进化结果与基准 **完全一致**（rc101–rc108 每个实例 delta 都为 0）。
- 说明：`GenRoute` 在该代码结构里更多是对 `RoutingTS` 的封装（重算+更新 next），对最终成本的可调空间有限；更可能带来提升的算子是 `InsertShips` / `Optimization` / `RoutingTS` 本身。

### 4.2 全量评估报告

本次 planning-first run 的报告文件：
- [genroute_report_20260401_214319.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/reports/genroute_report_20260401_214319.md)

报告中给出了：
- Avg fitness 与 baseline avg
- rc101–rc108 每个实例的 cost / baseline / delta

## 5. 状态回写（plan/memory）

- MEMORY 已记录最近一次 run 的 query、seed code review、进化与报告路径：见 [MEMORY.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/MEMORY.md)
- PLAN 已记录“GenRoute 无提升，下一步切换消融目标到 InsertShips/Optimization”：见 [PLAN.md](file:///c:/Users/24294/.trae/Agent_EOH/eoh/src/eoh/examples/user_genroute_go/v2_agent/PLAN.md)

## 6. 环境与注意事项

- 评估方式：临时复制 Go 源码并替换 `GenRoute`，编译运行后解析 stdout 的 `final cost`。
- `run_code_review` 支持：
  - `run_code_review(code=...)` 或
  - `run_code_review(seed_path=..., seed_index=...)`
- 搜索与知识沉淀：
  - `web_search` 只追加 notes
  - `generate_seeds_from_research` 会生成 research seed JSON，但其 “实质代码变体”需要进一步加强（否则容易只有文本差异、行为不变）。

## 7. 下一步建议（消融/提升方向）

为了获得超过基准的提升，建议优先把 v2_agent 的目标算子从 `GenRoute` 切换到：

1. `InsertShips`：插单顺序/准则（Solomon I1/I2/I3、regret、time-oriented criteria）
2. `Optimization`：跨车 move、接受准则、步数/温度（参考 HGS 的 relocate/swap 思路）
3. `RoutingTS`：搜索策略/剪枝（风险更高，但潜在收益更大）

