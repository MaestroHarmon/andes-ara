---
type: "claim"
id: "server_capacity_increase"
falsifiable: true
relies_on:
  - concepts/andes.md
  - concepts/qoe_metric.md
supported_by:
  - experiments/qoe_improvement_experiment.md
---

Andes can serve 1.2x-1.6x higher request rate while maintaining the same high Quality-of-Experience (QoE) compared to existing LLM serving systems. This demonstrates Andes's ability to utilize GPU resources more efficiently by prioritizing requests that contribute most to the overall QoE.