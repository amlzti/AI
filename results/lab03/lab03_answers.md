# Lab 3 (Week 06) — Search Engineering: Package, Tests, CLI and Benchmark

Script: `all_experiments/lab03_search_engineering.py` · CLI: `all_experiments/utils/__main__.py`

## Results

| Check | Result |
|---|---|
| `python -m pytest utils -q` | **8 passed** (`pytest_output.txt`) |
| `python -m utils --algorithm astar --start KUL --goal KEF` | hops=4, cost=11,461.3 km, expanded=69 — KUL -> HKT -> LED -> HEL -> KEF (`cli_kul_kef.txt`) |
| `python -m utils --algorithm astar --start JFK --goal SYD` | hops=2, cost=16,035.3 km, expanded=21 — JFK -> LAX -> SYD (`cli_jfk_syd.txt`) |
| A* cost equals UCS on all 10 queries | True |
| GBFS costlier than UCS | 7 of 10 queries |

Benchmark summary (`benchmark_summary.csv`):

| Algorithm | Success | Mean cost (km) | Mean hops | Mean expanded |
|---|---|---|---|---|
| A* | 1.0 | 14,321.11 | 2.2 | 62.7 |
| BFS | 1.0 | 16,469.27 | 1.8 | 323.9 |
| GBFS | 1.0 | 15,087.33 | 2.1 | 2.1 |
| UCS | 1.0 | 14,321.11 | 2.2 | 2,700.4 |

## Discussion in pairs

**Why is GBFS fastest but not the best?** GBFS orders the frontier by h(n) only, so it heads straight
toward the goal and expands very few states (2.1 on average). It ignores the distance already flown,
g(n), so the first path it reaches is often not the shortest — it was costlier than UCS on 7 of 10 queries.

**Why does A\* match UCS?** A\* orders by f(n) = g(n) + h(n). The haversine heuristic is admissible
(a great-circle distance never overestimates the real flight distance), so A\* is guaranteed to return an
optimal path, the same cost as UCS. The heuristic only prunes states that cannot lead to a cheaper route,
so A\* needs about 63 expansions instead of UCS's 2,700.

## Check your understanding

1. **Which one line differs between UCS and A\* in `best_first`?** The priority: UCS returns `g`,
   A\* returns `g + h(state)`. Everything else in the loop is shared.
2. **Why is `path_cost_km` recomputed from the returned path?** So the reported cost is independent of
   how each algorithm orders its frontier. BFS, DFS and GBFS do not track g at all, and recomputing from
   the edges actually on the path makes every algorithm's cost directly comparable and verifiable.
3. **What is the counter in the heap tuple for?** It is a tie-breaker. When two entries have the same
   priority, `heapq` compares the next element; the unique, increasing counter settles the tie (FIFO order)
   so the states themselves are never compared, which would fail or be arbitrary for some state types.
4. **Why do tests use a five-state graph, not the airline network?** The correct answer can be worked out
   by hand, so the test proves correctness; it needs no dataset and runs in under a second.
5. **Why is "7 of 10" more informative than the mean cost gap?** A mean can be dominated by one or two
   very bad queries. "7 of 10" shows how *often* GBFS loses, i.e. that suboptimality is the usual case,
   not a rare outlier.
