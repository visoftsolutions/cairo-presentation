import { ethers } from "hardhat";

const OWNER_ADDRESS = "0x69EA62095caD5211899720f1EB4dbE716205796C";

async function main() {
  const signer = await ethers.getSigner(OWNER_ADDRESS);

  console.log(`Deploying contract with ${signer.address}`);

  const Token = await ethers.getContractFactory("Token");
  const token = await Token.connect(signer).deploy("CairoCoin", "CAIR");

  console.log(`Token deployed to ${token.address}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
