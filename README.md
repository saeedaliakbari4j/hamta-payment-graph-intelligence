# Hamta (همتا)

**Peer-graph intelligence for payment networks and customer discovery.**

*همتا* means "peer / counterpart" in Persian — the core idea of the project: uncovering organizational intelligence and behavioral patterns in payment transaction networks through bipartite graph modeling, higher-order curvature analysis, and deep graph neural representations.

> **Persian Title:** از داده‌های خام تراکنشی تا هوشمندی سازمانی: بازنمایی گراف دوبخشی و خوشه‌بندی رفتاری کارت‌های پرداخت با اتوانکودر عصبی مبتنی بر انحنا (HG-CAN)  
> **English Paper Title:** *From Transactional Data to Organizational Intelligence: A Graph-Based Architectural Framework for Customer Discovery in the Payment Industry*  
> **Target Venue:** ICAEA 2026 (10th Iranian Conference on Advances in Enterprise Architecture) — Track 5: Data Analytics, BI, and Decision Support.

---

## 📁 Repository Structure

```text
hamta/
│
├── docs/                                                        # Project Research, Proposals & Conference Docs
│   ├── proposal.md                                              # Original Hamta Project Proposal (Persian)
│   ├── research.md                                              # State-of-the-art Technology & Literature Review
│   ├── roadmap.md                                               # Phased Plan & Publication Path
│   └── conference/                                              # ICAEA 2026 Notes, Templates & AI Policy
│       └── files/                                               # Official Conference Forms & Word Templates
│
├── FA_From_Transactional_Data_to_Organizational_Intelligence.pdf # Final Persian Conference Paper (5 pages)
├── FA_From_Transactional_Data_to_Organizational_Intelligence.docx# Final Persian Paper (.docx)
├── FA_From_Transactional_Data_to_Organizational_Intelligence.doc # Final Persian Paper (.doc)
├── From_Transactional_Data_to_Organizational_Intelligence.pdf    # English IEEE Format Paper (5 pages)
├── From_Transactional_Data_to_Organizational_Intelligence.docx   # English Paper (.docx)
├── راهنمای_جامع_کدها_و_معماری_پروژه.pdf                       # Comprehensive Architecture & Code Guide (11 pages)
│
├── run_pipeline.py                                              # Master End-to-End Orchestrator
├── create_paper_fa.py                                           # Persian Academic Paper Generator
├── create_paper.py                                              # English Academic Paper Generator
├── create_project_docs.py                                       # Comprehensive PDF Technical Docs Generator
│
├── src/                                                         # Core Modular Architecture
│   ├── config.py                                                # Hyperparameters, Paths & Configuration
│   ├── data_generator.py                                        # Multi-Agent Payment Transaction Stream Generator
│   ├── graph_builder.py                                         # Heterogeneous & Co-Occurrence Graph Builder
│   ├── graph_models.py                                          # Multi-Head Graph Attention Autoencoder
│   ├── customer_discovery.py                                    # Organizational Intelligence & Persona Engine
│   ├── baselines.py                                             # Classical RFM + K-Means and SVD Baselines
│   └── evaluation.py                                            # Quantitative Benchmark & Figure Generator
│   └── models/                                                  # Advanced Curvature GNN Modules
│       └── curvature_gnn.py                                     # Forman-Ricci Higher-Order Attention GNN
│
├── figures/                                                     # 300 DPI Publication-Ready Academic Figures
│   ├── fig1_framework_architecture.png                          # Architectural 4-Tier Blueprint
│   ├── fig2_graph_topology_communities.png                      # Network Topology & Personas
│   ├── fig3_latent_tsne_comparison.png                          # t-SNE: Tabular RFM vs. Proposed HG-CAN Manifold
│   ├── fig4_radar_persona_profiles.png                          # Multidimensional Behavioral Radar Charts
│   └── fig5_benchmark_comparison_bar.png                        # Performance Comparison Bar Chart
│
└── output/                                                      # Output Datasets & Benchmark Tables
    ├── benchmark_results.csv                                    # Quantitative Comparison (NMI, ARI, Silhouette)
    ├── payment_transactions.csv                                 # Synthesized Transaction Stream (35,000 records)
    ├── discovered_personas_summary.csv                          # Segment Profiles & Enterprise Value Metrics
    └── discovered_customers.csv                                 # Customer Discovery Node Scores & Affluence Index
```

---

## 🚀 Quick Start & Reproducibility

### 1. Requirements
Ensure Python 3.10+ is installed with the required packages:
```bash
pip install torch networkx scikit-learn scipy pandas numpy matplotlib python-docx reportlab
```

### 2. Run Complete Pipeline
Executes data generation, graph modeling, HG-CAN neural training, customer persona extraction, baseline comparison, and renders all 5 figures:
```bash
python run_pipeline.py
```

### 3. Generate Research Papers
- Persian Paper (ICAEA format):
  ```bash
  python create_paper_fa.py
  ```
- English Paper (IEEE format):
  ```bash
  python create_paper.py
  ```
- Comprehensive Technical Manual:
  ```bash
  python create_project_docs.py
  ```

---

## 🔒 Data Policy
No real transaction data is ever committed to this repository. All experiments use synthetic transactions with realistic statistical distributions.
