# Neural Network Models

This directory contains the neural network weights used by the Infinite AI Tsumego Miner.

> **Note:** Model files (`.bin.gz`, `.txt.gz`) are gitignored due to their size (50MB-400MB each).
> You must download them manually from the sources below.

---

## The Model Bench

### 🏛️ The High Referee (REQUIRED)
**Role:** The absolute source of truth. Validates all puzzles with zero temperature and deep reading.

| Your File | Alias | Architecture | ELO | Source |
|-----------|-------|--------------|-----|--------|
| `STR_CONF_RTD_20251002__ELO14079_kata1-b28c512nbt-adam-s11165M-d5387M.bin.gz` | The_High_Referee | b28c512nbt | 14079 | [katagotraining.org](https://katagotraining.org/) - "Strongest Confidently Rated" |

---

### 🎭 The Chameleon (RECOMMENDED)
**Role:** Human-SL model for naturalistic, human-like mistakes. Supports rank emulation from 18k to 9d.

| Your File | Alias | Architecture | Source |
|-----------|-------|--------------|--------|
| `b18c384nbt-humanv0.bin.gz` | The_Chameleon | b18c384nbt | [KataGo Releases v1.15+](https://github.com/lightvector/KataGo/releases) |

---

### 🎯 The Specialist (IDEAL FOR 9x9)
**Role:** Finetuned specifically for 9x9 boards. Possibly the strongest network for your use case.

| Your File | Alias | Architecture | Source |
|-----------|-------|--------------|--------|
| `kata9x9-b18c384nbt-20231025.bin.gz` | The_Specialist | b18c384nbt | [katagotraining.org](https://katagotraining.org/) |

---

### 🦖 Large Networks

| Your File | Alias | Architecture | ELO | Notes |
|-----------|-------|--------------|-----|-------|
| `20220421_ELO13504_kata1-b60c320-s5943629568-d2852985812.bin.gz` | The_Titan | b60c320 | 13504 | 60-block monster. Slow but powerful. |
| `20201128_ELO12520_kata1-b20c256x2-s1610809600-d384128195.txt.gz` | The_Veteran | b20c256x2 | 12520 | Classic "g170 era" style. Good balance. |

---

### 🔬 Specialized Networks

| Your File | Alias | Architecture | Notes |
|-----------|-------|--------------|-------|
| `rect15-b20c256-s343365760-d96847752.bin.gz` | The_Explorer | b20c256 | Trained on rectangular boards 3x3 to 15x15. |
| `lionffen_b6c64_3x3_v10.txt.gz` | The_Pixie | b6c64 | Tiny experimental network. |

---

### 📚 The Novice Series (Lightweight b6 Networks)
**Role:** Fast, error-prone networks for generating variety and beginner puzzles.

| Your File | Alias | ELO | Approximate Rank |
|-----------|-------|-----|------------------|
| `20201128_ELO9023_kata1-b6c96-s73091584-d10630987.txt.gz` | The_Apprentice | 9023 | ~SDK (1-5 dan) |
| `20201128_ELO3330_kata1-b6c96-s15704832-d2832803.txt.gz` | The_Student | 3330 | ~DDK (5-10 kyu) |
| `20201128_ELO1530_kata1-b6c96-s4136960-d1510003.txt.gz` | The_Beginner | 1530 | ~15-20 kyu |
| `20201128_ELO484_kata1-b6c96-s1248000-d550347.txt.gz` | The_Novice | 484 | ~25+ kyu |

---

## Download Sources

- **Main KataGo Training:** https://katagotraining.org/
- **KataGo Releases (HumanSL):** https://github.com/lightvector/KataGo/releases
- **Supported Models Docs:** https://github.com/lightvector/KataGo/blob/master/docs/SupportedModels.md

---

## Architecture Key

| Code | Meaning |
|------|---------|
| `b28` | 28 residual blocks |
| `c512` | 512 channels |
| `nbt` | Nested bottleneck architecture |
| `humanv0` | Human-SL v0 (trained on human games) |
