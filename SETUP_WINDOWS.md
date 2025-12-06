# Windows Development Setup

Developing `Infinite_AI_Tsumego_Miner` on Windows is fully supported. Follow these steps to set up your environment.

## 1. Install Python
We recommend **Python 3.11.9** for stability and compatibility.
* [Download Python 3.11.9 for Windows](https://www.python.org/downloads/release/python-3119/)

## 2. Install Dependencies
Open a terminal (PowerShell or Command Prompt) in the project root:
```powershell
pip install -r requirements.txt
```

## 3. Install KataGo (Critical)
The mining rig requires the KataGo engine to function. On Windows, you need the executable.

1.  Download the latest release (v1.16.4) from the [KataGo Releases Page](https://github.com/lightvector/KataGo/releases).
    *   **Recommended:** `katago-v1.16.4-opencl-windows-x64.zip` (Best compatibility).
    *   *Alternative (if you have CUDA installed):* `katago-v1.16.4-cuda12.x-windows-x64.zip`
2.  Extract the zip file.
3.  Locate `katago.exe`.
4.  Copy `katago.exe` (and any `.dll` files in that folder) to:
    `C:\GameDev\Infinite_AI_Tsumego_Miner\assets\katago\`

## 4. Install Models
You need two specific neural network weights files.

1.  **Refree Model (Strong):** Download the latest "b18" model from [KataGo Training](https://katagotraining.org/).
    *   Rename it to `referee.bin.gz`
    *   Place in `assets/models/`
2.  **Human Model (Creative):** Download the `humanv0` model (b18c384nbt-humanv0.bin.gz) from [KataGo Extra Networks](https://github.com/lightvector/KataGo/blob/master/docs/SupportedModels.md).
    *   Rename it to `human.bin.gz`
    *   Place in `assets/models/`
3.  *(Optional)* **Vintage Model:** Old `g170` model for variety. Rename to `vintage.bin.gz`.

## 5. File Structure Check
Your `assets` folder should look like this:

```text
assets/
├── katago/
│   ├── katago.exe
│   └── (various .dll files)
└── models/
    ├── referee.bin.gz
    └── human.bin.gz
```

## 6. Run
```powershell
python src/miner.py
```
