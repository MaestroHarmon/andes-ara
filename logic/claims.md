# Core Claims

## Primary Contribution
This paper formally defines Quality-of-Experience (QoE) for LLM-based text streaming services, considering the end-to-end token delivery process throughout the entire user interaction. Based on this definition, it proposes Andes, a QoE-aware serving system that strategically allocates contended GPU resources among multiple requests over time to optimize their QoE.

## Supporting Claims
1.  **QoE Definition**: A formal mathematical definition of QoE for text streaming services is proposed, comparing actual and expected Token Delivery Timelines (TDT) to reflect user experience throughout the entire interaction (Section 3.1).
2.  **Andes System Design**: Andes employs a dynamic priority-based preemptive scheduler operating at token granularity, which strategically allocates system resources to more urgent requests and preempts requests that have already received sufficient service to enhance QoE (Section 4).
3.  **Client-Side Token Buffer**: Andes co-designs a client-side token buffer that temporarily withholds excess tokens and displays them to the user at their expected pace, ensuring smooth token delivery oblivious to server-side scheduling or network fluctuations (Section 5).
4.  **Performance Improvement (Average QoE)**: Andes improves the average QoE by up to $3.2\times$ under high and/or bursty request rates compared to state-of-the-art LLM serving systems like vLLM (Section 6.2.1).
5.  **Performance Improvement (System Capacity)**: Andes attains up to $1.6\times$ higher request rate while preserving high QoE (average QoE $\geq 0.9$) without requiring additional resources, thereby reducing the cost per request (Section 6.2.2).
6.  **Minimal Throughput Impact**: Andes maintains similar token generation throughput as baselines, with only a minor drop ($\leq 10\%$) at increased request rates, demonstrating negligible system overhead (Section 6.2.3).
7.  **Improved Responsiveness**: Andes significantly improves Time-To-First-Token (TTFT) while maintaining Token Delivery Speed (TDS) above user-expected speeds (Section 6.3).
8.  **Robustness**: Andes demonstrates robustness across diverse workloads, including different hardware, bursty arrival patterns, and varying QoE traces (Section 6.4).
9.  **Efficiency of Greedy Solution**: The proposed greedy packing algorithm for the knapsack problem is shown to be efficient and effective, outperforming a computationally heavier dynamic programming solution in practice (Section 6.5).

## Novelty Claims
-   Identification of text streaming services as an emerging category of LLM-based applications with unique QoE challenges.
-   First formal definition of QoE specifically for LLM-based text streaming services.
-   First LLM serving system (Andes) designed to optimize this newly defined QoE metric.
-   Co-design of a client-side token buffer to complement server-side QoE-aware scheduling.