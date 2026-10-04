# Graph-Based Customer Discovery Architectural Framework for Payment Systems

**Paper Title:** *From Transactional Data to Organizational Intelligence: A Graph-Based Architectural Framework for Customer Discovery in the Payment Industry*  
**عنوان فارسی:** *از داده تراکنشی تا هوشمندی سازمانی: ارائه چارچوب معماری مبتنی بر گراف برای کشف مشتری در صنعت پرداخت*

---

## 📁 Repository Structure

```text
d:/project/hamta/
│
├── From_Transactional_Data_to_Organizational_Intelligence.doc   # Final Paper Manuscript (.doc - IEEE Format)
├── From_Transactional_Data_to_Organizational_Intelligence.docx  # Final Paper Manuscript (.docx - IEEE Format)
├── PAPER_MANUSCRIPT.md                                         # Complete Paper Manuscript in Academic Markdown
│
├── run_pipeline.py                                             # Master End-to-End Orchestrator
├── create_paper.py                                             # Academic Paper Generator
│
├── src/                                                        # Core Modular Architecture
│   ├── config.py                                               # Hyperparameters, Paths & Configuration
│   ├── data_generator.py                                       # Multi-Agent Payment Transaction Stream Generator
│   ├── graph_builder.py                                        # Heterogeneous & Co-Occurrence Graph Builder
│   ├── graph_models.py                                         # Multi-Head Graph Attention Autoencoder (GAT-GAE)
│   ├── customer_discovery.py                                   # Organizational Intelligence & Persona Engine
│   ├── baselines.py                                            # Classical RFM + K-Means and SVD Baselines
│   └── evaluation.py                                           # Quantitative Benchmark & Figure Generator
│
├── figures/                                                    # 300 DPI Publication-Ready Academic Figures
│   ├── fig1_framework_architecture.png                         # Architectural 4-Tier Blueprint
│   ├── fig2_graph_topology_communities.png                     # Network Topology & Personas
│   ├── fig3_latent_tsne_comparison.png                         # t-SNE: Tabular RFM vs. Proposed GNN Manifold
│   ├── fig4_radar_persona_profiles.png                         # Multidimensional Behavioral Radar Charts
│   └── fig5_benchmark_comparison_bar.png                       # Performance Comparison Bar Chart
│
└── output/                                                     # Output Datasets & Benchmark Tables
    ├── benchmark_results.csv                                   # Quantitative Comparison (NMI, ARI, Silhouette)
    ├── payment_transactions.csv                                # Synthesized Transaction Stream (28,752 records)
    ├── discovered_personas_summary.csv                         # Segment Profiles & Enterprise Value Metrics
    └── discovered_customers.csv                                # Customer Discovery Node Scores & Affluence Index
```

---

## 🚀 Quick Start & Reproducibility

### 1. Requirements
Ensure Python 3.10+ is installed with the required packages:
```bash
pip install torch networkx scikit-learn scipy pandas numpy matplotlib python-docx
```

### 2. Run Complete Pipeline
Executes data generation, graph modeling, GAT-GAE neural training, customer persona extraction, baseline comparison, and renders all 5 figures:
```bash
python run_pipeline.py
```

### 3. Generate Research Paper Document (.docx / .doc)
Generates the IEEE-formatted research paper with all embedded figures and tables:
```bash
python create_paper.py
```
