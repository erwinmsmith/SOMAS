# Human-Machine Collaborative Crisis Response Framework (HMC-CRF)
A reinforcement learning-based framework for trusted multi-agent collaboration in emergency management scenarios.

---

## 📖 Introduction
This repository implements a **Multi-Agent System (MAS)** framework for human-machine collaborative crisis response, combining **vision-language models (VL)** and **reinforcement learning (RL)** to enhance safety and reliability. The framework features:
- **Real-Time Task Execution**: Modular task chains with built-in safety rules and human oversight.
- **Simulation Training**: Experience replay library for risk prediction and optimization.
- **Dynamic Trust Mechanism**: Balances task utility and safety constraints through RL.

**Key Contributions**:
1. Dual-mode architecture (online execution + offline simulation).
2. First fine-tuned safe LLM and training dataset for emergency scenarios.
3. 15% improvement in helpfulness and 40% reduction in risk response rate compared to baseline.

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/yourusername/HMC-CRF.git
cd HMC-CRF
pip install -r requirements.txt
```

### Usage
1. **Real-Time Task Execution**:
```python
from hmc_crf import RealTimeSystem
system = RealTimeSystem(safety_rules="config/safety_rules.yaml")
system.execute_task("task_chain.json")
```

2. **Simulation Training**:
```python
from hmc_crf import SimulationSystem
simulator = SimulationSystem(dataset="data/sim_tasks.json")
simulator.train(epochs=10, batch_size=32)
```

---

## 🧠 Framework Architecture
![](media/architecture.png)

### Core Components
1. **Online Execution System**  
   - **Planning-Execution Pipeline**: Modular task chains drive tool operations.  
   - **Safety Guardrails**: Predefined rules and GPT-4-based risk assessment.  

2. **Offline Simulation System**  
   - **Task Generation**: Synthetic tasks from manual records and prior knowledge.  
   - **Experience Replay**: Optimizes RL policies for dynamic environments.  

---

## 📊 Experimental Results

### Key Metrics
| Domain      | Model              | Safety (↑) | Helpfulness (↑) | Risk Response Rate (↓) |
|-------------|--------------------|------------|-----------------|-------------------------|
| Safety-CV   | Qwen2-7B-VL (Ours) | **4.5**    | **4.7**         | **40%** (Baseline: 100%) |
| Medicine    | Llama3.2-11B-VL    | 3.7        | 4.0             | 55%                     |

### Highlights
- **VL models** reduced operational risks by **30%** via image semantic parsing.  
- **Dynamic safety validation** improved helpfulness by **15%** over ToolEmu.  

[View full results](experiments/README.md)

---

## 🛠️ Limitations & Future Work
- **Limitations**:  
  - Simplified experimental environments.  
  - Dependency on predefined safety rules.  

- **Future Directions**:  
  - Extend to real-world dynamic scenarios.  
  - Integrate adaptive risk assessment modules.  

---

## 📜 Citation
```bibtex
@article{duan2024hmccrf,
  title={A Framework of Human-Machine Collaborative Crisis Response Based on Multi-agent System},
  author={Duan, Zhenke and Tu, Jiani and Wu, Fan and Yi, Qingfeng and Yu, Liangtao},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2024}
}
```

---

## 📞 Contact
For questions or collaborations, contact:  
- **Zhenke Duan**: zhenke.duan@example.com  
- **Qingfeng Yi (Corresponding Author)**: qingfeng.yi@example.com  

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
``` 

### Notes:
1. Replace placeholder links (e.g., `https://example.com/paper.pdf`, `media/architecture.png`) with actual resources.
2. Add detailed installation steps and example files (e.g., `task_chain.json`, `safety_rules.yaml`) to the repository.
3. Include supplementary materials (e.g., dataset samples, training scripts) in subdirectories.
