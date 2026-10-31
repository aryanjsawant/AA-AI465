| Method | Accuracy % (mean ± std) | Samples | Rounds | Prompt tok | Completion tok | Total tok | Latency s |
|---|---|---|---|---|---|---|---|
| CoT greedy (T=0) | 58.0 | 1.00 | 1.00 | 420 | 90 | 510 | 6.5 |
| SC-1 | 52.0 ± 2.0 | 1.00 | 1.00 | 420 | 93 | 512 | 4.0 ± 0.5 |
| SC-5 | 62.7 ± 3.1 | 5.00 | 1.00 | 420 | 466 | 885 | 19.8 ± 2.4 |
| SC-10 | 64.7 ± 6.4 | 10.00 | 1.00 | 420 | 918 | 1338 | 38.4 ± 3.7 |
| SC-15 | 67.3 ± 5.0 | 15.00 | 1.00 | 420 | 1376 | 1795 | 56.6 ± 4.9 |
| SC-16 | 68.0 ± 4.0 | 16.00 | 1.00 | 420 | 1467 | 1886 | 60.2 ± 4.8 |
| SC-20 | 67.3 ± 3.1 | 20.00 | 1.00 | 420 | 1836 | 2256 | 74.6 ± 4.7 |
| ESC (w=5, L=20) | 67.3 ± 3.1 | 15.30 | 3.06 | 1295 | 1487 | 2782 | 60.7 ± 5.3 |
| AC (Beta 0.95, L=20) | 67.3 ± 3.1 | 12.71 | 12.71 | 5391 | 1257 | 6648 | 52.0 ± 5.9 |
| Random stopping (ablation) | 65.9 ± 3.4 | 15.30 | 3.06 | 1295 |  |  |  |

Paired accuracy differences (percentage points, mean ± std over runs):

- ESC - SC-15 (matched, floor): +0.00 ± 2.00
- ESC - SC-16 (matched, ceil): -0.67 ± 1.15
- ESC - SC-20 (full budget): +0.00 ± 0.00
- ESC - random stopping: +1.39 ± 0.64
