import hre from "hardhat";

async function main() {
  console.log("[*] Connecting to network and deploying EvidenceRegistry...");

  const connection = await hre.network.create();
  const EvidenceRegistry = await connection.ethers.getContractFactory("EvidenceRegistry");
  const evidenceRegistry = await EvidenceRegistry.deploy();

  await evidenceRegistry.waitForDeployment();

  const address = await evidenceRegistry.getAddress();
  console.log(`[SUCCESS] EvidenceRegistry deployed to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});