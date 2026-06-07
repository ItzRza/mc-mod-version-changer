# Minecraft Mod & Plugin Utility

A Python-based CLI tool designed to manage Minecraft modifications efficiently using the Modrinth API. It can verify, update, and download local mods for specific game versions/loaders, as well as search for server-side plugins and mods.

---

## 📜 License & Credits

This project is open-source and licensed under the **GNU General Public License v3.0 (GPLv3)**. 

### Original Work Notice
* This repository contains modified code based on an original project developed by the **Original Author**.
* Original Repository: `[https://github.com/omltcat/mc-version-mods-checker]`
* All original copyright notices, legal disclaimers, and headers in the source code have been strictly preserved in compliance with Section 4 and 5 of the GNU GPLv3.

### Modifications
* Upgraded and expanded in 2026 by **Rza**.
* Added advanced filtering for server-side mods and plugins.
* Implemented automatic directory handling for distinct server loaders (Paper, Purpur, Spigot, etc.).

For full details regarding your rights to run, modify, and distribute this software, please refer to the accompanying `LICENSE` file.

---

## 🚀 Features

* **Mod Verification & Update:** Analyzes local `.jar` files using SHA-1 hashing to match them directly with Modrinth project IDs.
* **Smart Downloads:** Filters and downloads the exact matching mod versions for your target Minecraft version and loader (Fabric, Forge, NeoForge, etc.).
* **Server-Side Search:** Directly queries the Modrinth API to find and display up to 50 server-side specific plugins or mods compatible with your version.
* **Zero Dependencies:** Built entirely using Python's standard libraries (`urllib`, `hashlib`, `pathlib`), requiring no extra `pip` installations.

---

## 💻 How to Run

### Optional Prerequisites
* Python 3.8 or higher installed on your system.

## 💻 How to Run

Depending on your operating system, you can run this tool either as a standalone executable or as a Python script.

### Method 1: For Windows 11 Users (Easiest)
If you are on Windows 11, you do not need to install Python. You can directly run the pre-compiled executable file:
1. Locate the `MinecraftModUtility.exe` file in the release folder.
2. Double-click to run it, or open your terminal (PowerShell/CMD) and execute:
   MinecraftModUtility.exe
   
Method 2: For Other Operating Systems (Mac, Linux, or Older Windows)
If you are not on Windows 11, you can easily run the project using the raw Python source code.

Prerequisites
Python 3.8 or higher installed on your system.

Execution
Open your terminal in the project directory and run:
