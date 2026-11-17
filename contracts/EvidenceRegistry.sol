// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MobileChain-Guard Evidence Registry
 * @dev Anchors mobile forensic artifacts, device metadata, and cryptographic hashes
 *      to prevent tampering and verify forensic duplicate integrity.
 */
contract EvidenceRegistry {
    
    struct DeviceMetadata {
        string imeiHash;     // Hashed or anonymized IMEI for device identification
        string androidId;    // Android system ID or device serial
        string osVersion;    // Android OS version at time of acquisition
        string examinerId;   // Unique ID/Badge of the forensic examiner
    }

    struct Evidence {
        string evidenceId;   // Unique case or artifact identifier (e.g., CASE-2026-001)
        string sha256Hash;   // Baseline SHA-256 hash of the raw mobile extraction/database
        DeviceMetadata metadata;
        uint256 timestamp;   // Block timestamp of registration
        address examiner;    // Ethereum address of the submitting examiner
        bool exists;         // Validation flag
    }

    // Mapping from Evidence ID to Evidence struct
    mapping(string => Evidence) private evidenceRegistry;
    
    address public contractOwner;

    // Events for logging audit trails on-chain
    event EvidenceRegistered(
        string indexed evidenceId, 
        string sha256Hash, 
        address indexed examiner, 
        uint256 timestamp
    );
    
    event IntegrityVerified(
        string indexed evidenceId, 
        bool isIntact, 
        uint256 timestamp
    );

    event CustodyTransferred(
        string indexed evidenceId,
        address indexed previousCustodian,
        address indexed newCustodian,
        string notes,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == contractOwner, "Unauthorized: Only contract owner can perform this action");
        _;
    }

    constructor() {
        contractOwner = msg.sender;
    }

    /**
     * @dev Registers a new mobile forensic artifact and its baseline SHA-256 hash.
     */
    function registerEvidence(
        string memory _evidenceId,
        string memory _sha256Hash,
        string memory _imeiHash,
        string memory _androidId,
        string memory _osVersion,
        string memory _examinerId
    ) public {
        require(!evidenceRegistry[_evidenceId].exists, "Error: Evidence ID is already registered in the immutable ledger.");
        require(bytes(_evidenceId).length > 0, "Error: Evidence ID cannot be empty.");
        require(bytes(_sha256Hash).length > 0, "Error: SHA-256 hash cannot be empty.");

        DeviceMetadata memory meta = DeviceMetadata({
            imeiHash: _imeiHash,
            androidId: _androidId,
            osVersion: _osVersion,
            examinerId: _examinerId
        });

        evidenceRegistry[_evidenceId] = Evidence({
            evidenceId: _evidenceId,
            sha256Hash: _sha256Hash,
            metadata: meta,
            timestamp: block.timestamp,
            examiner: msg.sender,
            exists: true
        });

        emit EvidenceRegistered(_evidenceId, _sha256Hash, msg.sender, block.timestamp);
    }

    /**
     * @dev Compares a runtime hash against the on-chain baseline to check for hash drift/tampering.
     */
    function verifyEvidenceIntegrity(
        string memory _evidenceId,
        string memory _runtimeHash
    ) public returns (bool) {
        require(evidenceRegistry[_evidenceId].exists, "Error: Evidence ID not found in the registry.");

        Evidence memory ev = evidenceRegistry[_evidenceId];
        
        // Exact string comparison of hashes
        bool isIntact = (keccak256(abi.encodePacked(ev.sha256Hash)) == keccak256(abi.encodePacked(_runtimeHash)));

        emit IntegrityVerified(_evidenceId, isIntact, block.timestamp);
        return isIntact;
    }

    /**
     * @dev Transfers or updates the chain-of-custody handler for an evidence record.
     */
    function transferCustody(
        string memory _evidenceId,
        address _newCustodian,
        string memory _notes
    ) public {
        require(evidenceRegistry[_evidenceId].exists, "Error: Evidence ID not found in the registry.");
        require(_newCustodian != address(0), "Error: Invalid new custodian address.");

        address previousCustodian = evidenceRegistry[_evidenceId].examiner;
        evidenceRegistry[_evidenceId].examiner = _newCustodian;

        emit CustodyTransferred(_evidenceId, previousCustodian, _newCustodian, _notes, block.timestamp);
    }

    /**
     * @dev Retrieves registered evidence details and metadata for courtroom reporting.
     */
    function getEvidenceDetails(string memory _evidenceId) public view returns (
        string memory sha256Hash,
        string memory imeiHash,
        string memory androidId,
        string memory osVersion,
        string memory examinerId,
        uint256 timestamp,
        address examiner
    ) {
        require(evidenceRegistry[_evidenceId].exists, "Error: Evidence ID not found.");
        Evidence memory ev = evidenceRegistry[_evidenceId];
        return (
            ev.sha256Hash,
            ev.metadata.imeiHash,
            ev.metadata.androidId,
            ev.metadata.osVersion,
            ev.metadata.examinerId,
            ev.timestamp,
            ev.examiner
        );
    }
}