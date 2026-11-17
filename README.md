# MobileChain-Guard 🛡️⛓️
*Blockchain-Anchored Mobile Forensics Evidence Integrity & Chain-of-Custody Verification System*

MobileChain-Guard is a forensic security tool designed to guarantee the cryptographic integrity of mobile device extractions (e.g., SQLite databases like `mmssms.db`, tarballs, and disk images). By anchoring SHA-256 hashes and device metadata to an immutable local Ethereum ledger (Hardhat / Solidity), forensic examiners can instantly detect evidence tampering or hash drift.

---

## 🛠️ Tech Stack & Architecture
- **Backend:** Python, Flask, `web3.py` for blockchain interaction and file hashing.
- **Smart Contract:** Solidity (`^0.8.20`) deployed via Hardhat.
- **Blockchain Node:** Local Ethereum JSON-RPC node (`http://127.0.0.1:8545`).
- **Frontend:** HTML5, CSS3, JavaScript (Responsive Dashboard).
- **Version Control:** Git & GitHub (`Laxman86/mobilechain-guard`).

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