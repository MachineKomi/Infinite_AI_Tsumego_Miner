"""
Model Registry for Infinite AI Tsumego Miner

This module provides a centralized registry mapping original model filenames
to meaningful aliases and metadata. This preserves network lineage while
providing human-readable names in logs and output.

Infinite AI Tsumego Miner
Copyright (C) 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import glob

# =============================================================================
# MODEL REGISTRY
# Maps original filenames to aliases and metadata
# =============================================================================

MODEL_REGISTRY = {
    # =========================================================================
    # THE HIGH REFEREE - Strongest Confidently Rated Network
    # =========================================================================
    "STR_CONF_RTD_20251002__ELO14079_kata1-b28c512nbt-adam-s11165M-d5387M.bin.gz": {
        "alias": "The_High_Referee",
        "role": "referee",
        "elo": 14079,
        "architecture": "b28c512nbt",
        "blocks": 28,
        "channels": 512,
        "description": "Strongest confidently-rated network from kata1 run. "
                       "28 blocks, 512 channels with nested bottleneck architecture. "
                       "Use as the absolute source of truth for validation.",
        "source": "https://katagotraining.org/",
    },
    
    # =========================================================================
    # PLAYER NETWORKS - Human-Style
    # =========================================================================
    "b18c384nbt-humanv0.bin.gz": {
        "alias": "The_Chameleon",
        "role": "player",
        "elo": None,  # Varies by rank setting
        "architecture": "b18c384nbt",
        "blocks": 18,
        "channels": 384,
        "is_human_sl": True,
        "description": "Human-SL model trained on historical human games. "
                       "Can emulate play from 18k to 9d by setting humanSLProfile. "
                       "Produces naturalistic, human-like moves and mistakes.",
        "source": "https://github.com/lightvector/KataGo/releases",
    },
    
    # =========================================================================
    # PLAYER NETWORKS - 9x9 Specialist
    # =========================================================================
    "kata9x9-b18c384nbt-20231025.bin.gz": {
        "alias": "The_Specialist",
        "role": "player",
        "elo": None,  # Specialized, not directly comparable
        "architecture": "b18c384nbt",
        "blocks": 18,
        "channels": 384,
        "description": "9x9 finetuned specialist. Several months of dedicated training "
                       "on 9x9 positions. Possibly strongest network for 9x9 games. "
                       "Used in creation of the katagobooks.org 9x9 book.",
        "source": "https://katagotraining.org/",
    },
    
    # =========================================================================
    # PLAYER NETWORKS - Large/Strong
    # =========================================================================
    "20220421_ELO13504_kata1-b60c320-s5943629568-d2852985812.bin.gz": {
        "alias": "The_Titan",
        "role": "player",
        "elo": 13504,
        "architecture": "b60c320",
        "blocks": 60,
        "channels": 320,
        "description": "Large 60-block network from kata1 run. Very strong general "
                       "player. Slower to evaluate but extremely powerful.",
        "source": "https://katagotraining.org/",
    },
    
    "20201128_ELO12520_kata1-b20c256x2-s1610809600-d384128195.txt.gz": {
        "alias": "The_Veteran",
        "role": "player",
        "elo": 12520,
        "architecture": "b20c256x2",
        "blocks": 20,
        "channels": 256,
        "description": "20-block network from late 2020 kata1 run. Classic 'g170 era' "
                       "KataGo style. Good balance of strength and speed.",
        "source": "https://katagotraining.org/",
    },
    
    # =========================================================================
    # PLAYER NETWORKS - Rectangular Board Specialist
    # =========================================================================
    "rect15-b20c256-s343365760-d96847752.bin.gz": {
        "alias": "The_Explorer",
        "role": "player",
        "elo": None,
        "architecture": "b20c256",
        "blocks": 20,
        "channels": 256,
        "description": "Trained on rectangular boards from 3x3 to 15x15. "
                       "Specializes in non-square and small board positions. "
                       "From December 2020 distributed training test run.",
        "source": "https://katagotraining.org/",
    },
    
    # =========================================================================
    # PLAYER NETWORKS - Lightweight/Fast (b6c96 series)
    # =========================================================================
    "20201128_ELO9023_kata1-b6c96-s73091584-d10630987.txt.gz": {
        "alias": "The_Apprentice",
        "role": "player",
        "elo": 9023,
        "architecture": "b6c96",
        "blocks": 6,
        "channels": 96,
        "description": "Lightweight 6-block network. SDK-level strength. "
                       "Fast evaluation, good for high-throughput generation.",
        "source": "https://katagotraining.org/",
    },
    
    "20201128_ELO3330_kata1-b6c96-s15704832-d2832803.txt.gz": {
        "alias": "The_Student",
        "role": "player",
        "elo": 3330,
        "architecture": "b6c96",
        "blocks": 6,
        "channels": 96,
        "description": "Early 6-block network. DDK-level strength (~5-10 kyu). "
                       "Makes interesting tactical mistakes.",
        "source": "https://katagotraining.org/",
    },
    
    "20201128_ELO1530_kata1-b6c96-s4136960-d1510003.txt.gz": {
        "alias": "The_Beginner",
        "role": "player",
        "elo": 1530,
        "architecture": "b6c96",
        "blocks": 6,
        "channels": 96,
        "description": "Very early 6-block network. Weak DDK-level (~15-20 kyu). "
                       "Produces many blunders suitable for easy puzzles.",
        "source": "https://katagotraining.org/",
    },
    
    "20201128_ELO484_kata1-b6c96-s1248000-d550347.txt.gz": {
        "alias": "The_Novice",
        "role": "player",
        "elo": 484,
        "architecture": "b6c96",
        "blocks": 6,
        "channels": 96,
        "description": "Earliest 6-block network. Very weak (~25+ kyu). "
                       "Extremely error-prone. Good for beginner puzzle generation.",
        "source": "https://katagotraining.org/",
    },
    
    # =========================================================================
    # SPECIAL NETWORKS
    # =========================================================================
    "lionffen_b6c64_3x3_v10.txt.gz": {
        "alias": "The_Pixie",
        "role": "special",
        "elo": None,
        "architecture": "b6c64",
        "blocks": 6,
        "channels": 64,
        "description": "Tiny 6-block, 64-channel network. Extremely fast. "
                       "Alternative training run (lionffen). Experimental.",
        "source": "Community contribution",
    },
}


def get_model_info(filename):
    """
    Look up model metadata by filename.
    Returns the registry entry or a default if not found.
    """
    basename = os.path.basename(filename)
    if basename in MODEL_REGISTRY:
        return MODEL_REGISTRY[basename]
    return {
        "alias": f"Unknown_{basename[:20]}",
        "role": "unknown",
        "description": f"Unregistered model: {basename}",
    }


def get_alias(filename):
    """Get just the human-readable alias for a model."""
    return get_model_info(filename).get("alias", os.path.basename(filename))


def scan_models_directory(models_dir="./assets/models"):
    """
    Scan the models directory and return info about all available models.
    """
    available = []
    patterns = ["*.bin.gz", "*.txt.gz", "*.bin", "*.txt"]
    
    for pattern in patterns:
        for filepath in glob.glob(os.path.join(models_dir, pattern)):
            info = get_model_info(filepath)
            info["filepath"] = filepath
            info["filename"] = os.path.basename(filepath)
            available.append(info)
    
    return available


def find_referee_model(models_dir="./assets/models"):
    """Find the best available referee model."""
    available = scan_models_directory(models_dir)
    
    # First, look for explicitly marked referee
    for model in available:
        if model.get("role") == "referee":
            return model["filepath"]
    
    # Fall back to highest ELO model
    rated = [m for m in available if m.get("elo") is not None]
    if rated:
        best = max(rated, key=lambda x: x["elo"])
        return best["filepath"]
    
    return None


def find_player_models(models_dir="./assets/models"):
    """Find all available player models."""
    available = scan_models_directory(models_dir)
    return [m for m in available if m.get("role") == "player"]


# =============================================================================
# HUMAN SL RANK PROFILES
# =============================================================================

HUMAN_SL_RANKS = {
    "beginner": ["18k", "15k", "12k"],
    "intermediate": ["10k", "8k", "5k", "3k", "1k"],
    "advanced": ["1d", "2d", "3d", "4d", "5d"],
    "expert": ["6d", "7d", "8d", "9d"],
}

# Full list of valid humanSLProfile values
VALID_HUMAN_SL_PROFILES = [
    "preaz_18k", "preaz_15k", "preaz_12k", "preaz_10k", "preaz_8k",
    "preaz_5k", "preaz_3k", "preaz_1k", "preaz_1d", "preaz_2d",
    "preaz_3d", "preaz_4d", "preaz_5d", "preaz_6d", "preaz_7d",
    "preaz_8d", "preaz_9d",
    # Also simple rank names work
    "rank_18k", "rank_15k", "rank_12k", "rank_10k", "rank_8k",
    "rank_5k", "rank_3k", "rank_1k", "rank_1d", "rank_2d",
    "rank_3d", "rank_4d", "rank_5d", "rank_6d", "rank_7d",
    "rank_8d", "rank_9d",
]


if __name__ == "__main__":
    # Test: Print all registered models
    print("=== Model Registry ===\n")
    for filename, info in MODEL_REGISTRY.items():
        print(f"{info['alias']:20} | ELO {str(info.get('elo', 'N/A')):>6} | {info['architecture']}")
        print(f"  └─ {filename}")
        print()
