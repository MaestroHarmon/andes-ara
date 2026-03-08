# Greedy Packing Algorithm for QoE-Aware Scheduling

## Purpose
This algorithm provides an efficient, approximate solution to the Exact K-item Knapsack problem formulated in Andes's QoE-aware scheduler (Equation 4). It aims to select a batch of requests to serve that maximizes QoE gain while respecting GPU memory and batch size constraints, with low computational overhead suitable for online serving.

## Inputs
*   `N`: Total number of requests (queued or running).
*   `M`: Total KV cache capacity in GPU memory (number of tokens).
*   `l[N]`: Array of context lengths for each request $i$ (representing memory weight).
*   `q[N]`: Array of QoE gains for each request $i$ (representing item value), calculated as $Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}$.
*   `B`: Target batch size (number of requests to select).

## Outputs
*   `x[N]`: A binary array where `x[i] = 1` if request $i$ is selected to be served, and `0` otherwise.

## Procedure (Algorithm 1)

1.  **Initialize Priority Array**: Create an array `p[N]` to store priorities, initialized to zeros.
2.  **Calculate Priorities**: For each request `i` from `0` to `N-1`:
    *   Calculate priority `p[i]` as the ratio of QoE gain to context length:
        $$
        p[i] = \frac{q[i]}{l[i]}
        $$
    *   This priority function aims to:
        *   **Reflect merit**: Prioritize requests with high QoE gain per unit of GPU memory.
        *   **Prevent starvation**: As a request receives service, its context length `l[i]` increases, automatically decreasing its priority. Conversely, waiting increases `q[i]`, boosting priority.
        *   **Reduce preemption**: Requests with longer context lengths (larger `l[i]`) will have lower priority, making them candidates for preemption to free up more memory for potentially multiple smaller requests.
3.  **Initialize State**:
    *   `M_current = 0`: Current total memory occupied by selected requests.
    *   `N_current = 0`: Current number of selected requests.
    *   `x[N]`: Solution array, initialized to all zeros.
4.  **Greedy Packing**: Iterate through all requests `i` in descending order of their calculated priority `p[i]`.
    *   **Check Constraints**: For each request `i`, if:
        *   Adding `l[i]` to `M_current` does not exceed total memory capacity `M` (`M_current + l[i] <= M`), AND
        *   Adding 1 to `N_current` does not exceed the target batch size `B` (`N_current + 1 <= B`),
    *   **Select Request**: Then, select request `i`:
        *   Set `x[i] = 1`.
        *   Update `M_current = M_current + l[i]`.
        *   Update `N_current = N_current + 1`.
    *   **Stop**: If a request cannot be added (either memory or batch size constraint is violated), break the loop. (This implies that requests are sorted by priority, so subsequent requests will also likely not fit or be less optimal).
5.  **Return Solution**: Return the `x` array.

## Complexity
*   **Time Complexity**: $O(N \log N)$, primarily due to sorting the requests by priority. This is significantly more efficient than the $O(M \cdot N^2)$ dynamic programming solution.
*   **Space Complexity**: $O(N)$ for storing priority and solution arrays.

## Advantages
*   **Efficiency**: Fast enough for online, real-time scheduling decisions.
*   **Effectiveness**: Empirically shown to achieve performance comparable to the optimal DP solution while greatly reducing scheduling overhead (Section 6.5).
*   **QoE-Awareness**: Directly incorporates QoE gain and resource consumption into its priority metric.