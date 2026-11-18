# MobileChain-Guard 🛡️⛓️

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Solidity-%23363636.svg?style=for-the-badge&logo=solidity&logoColor=white" alt="Solidity">
  <img src="https://img.shields.io/badge/Hardhat-FFF100?style=for-the-badge&logo=hardhat&logoColor=black" alt="Hardhat">
  <img src="https://img.shields.io/badge/Web3.py-F16822?style=for-the-badge&logo=web3.py&logoColor=white" alt="Web3.py">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

*Blockchain-Anchored Mobile Forensics Evidence Integrity & Chain-of-Custody Verification System*

MobileChain-Guard is an advanced forensic security tool designed to guarantee the cryptographic integrity of mobile device extractions (such as SQLite databases like `mmssms.db`, tarballs, and disk images). By securely anchoring SHA-256 file hashes and device metadata to an immutable local Ethereum ledger (Hardhat / Solidity), forensic examiners can instantly detect evidence tampering, hash drift, or unauthorized chain-of-custody modifications.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology / Protocol | Description |
| :--- | :--- | :--- |
| **Smart Contract** | ![Solidity](https://img.shields.io/badge/Solidity-%23363636.svg?style=flat-square&logo=solidity&logoColor=white) Hardhat | Immutably records SHA-256 hashes, metadata, and custody transfers on-chain. |
| **Backend & Hashing** | ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) Web3.py | Handles device extraction ingestion, local file hashing, and RPC transaction relay. |
| **Local Node** | ![Ethereum](https://img.shields.io/badge/Ethereum-3C3C3D?style=flat-square&logo=Ethereum&logoColor=white) Hardhat Node | Provides local JSON-RPC Ethereum testing network (`http://127.0.0.1:8545`). |
| **Frontend Dashboard** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) | Responsive user interface for evidence management and verification auditing. |

---

## 📁 Project Structure

```text
mobilechain-guard/
│
├── contracts/
│   └── EvidenceRegistry.sol      # Core Solidity smart contract
├── scripts/
│   └── deploy.js                 # Hardhat deployment script
├── docs/
│   └── screenshots/              # UI walkthrough screenshots
├── app.py                        # Flask backend application
├── hasher_cli.py                 # Ingestion & on-chain anchoring CLI
├── verify_cli.py                 # Integrity verification & tamper-detection CLI
├── mmssms.db                     # Simulated mobile evidence artifact (Git-ignored)
└── README.md
