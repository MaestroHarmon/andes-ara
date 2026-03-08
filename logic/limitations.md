# Limitations

## 1. Algorithmic Hardness and Approximation (Section 4.2)
*   The core scheduling problem is formulated as an Exact K-item Knapsack problem, which is weakly NP-Hard. An optimal solution using 3D dynamic programming has a pseudo-polynomial time complexity of $O(M \cdot N^2)$, making it too slow for online, real-time serving where $M$ (memory capacity) and $N$ (number of requests) can be large.
*   Andes relies on a greedy packing algorithm, which provides an approximate solution. While empirically shown to be effective, it is not guaranteed to be globally optimal.

## 2. Preemption Overhead (Section 4.2, 6.2.3)
*   Preemption (swapping KV cache to CPU or recomputing it) is not free and incurs latency overhead. Frequent preemptions can slow down token generation and delay token delivery, potentially degrading request throughput and QoE.
*   Andes introduces a minor drop in system throughput ($\leq 10\%$) at high request rates due to these overheads.
*   The effectiveness of preemption depends on the specific hardware and system configuration (e.g., NVLink connectivity affects recomputation overhead).

## 3. Potential for Starvation of Longer Requests (Section 6.3)
*   While Andes significantly improves QoE for most requests, especially shorter ones, it might slightly starve a small fraction of longer requests. This is because longer requests consume more resources (larger $l_i$) and take longer to complete, which can lead to them being deprioritized by the greedy algorithm to free up memory for multiple shorter, higher-priority requests.

## 4. Hardware-Specific Performance (Section 6.4)
*   The magnitude of QoE improvement and server capacity increase can be dependent on the computational capability of the underlying GPU hardware. For instance, on an NVIDIA A40 GPU (lower computational capability than A100), the improvement in server capacity was smaller ($1.1\times$ vs. $1.6\times$). This is because a slower average token generation speed on less powerful GPUs reduces the "slack" between expected and actual TDS, limiting opportunities for scheduling optimization.

## 5. Scope of QoE Definition (Section 3.1)
*   The default QoE definition focuses on the relative relationship between actual and expected token delivery. While it can be extended with penalizing terms (e.g., for TTFT), the paper primarily uses the default. Different applications might require more complex or nuanced QoE models that are not fully explored.

## 6. Sensitivity to Parameters (Section 6.5)
*   The preemption frequency cap $P$ requires tuning to find a balance between QoE enhancement and throughput degradation. While $P=1$ is suggested as a good default, optimal values might vary with workloads and system configurations.
*   The prediction timeframe $\Delta t$ is shown to be robust for values greater than 50, but its impact for very short $\Delta t$ (leading to shortsighted decisions) or very long $\Delta t$ (leading to state deviation) is acknowledged.

## 7. External Factors (Section 5)
*   Andes's server-side scheduler focuses on managing requests within a single LLM instance. Cluster-level load balancing and fault tolerance are assumed to be handled separately.
*   The client-side token buffer, while crucial, requires appropriate implementation depending on the client environment (e.g., TypeScript for web, Python for API).