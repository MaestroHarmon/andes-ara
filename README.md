# Andes ARA (Agent-Native Research Artifact)

This repository contains the ARA (Agent-Native Research Artifact) extraction of the **Andes** paper:

> **Andes: Defining and Enhancing Quality-of-Experience in LLM-Based Text Streaming Services**
> 
> ArXiv: [2404.16283](https://arxiv.org/abs/2404.16283)

## What is an ARA?

An ARA is a structured filesystem representation of a research paper that strips away the "storytelling tax" of academic writing and isolates:
- **Core logic** (cognitive layer)
- **Executable components** (physical layer)
- **Temporal context** (trace layer)
- **Supporting evidence** (evidence layer)

## Repository Structure

```
├── logic/                    # Cognitive Layer
│   ├── claims.md            # Core claims and contributions
│   ├── methodology.md       # Research approach
│   ├── definitions.md       # Key terms (QoE, TTFT, TDS, etc.)
│   ├── assumptions.md       # System assumptions
│   └── limitations.md       # Known limitations
├── src/                      # Physical Layer
│   ├── algorithms/
│   │   ├── greedy_packing.md    # O(N log N) scheduling algorithm
│   │   └── dynamic_programming.md
│   ├── equations.md         # Mathematical formulations
│   └── system_design.md     # Andes architecture
├── _deconstruction.md       # Chain-of-thought analysis
├── ara_system_prompt.txt    # ARA extraction prompt
├── ingest.py                # Thin client ingestor
└── report.md                # Implementation report
```

## Key Extracted Knowledge

### QoE Metric (from `/logic/definitions.md`)
Quality-of-Experience (QoE) quantifies user satisfaction by comparing actual vs. expected Token Delivery Timelines.

### Scheduling Algorithm (from `/src/algorithms/greedy_packing.md`)
Priority function: `p[i] = QoE_gain[i] / context_length[i]`
- Time complexity: O(N log N)
- Maximizes QoE gain per unit GPU memory

## How This Was Generated

This ARA was generated using the "Fat Prompt, Thin Client" architecture:
1. **Fat Prompt**: Comprehensive system prompt defining ARA schema
2. **Thin Client**: Simple Python script that fetches paper and calls LLM

```bash
python ingest.py 2404.16283 --output_dir andes_ara_output
```

## License

The original paper is by Liu et al. (2024). This ARA extraction is provided for research purposes.
