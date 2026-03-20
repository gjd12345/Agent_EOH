# CVRP Research Notes

## Basic Concepts
- **CVRP**: Capacitated Vehicle Routing Problem
- **Solution approach**: Route-First, Cluster-Second
- The LLM generates `giant_tour` (permutation of all customers)
- Environment provides `optimal_split` (DP-based) and `calculate_total_distance`

## Known Methods (no implementation details)
- Sweep algorithm
- Savings algorithm
- K-means clustering
- Local search (2-opt, Or-opt)
- ALNS (Adaptive Large Neighborhood Search)
- HGS-CVRP (Hybrid Genetic Search)

## Notes
- For implementation details of advanced methods (ALNS, LNS, tabu search),
  use web_search to find recent papers and code.
- After web_search, use fetch_paper_summary for papers or read_github_repo for code.
