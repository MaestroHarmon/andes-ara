---
type: "experiment"
id: "qoe_improvement_experiment"
validates:
  - claims/qoe_improvement.md
  - claims/server_capacity_increase.md
config:
  models: OPT family (13B, 30B, 66B, 175B parameters)
  hardware: NVIDIA A100 GPUs (80GB)
  datasets: ShareGPT, Multi-Round ShareGPT
  preemption_cap: 1
  qoe_threshold: 0.9
---

This experiment evaluates the QoE improvement achieved by Andes compared to baselines like vLLM and Round-Robin scheduling. The experiment uses the OPT model family, NVIDIA A100 GPUs, and the ShareGPT dataset.

Key metrics measured:

*   Average QoE
*   Server capacity (request rate at a given QoE)
*   Throughput
*   Preemption frequency
*   TTFT

The results demonstrate that Andes achieves a significant QoE improvement (up to 3.2x) and increases server capacity (1.2x-1.6x) compared to the baselines. For example, with the OPT-66B model and ShareGPT dataset at a request rate of 3.3, Andes improved the 10th percentile QoE from 0.05 (vLLM) to 0.77 and the median TTFT from 56.73s (vLLM) to 0.47s.