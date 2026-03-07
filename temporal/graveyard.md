---
type: "temporal"
id: "graveyard"
---

This file documents approaches that were explored but ultimately did not work well.

*   **Very small batch sizes:** Using very small batch sizes did not help improve QoE, as the token delivery speed became faster than any reasonable user digest speed.

*   **Very large batch sizes:**  Using very large batch sizes hurt performance because the requests could not fit into the GPU memory, leading to increased preemption or even out-of-memory errors.

*   **Dynamic Programming (DP) scheduling solution:** The DP solution for the knapsack problem was too slow (O(M*N²)), where M is memory and N is the number of requests. The greedy packing algorithm provided comparable results with a much lower time complexity (O(N log N)).

*   **Unlimited preemptions:** Allowing unlimited preemptions for a request led to excessive overhead, as each preemption incurs a cost of approximately one token generation iteration.