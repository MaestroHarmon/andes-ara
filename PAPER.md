---
title: Andes: Defining and Enhancing Quality-of-Experience in LLM-Based Text Streaming Services
authors: Jiachen Liu, Jae-Won Chung, Zhiyu Wu, Fan Lai, Myungjin Lee, Mosharaf Chowdhury
venue: arXiv (cs.DC, cs.LG)
year: 2024
ara_version: "3.0"
primary_contribution: Andes introduces a QoE-aware LLM serving system that improves user experience in text streaming by dynamically prioritizing requests based on expected QoE gain and resource usage.
---

This paper introduces [Andes](./concepts/andes.md), a novel system for enhancing Quality-of-Experience (QoE) in LLM-based text streaming services. The core idea revolves around optimizing the [Token Delivery Timeline (TDT)](./concepts/token_delivery_timeline.md) to align with user expectations.

The paper defines a [QoE metric](./concepts/qoe_metric.md) to quantify user satisfaction based on the actual vs. expected TDT. Andes then utilizes a [preemptive request scheduler](./src/scheduler.py) to dynamically prioritize requests based on their expected QoE gain and resource usage, leading to improved [QoE](./claims/qoe_improvement.md) and reduced resource consumption. The system also incorporates a [client-side token buffer](./src/token_buffer.py) for smooth token delivery.

The paper validates its claims through [experiments](./experiments/qoe_improvement_experiment.md) using various LLMs and datasets, demonstrating significant improvements over existing systems like vLLM. The [scheduling algorithm](./src/scheduler.py) and its optimizations are key to the system's performance.

Key findings include the [QoE improvement](./claims/qoe_improvement.md) and [server capacity increase](./claims/server_capacity_increase.md) compared to baselines like vLLM and Round-Robin scheduling. Limitations and negative knowledge are discussed in [graveyard](./temporal/graveyard.md). The [decision making process](./temporal/decisions.md) describes key architectural choices.