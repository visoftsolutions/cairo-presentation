import { BigNumber } from "ethers";
import { ethers } from "hardhat";

const OWNER_ADDRESS = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const TOKEN_ADDRESS = "0xA65Cef3f906817AECd744E27401deb473579c150";
const TREASURY_ADDRESS = "0xD7E6bF61e079CaBaE9232C9F5E0A10bA6acd6603";

async function main() {
  const signer = await ethers.getSigner(OWNER_ADDRESS);
  console.log(`Using signer with address: ${signer.address}`);

  const Treasury = await ethers.getContractFactory("Treasury");
  const treasury = Treasury.connect(signer).attach(TREASURY_ADDRESS);

  const depositAmount = BigNumber.from("10").pow("18").mul("100");

  let contractTransaction = await treasury.connect(signer).deposit(TOKEN_ADDRESS, depositAmount);
  await contractTransaction.wait();
  console.log(`deposited ${depositAmount} to ${signer.address}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
