# PLAN.md

## Current Goal
Evolve the GenRoute operator in Archive_extracted to minimize final cost on Solomon benchmark (rc101–rc108). Baseline fitness: 206.415358.

## Status
- Stagnation at baseline after 3 generations.
- High average fitness (312500148.36) indicates many penalized candidates due to constraint violations.
- Best code is minimal: GenSeq() + RoutingTS with safe NextSta/NextTime updates.
- Research notes contain extensive insights on Solomon insertion heuristics (I1 regret, parallel insertion, time-oriented methods).

## Strategy
1. **Generate New Seeds**: Create seed candidates based on research heuristics:
   - Regret-based insertion (maximizing difference between best and second-best insertion costs).
   - Parallel insertion (constructing multiple routes simultaneously).
   - Time-oriented criteria (e.g., push-forward insertion cost).
   - Ensure seeds compile and avoid unsafe NextSta/NextTime updates.
2. **Quality Control**: Run code review on each seed before adding to seeds_genroute_go.json.
3. **Evolution Run**: Execute evolution with new seeds to explore promising variants.
4. **Analysis**: Monitor results for improvements or penalties; adjust seeds if needed.

## Next Actions
- Use generate_seeds_from_research to create a research seed file focused on regret and parallel insertion heuristics.
- Review and add promising seeds via add_new_seed after code review.
- Run evolution with updated seed pool.
- Analyze results and iterate.

## Constraints Adherence
- All seeds must be single Go method: `func (assign *Assign) GenRoute() { ... }`.
- Must compile with existing structs (Route as fixed-size array).
- NextSta/NextTime updates only if Cost >= 0.
- Keep GenRoute minimal; integrate heuristics within GenSeq() or RoutingTS calls if possible.

## Timeline
Immediate: Generate seeds from research.
Short-term: Run evolution and evaluate.
Long-term: If stagnation persists, consider hybrid approaches within GenRoute (e.g., combining heuristics).