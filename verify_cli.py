import hashlib
import json
import os
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3" 

def compute_sha256(file_path):
    """Computes the SHA-256 hash of a given file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_evidence():
    print(f"[*] Connecting to local blockchain node at {RPC_URL}...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        print("[!] Error: Could not connect to local blockchain node. Is 'npx hardhat node' running?")
        return

    # Load contract ABI from Hardhat artifacts
    artifact_path = os.path.join("artifacts", "contracts", "EvidenceRegistry.sol", "EvidenceRegistry.json")
    if not os.path.exists(artifact_path):
        print(f"[!] Error: Contract artifact not found at {artifact_path}. Did you compile the contract?")
        return

    with open(artifact_path, "r") as f:
        artifact_json = json.load(f)
        contract_abi = artifact_json["abi"]

    # Initialize contract instance
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)

    # Prompt user for details
    case_id = input("[?] Enter Case ID to verify (e.g., CASE-2026-MOB-089): ").strip()
    file_path = input("[?] Enter path to the evidence file to check (e.g., mmssms.db): ").strip()

    if not os.path.exists(file_path):
        print(f"[!] Error: Evidence file '{file_path}' not found.")
        return

    print(f"[*] Re-computing SHA-256 hash for '{file_path}'...")
    current_hash = compute_sha256(file_path)
    print(f"[+] Current Computed Hash: {current_hash}")

    print(f"[*] Fetching on-chain record for Case ID: {case_id}...")
    try:
        # Call getEvidenceDetails matching the Solidity contract return signature
        # Returns: (sha256Hash, imeiHash, androidId, osVersion, examinerId, timestamp, examiner)
        result = contract.functions.getEvidenceDetails(case_id).call()
        onchain_hash = result[0]
        imei_hash = result[1]
        android_id = result[2]
        os_version = result[3]
        examiner_id = result[4]
        timestamp = result[5]
        examiner_addr = result[6]
    except Exception as e:
        print(f"[!] Error querying smart contract: {e}")
        return

    print(f"[*] On-Chain Registered Hash: {onchain_hash}")

    # Compare hashes (case-insensitive strip)
    cleaned_onchain_hash = onchain_hash.strip().lower()
    cleaned_current_hash = current_hash.strip().lower()

    print("\n" + "="*50)
    if cleaned_onchain_hash == cleaned_current_hash:
        print("[SUCCESS] INTEGRITY VERIFIED: The evidence file is AUTHENTIC.")
        print(f"    - Examiner ID: {examiner_id}")
        print(f"    - Submitting Address: {examiner_addr}")
        print(f"    - Device Android ID: {android_id}")
        print(f"    - On-Chain Timestamp: {timestamp}")
    else:
        print("[ALERT] TAMPERING DETECTED: Hash mismatch!")
        print("    - The file has been modified or altered since its initial seizure.")
    print("="*50)

if __name__ == "__main__":
    verify_evidence()