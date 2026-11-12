import hashlib
import json
import sys
from web3 import Web3

# Configuration for local Hardhat node
RPC_URL = "http://127.0.0.1:8545"
# Replace with your deployed contract address after running the deployment script
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3" 

# Standard ABI for the registerEvidence function
CONTRACT_ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "string", "name": "_evidenceId", "type": "string"},
            {"internalType": "string", "name": "_sha256Hash", "type": "string"},
            {"internalType": "string", "name": "_imeiHash", "type": "string"},
            {"internalType": "string", "name": "_androidId", "type": "string"},
            {"internalType": "string", "name": "_osVersion", "type": "string"},
            {"internalType": "string", "name": "_examinerId", "type": "string"}
        ],
        "name": "registerEvidence",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]''')

def compute_sha256(file_path):
    """Computes the SHA-256 checksum of a mobile evidence file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        print(f"[-] Error: Evidence file not found at '{file_path}'.")
        sys.exit(1)

def register_evidence_on_chain(evidence_id, file_path, imei, android_id, os_ver, examiner_id):
    # 1. Compute Hash
    print(f"[*] Analyzing and hashing evidence file: {file_path}...")
    file_hash = compute_sha256(file_path)
    print(f"[+] SHA-256 Baseline Hash: {file_hash}")

    # 2. Connect to Blockchain Node
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("[-] Error: Unable to connect to Ethereum node. Is Hardhat running?")
        sys.exit(1)

    # Use the first default Hardhat account as the submitting examiner
    examiner_account = w3.eth.accounts[0]
    w3.eth.default_account = examiner_account

    # 3. Instantiate Contract
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)

    # 4. Send Transaction
    print(f"[*] Anchoring evidence record '{evidence_id}' to blockchain using account {examiner_account}...")
    try:
        tx_hash = contract.functions.registerEvidence(
            evidence_id,
            file_hash,
            imei,
            android_id,
            os_ver,
            examiner_id
        ).transact()

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"[SUCCESS] Evidence successfully anchored on-chain!")
        print(f"    - Transaction Hash: {receipt['transactionHash'].hex()}")
        print(f"    - Block Number: {receipt['blockNumber']}")

    except Exception as e:
        print(f"[-] Smart Contract Execution Failed: {e}")

if __name__ == "__main__":
    # Create a dummy simulated evidence database file for testing
    sample_file = "mmssms.db"
    with open(sample_file, "wb") as f:
        f.write(b"SIMULATED_ANDROID_SMS_DATABASE_CONTENT_FORENSIC_EXTRACTION")

    # Run ingestion and registration
    register_evidence_on_chain(
        evidence_id="CASE-2026-MOB-089",
        file_path=sample_file,
        imei="a8f5c2...hashed_imei",
        android_id="droid_14_98234",
        os_ver="Android 14",
        examiner_id="EXAM-9021"
    )