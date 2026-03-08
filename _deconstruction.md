# Paper Deconstruction

1.  **Paper Identity**:
    *   Title: Andes: Defining and Enhancing Quality-of-Experience in LLM-Based Text Streaming Services
    *   Authors: Jiachen Liu, Zhiyu Wu, Jae-Won Chung, Fan Lai, Myungjin Lee, Mosharaf Chowdhury
    *   Venue: arXiv preprint (2404.16283)
    *   Year: 2024

2.  **Core Contribution**:
    The paper formally defines Quality-of-Experience (QoE) for LLM-based text streaming services, which considers the end-to-end token delivery process. It then proposes Andes, a QoE-aware serving system that enhances user experience by strategically allocating contended GPU resources among multiple requests over time to optimize their QoE. Andes achieves this by managing higher request rates or significantly improving average QoE compared to state-of-the-art LLM serving systems.

3.  **Problem Statement**:
    Existing LLM serving systems prioritize server-side aggregate metrics (e.g., token generation throughput) and often use First-Come-First-Serve (FCFS) scheduling, ignoring individual user experience with streamed text. This leads to poor Quality-of-Experience (QoE) under high or bursty loads, characterized by prolonged Time-To-First-Token (TTFT) for some users and excessively fast token generation for others (exceeding digestion speed). This misalignment necessitates over-provisioning of resources to maintain acceptable user experience, increasing operational costs.

4.  **Key Innovation**:
    *   **Formal QoE Definition**: A novel mathematical definition of QoE for text streaming services that captures the continuous interaction process over time, comparing the actual Token Delivery Timeline (TDT) with an expected TDT, incorporating factors like TTFT and Token Delivery Speed (TDS).
    *   **Andes QoE-Aware Scheduler**: A dynamic priority-based preemptive scheduler that operates at the granularity of tokens. It formulates the scheduling problem as a Knapsack variant, using a greedy packing algorithm to maximize QoE gain by prioritizing urgent requests and preempting those that have received sufficient service, while considering GPU memory constraints and token generation latency.
    *   **Client-Side Token Buffer**: A co-designed client-side component that temporarily buffers excess tokens and displays them to the user at their expected pace, ensuring smooth token delivery and masking server-side scheduling intricacies or network fluctuations.

5.  **Technical Components**:
    *   **Metrics**: Quality-of-Experience (QoE), Token Delivery Timeline (TDT), Time-to-First-Token (TTFT), Token Delivery Speed (TDS), System Capacity, System Throughput, Preemption Frequency, Normalized Latency.
    *   **Algorithms**:
        *   QoE-aware scheduling algorithm (Knapsack variant, specifically Exact K-item Knapsack).
        *   Greedy packing algorithm (Algorithm 1) for approximate, efficient solution.
        *   3D Dynamic Programming solution (Algorithm 2) for optimal, but computationally heavy, solution to Exact K-item Knapsack.
    *   **System Design**:
        *   Andes serving system architecture: User requests with QoE requirements, QoE tracker, waiting queue, running queue, GPU workers, request metadata store (for KV cache during preemption), client-side token buffer.
        *   Preemption mechanisms: Swapping (KV cache GPU-CPU transfer) and recomputation.
    *   **LLMs**: OPT family (13B, 30B, 66B, 175B).
    *   **Serving Systems**: vLLM (baseline), vLLM with Round-Robin (RR) scheduling (baseline).
    *   **Hardware**: NVIDIA A100 GPUs, NVIDIA A40 GPU.

6.  **Evaluation Strategy**:
    *   **Models**: OPT 13B, 30B, 66B, 175B (175B with INT8 quantization).
    *   **Hardware**: NVIDIA A100 GPUs (4x), NVIDIA A40 GPU (single).
    *   **Datasets**: ShareGPT and Multi-Round ShareGPT (derived from ShareGPT for longer conversations).
    *   **Workloads**: Poisson distribution for request arrival rates, Gamma arrival process for bursty workloads. QoE requirements (TTFT=1s, TDS based on reading/speaking speeds from tables).
    *   **Baselines**: vLLM (default FCFS scheduling), vLLM with Round-Robin (RR) scheduling.
    *   **Metrics**: Average QoE (with 0.9 threshold), System Capacity (max request rate at 0.9 QoE), System Throughput, TTFT, TDS, Preemption Frequency, Normalized Latency.
    *   **Analyses**:
        *   End-to-end experiments: Average QoE improvement, server capacity increase, impact on system throughput.
        *   Breakdown analysis: QoE, TTFT, and TDS distributions.
        *   Robustness analysis: Performance on different hardware (A40), bursty arrival patterns, and different QoE traces (voice chat).
        *   Sensitivity analysis: Impact of preemption frequency cap ($P$), prediction timeframe ($\Delta t$), and choice of knapsack solver (greedy vs. DP).

7.  **Negative Knowledge**:
    *   **Preemption Overhead**: Swapping KV cache between GPU and CPU memory, or recomputing it, incurs latency overhead. Frequent preemptions can degrade QoE and throughput.
    *   **Algorithmic Complexity**: The Exact K-item Knapsack problem is weakly NP-Hard, making optimal solutions (like 3D DP) computationally intractable for online, real-time scheduling due to high `M` (memory capacity) and `N` (number of requests).
    *   **Throughput Reduction**: Andes introduces a minor throughput drop (up to 10%) at high request rates due to preemption overhead, though this is compensated by significant QoE and capacity improvements.
    *   **Starvation of Longer Requests**: While improving overall QoE, Andes might slightly starve a small fraction of very long requests, as they consume more resources and take longer to complete.
    *   **Hardware-Specific Improvements**: The magnitude of QoE improvement can vary with hardware. Less powerful GPUs (e.g., A40) show smaller improvements because the gap between actual and expected TDS is narrower, offering fewer opportunities for scheduling optimization.
    *   **Sensitivity to Parameters**: While Andes is robust to `Δt`, the preemption cap `P` requires tuning to balance QoE gains and throughput.

8.  **Layer Mapping**:

    *   **`/logic`**:
        *   `claims.md`: Abstract, Introduction (contributions), Conclusion.
        *   `methodology.md`: Section 3.1 (QoE definition principles), Section 3.2 (Andes overview), Section 4 (QoE-Aware Scheduling problem formulation and solution design), Section 5 (Implementation details).
        *   `assumptions.md`: Implicit assumptions about user behavior (reading/speaking speeds), system environment (GPU memory, continuous batching support).
        *   `limitations.md`: Section 2.4 (Limitations of existing solutions), Section 4.2 (Algorithmic Hardness, Preemption Overhead, Preemption Cap discussion), Section 6.2.3 (Throughput drop), Section 6.3 (Starvation of longer requests), Section 6.4 (A40 smaller improvement).
        *   `definitions.md`: Section 1 (tokens, text streaming services, TDT, TTFT, TDS, expected TDT), Section 2.1 (KV cache), Section 3.1 (QoE principles).
        *   `theorems.md`: Discussion of NP-Hardness of Exact K-item Knapsack.

    *   **`/src`**:
        *   `algorithms/greedy_packing.md`: Algorithm 1.
        *   `algorithms/dynamic_programming.md`: Algorithm 2.
        *   `equations.md`: Equation 1, 2, 4, 5. Also equations from Appendix A (6, 7).
        *   `system_design.md`: Section 3.2 (Andes workflow), Section 5 (Server-Side Scheduler, Client-Side Token Buffer).

    *   **`/trace`**:
        *   `related_work.md`: Section 7 (General Model Serving Systems, LLM Serving Systems, Video Streaming and QoE).
        *   `timeline.md`: Introduction (context of LLM evolution, problem emergence).
        *   `future_work.md`: Implicit in the conclusion and opportunities (e.g., API price tiering, more powerful GPUs).
        *   `comparisons.md`: Section 1 (Figure 1), Section 2.4 (Figure 4), Section 6 (vLLM, RR comparisons throughout results).

    *   **`/evidence`**:
        *   `experiments.md`: Section 6.1 (Experiment Setup), Section 6.2 (End-to-End Experiments), Section 6.3 (Breakdown Analysis), Section 6.4 (Robustness), Section 6.5 (Sensitivity Analysis).
        *   `results.md`: Summarize findings from Section 6.2.1, 6.2.2, 6.2.3, 6.3, 6.4, 6.5. Include key numbers and observations.
        *   `datasets.md`: Section 6.1 (ShareGPT, Multi-Round ShareGPT, their characteristics).
        *   `baselines.md`: Section 6.1 (vLLM FCFS, Round-Robin).
        *   `ablations.md`: Section 6.5 (Sensitivity analysis on P, Delta t, Knapsack solver).
        *   `figures.md`: Descriptions and insights from Figures 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22.