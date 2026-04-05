# Agent Memory

## Facts
- Evaluation compiles a temporary Go binary from Archive_extracted/main.go + routing.go, replaces GenRoute, then runs rc101–rc108 and parses `final cost`.
- Baseline values match Archive_extracted/final_result.txt exactly (avg 206.415358).

## Constraints
- Candidate GenRoute code must be a single Go method definition:
  - `func (assign *Assign) GenRoute() { ... }`
- Must compile with the existing structs:
  - Route is a fixed-size array, not a slice.
- Unsafe NextSta/NextTime updates can break simulation and cause large penalties.

## Working Heuristics
- Keep GenRoute minimal: GenSeq() then RoutingTS(&assign.RoutingTask) and update NextSta/NextTime only if Cost >= 0.

## Latest Run
- Research query: Solomon VRPTW insertion heuristic I1 regret criteria time oriented
- Seeds: v2_agent/seeds_genroute_go_research.json generated; code review on seed_index=4 passed (fitness=219.810867 on rc101).
- Evolution: 2 generations, pop_size=4, instances=rc101–rc108; best_fitness stayed at baseline 206.415358; no per-instance deltas.
- Report: v2_agent/reports/genroute_report_20260401_214319.md

## Open Questions
- Which operator gives the most leverage beyond GenRoute for this codebase (InsertShips vs Optimization vs RoutingTS)?
