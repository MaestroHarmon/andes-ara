# Dynamic Programming Solution for Exact K-item Knapsack

## Purpose
This algorithm provides an optimal solution to the Exact K-item Knapsack problem, which is a sub-problem within Andes's QoE-aware scheduler (Equation 4). It is presented for theoretical completeness and comparison, though its computational cost makes it impractical for real-time online serving.

## Inputs
*   `N`: Total number of requests.
*   `M`: Total KV cache capacity in GPU memory (number of tokens).
*   `l[N]`: Array of context lengths for each request $i$ (representing memory weight).
*   `q[N]`: Array of QoE gains for each request $i$ (representing item value), calculated as $Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}$.
*   `B`: Target batch size (number of requests to select).

## Outputs
*   `x[N]`: A binary array where `x[i] = 1` if request $i$ is selected to be served, and `0` otherwise.

## Procedure (Algorithm 2)

1.  **Initialize DP Table**: Create a 3D DP table `dp[N+1][B+1][M+1]` initialized with $-\infty$. `dp[i][b][m]` will store the maximum QoE gain achievable by considering the first `i` requests, selecting exactly `b` of them, and using at most `m` memory.
2.  **Initialize Choice Table**: Create a 3D table `choice[N+1][B+1][M+1]` initialized with `0`. This table will store whether request `i` was included (1) or not (0) to achieve the `dp` value, for reconstruction of the solution.
3.  **Base Case**: Set `dp[0][0][0] = 0`. This means with 0 requests, 0 items selected, and 0 memory, the gain is 0.
4.  **Iterate Through Requests**: For each request `i` from `1` to `N`:
    *   **Iterate Through Batch Sizes**: For each batch size `b` from `0` to `min(i, B)`:
        *   **Iterate Through Memory Capacities**: For each memory `m` from `0` to `M`:
            *   **Option 1: Do Not Serve Request `i`**:
                *   If `dp[i-1][b][m]` (value without request `i`) is greater than the current `dp[i][b][m]`, update `dp[i][b][m] = dp[i-1][b][m]` and `choice[i][b][m] = 0`.
            *   **Option 2: Serve Request `i`**:
                *   If `b >= 1` (can select one more item) AND `m >= l[i]` (enough memory for request `i`):
                *   Calculate the gain if request `i` is served: `dp[i-1][b-1][m-l[i]] + q[i]`.
                *   If this gain is greater than the current `dp[i][b][m]`, update `dp[i][b][m]` with this new gain and set `choice[i][b][m] = 1`.
5.  **Find Maximum QoE Gain**: After filling the DP table, find the maximum value in `dp[N][B][:]` (considering all possible memory usages for exactly `B` items from `N` requests). Let this maximum value be `Q_max` and its corresponding memory usage be `m_current`.
6.  **Reconstruct Solution**:
    *   Initialize solution array `x[N+1]` with zeros.
    *   Set `b_current = B`.
    *   Iterate backwards from `i = N` down to `1`:
        *   Set `x[i] = choice[i][b_current][m_current]`.
        *   If `x[i] == 1` (request `i` was served):
            *   Decrement `m_current` by `l[i]`.
            *   Decrement `b_current` by `1`.
7.  **Return Solution**: Return the `x` array (excluding the 0th element).

## Complexity
*   **Time Complexity**: $O(M \cdot N \cdot B)$. In the worst case, $B$ can be $N$, leading to $O(M \cdot N^2)$. This is a pseudo-polynomial time complexity.
*   **Space Complexity**: $O(M \cdot N \cdot B)$ for the DP and choice tables.

## Disadvantages
*   **Computational Intractability**: The high time and space complexity make this solution impractical for real-time online scheduling, especially given typical values of $M$ (thousands) and $N$ (hundreds).
*   **Performance Degradation**: As shown in evaluation (Section 6.5), the substantial computational overhead of this DP solution can delay the inference process and degrade the average QoE, making it less effective than the greedy approach in practice.