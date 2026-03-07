---
type: "claim"
id: "qoe_improvement"
falsifiable: true
relies_on:
  - concepts/qoe_metric.md
  - concepts/token_delivery_timeline.md
supported_by:
  - experiments/qoe_improvement_experiment.md
---

Andes significantly improves the average Quality-of-Experience (QoE) compared to state-of-the-art LLM serving systems, achieving up to 3.2x improvement given the same GPU resources. This improvement stems from the QoE-aware scheduling and client-side token buffering mechanisms. The [experiment](./experiments/qoe_improvement_experiment.md) demonstrates a significant boost in both 10th and 50th percentile QoE scores.