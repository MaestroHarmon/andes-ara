# Methodology

## 1. Quality-of-Experience (QoE) Definition for Text Streaming Services (Section 3.1)

The methodology begins by formally defining QoE for text streaming services, which deliver tokens incrementally and interactively. This definition is guided by three principles:

1.  **Perfect Satisfaction**: Users are maximally satisfied (QoE = 1, normalized to $[0, 1]$) when actual token delivery perfectly aligns with or exceeds the expected delivery.
2.  **Excess Token Delivery**: Delivering tokens faster than the user's digestion speed does not add value to QoE; QoE remains unchanged.
3.  **Early Token Delivery**: Users prefer receiving more tokens earlier. QoE is higher for scenarios where more tokens are delivered earlier, e.g., shorter TTFT or faster TDS.

The QoE metric is formalized by comparing two curves:
*   **Expected Token Delivery Curve $T(t)$**: Defined by expected TTFT and TDS, representing the ideal timeline for token delivery. $T(t) = TDS_{\textrm{expected}} \cdot (t - TTFT_{\textrm{expected}})$.
*   **Actual Token Delivery Curve $A(t)$**: Reflects how tokens are digested by the user over time, with its slope capped by the expected TDS.

The QoE of a request with response length $l$ is quantified as the ratio of the actual and expected areas under these curves up to the actual time to the last token (TTLT):

$$
QoE=\frac{S_{\textrm{actual}}}{S_{\textrm{expected}}}=\frac{\int_{0}^{TTLT}A(t)dt}{\int_{0}^{TTLT}\min(T(t),l)dt}
$$

This formulation can be extended with a penalizing term for TTFT, e.g., $\alpha^{TTFT_{\textrm{actual}}-TTFT_{\textrm{expected}}} \cdot \frac{S_{\textrm{actual}}}{S_{\textrm{expected}}}$, where $\alpha \in [0,1]$, to stress shorter TTFT.

## 2. Andes System Overview (Section 3.2)

Andes is an LLM serving system designed to optimize overall QoE. Its workflow involves:
1.  **Request Submission**: User submits a request with pre-specified QoE requirements.
2.  **Priority Assignment**: QoE tracker assigns an initial scheduling priority and places the request in a waiting queue.
3.  **Dynamic Rescheduling**: At each scheduling iteration, the QoE tracker refreshes priorities for all requests (waiting and running). Andes then reschedules by admitting high-priority waiting requests to GPU workers and evicting low-priority running requests. Evicted requests' states (e.g., KV cache) are stored in CPU RAM.
4.  **Token Generation**: Running requests generate one token per inference iteration, which is sent to the client.
5.  **Client-Side Buffering**: A client-side token buffer stores excess tokens and displays them at the user's expected speed, ensuring smooth delivery.

## 3. QoE-Aware Scheduling (Section 4)

The core of Andes is an online preemptive scheduling algorithm for token generation, involving:

### 3.1. Problem Formulation (Section 4.1)
The scheduling problem is formulated as a variant of the Knapsack problem.

*   **Time Quantum**: Scheduling decisions are made at the beginning of each inference iteration, similar to continuous batching.
*   **Scheduling Objective**: Maximize QoE gain in an upcoming timeframe $\Delta t$. The objective function for request $i$ is:
    $$
    Q_{\textrm{serve},i}-Q_{\textrm{wait},i}
    $$
    where $Q_{\textrm{serve},i}$ is the QoE if served, and $Q_{\textrm{wait},i}$ is the QoE if not served. This represents the QoE gain from serving a request.
*   **Batch Size Constraints**:
    1.  **GPU Memory**: Total context length of served requests must not exceed GPU memory capacity $M$:
        $$
        \sum_{i=1}^{N}l_{i}x_{i}\leq M
        $$
        where $l_i$ is request $i$'s context length, $x_i$ is an indicator (1 if served, 0 otherwise), and $N$ is total requests.
    2.  **Batch Size Impact on Latency**: Token generation latency depends on batch size $B$, which in turn affects $Q_{\textrm{serve},i}$.
    3.  **Exact K-item Knapsack**: The problem is to select exactly $B$ requests to maximize total QoE gain, subject to memory constraints.
        $$
        \max_{x} \sum_{i=1}^{N}\left(Q_{\text{serve},i}(B)-Q_{\text{wait},i}\right)\cdot x_{i}
        $$
        $$
        \text{s.t. } x_{i}\in\{0,1\},~{}i\in 1,\ldots,N
        $$
        $$
        \sum_{i=1}^{N}x_{i}=B
        $$
        $$
        \sum_{i=1}^{N}l_{i}x_{i}\leq M
        $$
        This problem is solved for each possible batch size $B$ to find the optimal one.

### 3.2. Solution Design (Section 4.2)

To address the algorithmic hardness (Exact K-item Knapsack is weakly NP-Hard, $O(M \cdot N^2)$ DP solution is too slow) and preemption overhead, Andes employs several optimizations:

*   **Optimization #1: Selective Triggering**: The optimization problem is only solved when batch size is limited by memory capacity (high-memory watermark, e.g., 90%) or computation time (token generation latency exceeds stringent TDS requirement). Otherwise, all requests are served.
*   **Optimization #2: Batch Size Search Space Pruning**: The search space for batch size $B$ is reduced from $[1, N]$ to $[B_{\min}, B_{\max}]$.
    *   $B_{\max}$ is determined by packing shortest requests until memory $M$ is full.
    *   $B_{\min}$ is the largest batch size that generates tokens faster than the most stringent TDS requirement.
*   **Optimization #3: Greedy Packing Algorithm (Algorithm 1)**: An efficient greedy algorithm is used instead of DP. It computes a priority for each request $i$:
    $$
    \frac{Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}}{l_{i}}
    $$
    This priority function aims to:
    *   **Reflect merit**: High QoE gain, low resource consumption.
    *   **Prevent starvation**: Context length $l_i$ increases with service, deprioritizing the request. Waiting increases QoE gain, boosting priority.
    *   **Reduce preemption**: Prioritizes preempting long requests to free up more memory for potentially multiple new requests.
    The algorithm sorts requests by this priority in descending order and greedily packs them until memory or target batch size is reached. Time complexity: $O(N \log N)$.
*   **Optimization #4: Preemption Cap**: To prevent thrashing, Andes supports a cap $P$ on the average number of preemptions a request can experience. A default of $P=1$ is found to be effective.

## 4. Implementation Details (Section 5)

*   **Server-Side QoE-Aware Scheduler**: Implemented on top of vLLM, leveraging its continuous batching and preemption mechanisms (swapping KV cache between GPU and CPU memory, or recomputation).
*   **Client-Side Token Buffer**: Designed to smooth token delivery at the user's expected TDS, absorbing server-side fluctuations and network latency. It holds excess tokens and drains them at the user's pace.

## 5. Alternative Scheduling Objectives (Appendix A)

Andes's framework is adaptable to different QoE objectives:
*   **Maximizing Minimum QoE**: The gain for request $i$ is $\max(Q_{\min}-Q_{\textrm{wait},i},0)$, prioritizing requests that would degrade the minimum QoE.
*   **Maximizing Number of Requests with Perfect QoE**: The gain for request $i$ is $[\mathbb{1}(Q_{\textrm{serve, i}}=1)-\mathbb{1}(Q_{\textrm{wait, i}}=1)]\cdot\mathbb{1}(Q_{\textrm{current},i}=1)$, prioritizing requests that are currently perfect but would degrade if not served.

## 6. Modeling Token Generation Latency (Appendix B)

Token generation latency is modeled as a function of batch size $B$. Empirical data shows a strong correlation (Pearson 0.997) between batch size and total context length, allowing simplification to batch size alone.