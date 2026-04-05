# Agent Long-term Memory
- This file stores the agent's long-term memory, including key findings, failed attempts, and successful strategies.

## Key Findings
- Successfully retrieved Clarke-Wright algorithm implementation from GitHub and added to seed library. This provides a solid foundation for evolution with known effective heuristics for CVRP.
- V2.4 Collaboration (DeepSeek + KIMI) achieved 0.0% None Rate on A-n32-k5.
- KIMI is effective at designing PRMs with polar angle and load balance penalties.
- DeepSeek is robust at implementing the `generate_giant_tour` function using Nearest Neighbor and other heuristics.

## Failed Attempts
- (Empty) - Start tracking here.

## Successful Strategies
- Begin evolution process using Clarke-Wright seed as starting point. Run initial evolution with moderate generations to establish baseline performance and identify potential issues.
- Collaborative architecture: KIMI (Architect) + DeepSeek (Refiner).
- Using `optimal_split` for route cutting in CVRP.
