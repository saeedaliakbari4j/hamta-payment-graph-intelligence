"""
Transactional Payment Data Generator Module
Simulates realistic multi-card payment logs for financial institutions and payment switches.

Exact Schema:
[pan, amount, merchant_id, create_date, cast_name]
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, List
from src.config import cfg

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

np.random.seed(cfg.SEED)

GUILD_PROFILES: Dict[str, Dict] = {
    "طلافروشی": {
        "amount_dist": (16.8, 0.75),       # Mean ~20-25M Rials, High ticket
        "time_pref": (10, 20),
        "freq_weight": 0.08
    },
    "سوپرمارکت و خواروبار": {
        "amount_dist": (13.5, 0.55),       # Mean ~800k Rials, Micro daily
        "time_pref": (8, 23),
        "freq_weight": 0.35
    },
    "رستوران و فست‌فود": {
        "amount_dist": (14.6, 0.60),       # Mean ~2.5M Rials
        "time_pref": (12, 23),
        "freq_weight": 0.18
    },
    "لوازم الکترونیک و موبایل": {
        "amount_dist": (16.0, 0.70),       # Mean ~10-12M Rials
        "time_pref": (10, 21),
        "freq_weight": 0.10
    },
    "آژانس مسافرتی و گردشگری": {
        "amount_dist": (16.2, 0.65),       # Mean ~12-15M Rials
        "time_pref": (9, 18),
        "freq_weight": 0.09
    },
    "خدمات پزشکی و داروخانه": {
        "amount_dist": (14.2, 0.50),       # Mean ~1.6M Rials
        "time_pref": (8, 21),
        "freq_weight": 0.10
    },
    "پوشاک و کیف و کفش": {
        "amount_dist": (15.2, 0.60),       # Mean ~4.5M Rials
        "time_pref": (10, 22),
        "freq_weight": 0.15
    },
    "آهن‌آلات و مصالح صنعتی": {
        "amount_dist": (17.5, 0.80),       # Mean ~45M Rials, B2B wholesale
        "time_pref": (8, 16),
        "freq_weight": 0.05
    }
}

ARCHETYPE_PREFERENCES = {
    0: {"name": "طلا و سرمایه‌گذاری لوکس", "pref_guilds": ["طلافروشی", "پوشاک و کیف و کفش", "رستوران و فست‌فود"], "weights": [0.65, 0.20, 0.15]},
    1: {"name": "تجار و عمده‌فروشان آهن و مصالح", "pref_guilds": ["آهن‌آلات و مصالح صنعتی", "لوازم الکترونیک و موبایل", "سوپرمارکت و خواروبار"], "weights": [0.70, 0.20, 0.10]},
    2: {"name": "مایحتاج روزمره و خانوار", "pref_guilds": ["سوپرمارکت و خواروبار", "رستوران و فست‌فود", "پوشاک و کیف و کفش"], "weights": [0.60, 0.25, 0.15]},
    3: {"name": "مسافران و گردشگران پریمیوم", "pref_guilds": ["آژانس مسافرتی و گردشگری", "رستوران و فست‌فود", "لوازم الکترونیک و موبایل"], "weights": [0.55, 0.30, 0.15]},
    4: {"name": "خدمات سلامت و پزشکی", "pref_guilds": ["خدمات پزشکی و داروخانه", "سوپرمارکت و خواروبار", "پوشاک و کیف و کفش"], "weights": [0.60, 0.25, 0.15]}
}


def generate_merchant_pool(num_merchants: int = 350) -> pd.DataFrame:
    """Generate merchant terminals with specific guild assignments."""
    merchants = []
    guilds = cfg.CAST_NAMES
    weights = [GUILD_PROFILES[g]["freq_weight"] for g in guilds]
    weights = np.array(weights) / sum(weights)

    for i in range(num_merchants):
        mid = f"MERCH_{i+1:05d}"
        g = np.random.choice(guilds, p=weights)
        merchants.append({"merchant_id": mid, "cast_name": g})
    return pd.DataFrame(merchants)


def generate_card_pool(num_cards: int = 1500) -> pd.DataFrame:
    """
    Generate card tokens (PANs).
    Cards are associated with latent archetypes to establish ground-truth evaluation,
    simulating that multiple cards may belong to the same underlying entity.
    """
    cards = []
    bank_bins = ["603799", "589210", "627412", "502229", "621986", "639347", "505416", "627381"]

    for i in range(num_cards):
        bin_code = np.random.choice(bank_bins)
        last4 = f"{np.random.randint(1000, 9999):04d}"
        pan = f"{bin_code}******{last4}"
        # Latent persona assignment (0 to 4)
        latent_persona = i % len(ARCHETYPE_PREFERENCES)
        activity_multiplier = np.random.gamma(shape=2.0, scale=1.0)
        cards.append({
            "pan": pan,
            "latent_persona": latent_persona,
            "activity_multiplier": activity_multiplier
        })
    return pd.DataFrame(cards)


def generate_transactions(
    num_tx: int = cfg.NUM_TRANSACTIONS,
    num_cards: int = cfg.NUM_CARDS,
    num_merchants: int = cfg.NUM_MERCHANTS,
    days: int = cfg.SIMULATION_DAYS
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Synthesize high-fidelity multi-card payment logs.
    Returns:
        df_transactions: DataFrame with columns [pan, amount, merchant_id, create_date, cast_name]
        df_cards: Latent card metadata for ground truth benchmarking
        df_merchants: Merchant terminal metadata
    """
    df_merchants = generate_merchant_pool(num_merchants)
    df_cards = generate_card_pool(num_cards)

    # Pre-index merchants by guild
    merchants_by_guild = {g: df_merchants[df_merchants["cast_name"] == g]["merchant_id"].tolist() for g in cfg.CAST_NAMES}

    start_date = datetime.now() - timedelta(days=days)
    records = []

    card_weights = df_cards["activity_multiplier"].to_numpy().astype(float)
    card_weights /= card_weights.sum()

    for _ in range(num_tx):
        # 1. Select card (pan)
        card_idx = np.random.choice(len(df_cards), p=card_weights)
        card_row = df_cards.iloc[card_idx]
        pan = card_row["pan"]
        persona_id = card_row["latent_persona"]

        # 2. Select guild (cast_name) based on archetype preferences
        persona_pref = ARCHETYPE_PREFERENCES[persona_id]
        if np.random.rand() < 0.85:
            # Pick from preferred guilds
            cast_name = np.random.choice(persona_pref["pref_guilds"], p=persona_pref["weights"])
        else:
            # Occasional noise / incidental spending
            cast_name = np.random.choice(cfg.CAST_NAMES)

        # 3. Select specific merchant terminal in this guild
        available_merchants = merchants_by_guild[cast_name]
        merchant_id = np.random.choice(available_merchants)

        # 4. Monetary value from log-normal distribution
        mu, sigma = GUILD_PROFILES[cast_name]["amount_dist"]
        amount = float(np.random.lognormal(mean=mu, sigma=sigma))
        amount = round(amount, 0)

        # 5. Timestamp within simulation horizon
        random_day = np.random.randint(0, days)
        h_start, h_end = GUILD_PROFILES[cast_name]["time_pref"]
        random_hour = np.random.randint(h_start, h_end)
        random_min = np.random.randint(0, 60)
        random_sec = np.random.randint(0, 60)
        tx_dt = start_date + timedelta(days=random_day, hours=random_hour, minutes=random_min, seconds=random_sec)

        records.append({
            "pan": pan,
            "amount": amount,
            "merchant_id": merchant_id,
            "create_date": tx_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "cast_name": cast_name
        })

    df_transactions = pd.DataFrame(records)
    # Sort chronologically
    df_transactions["create_date"] = pd.to_datetime(df_transactions["create_date"])
    df_transactions = df_transactions.sort_values("create_date").reset_index(drop=True)
    df_transactions["create_date"] = df_transactions["create_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Enforce exact column order
    df_transactions = df_transactions[["pan", "amount", "merchant_id", "create_date", "cast_name"]]

    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    df_transactions.to_csv(cfg.DATA_PATH, index=False)
    print(f"[DataGenerator] Saved {len(df_transactions)} transactions to {cfg.DATA_PATH}")
    print(f"[DataGenerator] Distinct PANs: {df_transactions['pan'].nunique()}, Distinct Merchants: {df_transactions['merchant_id'].nunique()}, Guilds: {df_transactions['cast_name'].nunique()}")

    return df_transactions, df_cards, df_merchants


if __name__ == "__main__":
    df_tx, df_c, df_m = generate_transactions()
    print("Schema preview:")
    print(df_tx.head(5))
