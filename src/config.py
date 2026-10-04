"""
Configuration Module for Higher-Order Hypergraph Payment Intelligence Framework
Paper: "From Transactional Data to Organizational Intelligence:
        A Higher-Order Hypergraph Curvature Framework for Customer Discovery in the Payment Industry"

Data Schema Fields:
- pan: Primary Account Number (Masked Card Token, e.g. 603799******1234)
- amount: Transaction Monetary Value (in currency units / Rials)
- merchant_id: Merchant Terminal Identifier (e.g. MERCH_00342)
- create_date: Transaction Timestamp (ISO DateTime)
- cast_name: Merchant Business Guild (صنف پذیرنده مانند طلافروشی)
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Config:
    # Reproducibility
    SEED: int = 42

    # Data Synthesis Parameters
    NUM_CARDS: int = 1500          # Unique card tokens (pan)
    NUM_MERCHANTS: int = 350       # Unique merchant terminals (merchant_id)
    NUM_TRANSACTIONS: int = 35000  # Total payment transactions
    SIMULATION_DAYS: int = 90      # Simulation time horizon

    # Business Guilds / Categories (cast_name)
    CAST_NAMES: List[str] = field(default_factory=lambda: [
        "طلافروشی",                       # Gold & Jewelry (High ticket, capital preservation)
        "سوپرمارکت و خواروبار",             # Supermarket & Groceries (High frequency, daily retail)
        "رستوران و فست‌فود",               # Restaurants & Dining
        "لوازم الکترونیک و موبایل",          # Electronics & Mobile Tech
        "آژانس مسافرتی و گردشگری",           # Travel Agencies & Tourism
        "خدمات پزشکی و داروخانه",           # Medical & Healthcare Clinics
        "پوشاک و کیف و کفش",               # Apparel & Fashion Retail
        "آهن‌آلات و مصالح صنعتی"             # B2B Wholesalers & Industrial Construction
    ])

    # Mapping of cast_name to English academic labels
    CAST_TRANSLATIONS: Dict[str, str] = field(default_factory=lambda: {
        "طلافروشی": "Gold & Jewelry Stores",
        "سوپرمارکت و خواروبار": "Supermarkets & Groceries",
        "رستوران و فست‌فود": "Restaurants & Dining",
        "لوازم الکترونیک و موبایل": "Electronics & Mobile Tech",
        "آژانس مسافرتی و گردشگری": "Travel Agencies & Tourism",
        "خدمات پزشکی و داروخانه": "Medical Clinics & Pharmacies",
        "پوشاک و کیف و کفش": "Apparel & Retail Goods",
        "آهن‌آلات و مصالح صنعتی": "B2B Wholesalers & Industrial Materials"
    })

    # Ground-Truth Behavioral Archetypes (Used for Unsupervised Benchmark Evaluation)
    CUSTOMER_ARCHETYPES: List[str] = field(default_factory=lambda: [
        "طلا و سرمایه‌گذاری لوکس (Gold & Luxury Investors)",
        "تجار و عمده‌فروشان آهن و مصالح (B2B Industrial Wholesalers)",
        "مایحتاج روزمره و خانوار (Everyday Household & Groceries)",
        "مسافران و گردشگران پریمیوم (Affluent Travelers & Lifestyle)",
        "خدمات سلامت و پزشکی (Healthcare & Medical Consumers)"
    ])

    # Novel Higher-Order Hypergraph & Curvature Hyperparameters
    HYPERGRAPH_TIME_WINDOW_HOURS: int = 12   # Hyperedge temporal co-occurrence window
    CO_OCCURRENCE_THRESHOLD: float = 0.10   # Topological cosine pruning threshold
    RICCI_CURVATURE_ALPHA: float = 0.5       # Forman-Ricci curvature regularization weight
    EMBEDDING_DIM: int = 32                  # Continuous latent manifold dimension
    GNN_HIDDEN_DIM: int = 64
    GNN_LAYERS: int = 2
    GNN_HEADS: int = 4
    DROPOUT: float = 0.1
    LEARNING_RATE: float = 0.008
    WEIGHT_DECAY: float = 1e-4
    EPOCHS: int = 75

    # Customer Discovery & Clustering
    OPTIMAL_CLUSTERS: int = 5

    # Directory Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
    FIGURES_DIR: str = os.path.join(BASE_DIR, "figures")
    FIGURES_FA_DIR: str = os.path.join(BASE_DIR, "figures_fa")
    DATA_PATH: str = os.path.join(OUTPUT_DIR, "payment_transactions.csv")

cfg = Config()
