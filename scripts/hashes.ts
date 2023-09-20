import { ethers } from "hardhat";

const ACCOUNT_ADDRESS = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const TREASURY_ADDRESS = "0xbc0680Aba17CEe8A29a703B48377ff7C3FD864C3";

async function main() {
  const signer = await ethers.getSigner(ACCOUNT_ADDRESS);
  const Treasury = await ethers.getContractFactory("Treasury");
  const treasury = Treasury.attach(TREASURY_ADDRESS);

  let cairoProgramHash = await treasury.connect(signer).getCairoProgramHash();
  let cairoVerifierAddress = await treasury.connect(signer).getCairoVerifierAddress();
  // let lastOutputHash = await treasury.connect(signer).getLastOutputHash();
  // let lastFact = await treasury.connect(signer).getLastFact();

  console.log(`cairoProgramHash ${cairoProgramHash}`);
  console.log(`cairoVerifierAddress ${cairoVerifierAddress}`);
//   console.log(`lastOutputHash ${lastOutputHash}`);
//   console.log(`lastFact ${lastFact}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
