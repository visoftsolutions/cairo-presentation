import { BigNumber } from "ethers";
import { ethers } from "hardhat";

const ACCOUNT_ADDRESS1 = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const ACCOUNT_ADDRESS2 = "0xFa6C7c032A499A3c92b78Ff4fE0c2945264c26E0";
const TREASURY_ADDRESS = "0x082d29217832234868aCC671C1B0B58e79E1Ea2F";

async function main() {
  const signer1 = await ethers.getSigner(ACCOUNT_ADDRESS1);
  const signer2 = await ethers.getSigner(ACCOUNT_ADDRESS2);
  console.log(`Deployer address: ${signer1.address}`);

  const Treasury = await ethers.getContractFactory("Treasury");
  const treasury = Treasury.connect(signer1).attach(TREASURY_ADDRESS);
  const Token = await ethers.getContractFactory("Token");
  const token = await Token.connect(signer1).deploy("CairoCoin", "CAIR");
  console.log(`Token deployed at address: ${token.address}`);

  let mintAmount = BigNumber.from("10").pow("18").mul("1000");

  let transaction = await token.connect(signer1).mint(signer1.address, mintAmount);
  await transaction.wait();
  console.log(`Minted to ${signer1.address} -> ${mintAmount}`);
  transaction = await token.connect(signer1).mint(signer2.address, mintAmount);
  await transaction.wait();
  console.log(`Minted to ${signer1.address} -> ${mintAmount}`);

  let approvalAmount = BigNumber.from("10").pow("18").mul("100");
  transaction = await token.connect(signer1).approve(TREASURY_ADDRESS, approvalAmount);
  await transaction.wait();
  console.log(`Approved to ${TREASURY_ADDRESS} -> ${approvalAmount}`);

  transaction = await treasury.connect(signer1).registerValut(token.address);
  await transaction.wait();
  console.log(`Valut for ${signer1.address} is ${await treasury.connect(signer1).getValutId(token.address)}`);

  transaction = await treasury.connect(signer2).registerValut(token.address);
  await transaction.wait();
  console.log(`Valut for ${signer2.address} is ${await treasury.connect(signer2).getValutId(token.address)}`);

  let depositAmount = BigNumber.from("10").pow("18").mul("100");
  transaction = await treasury.connect(signer1).deposit(token.address, depositAmount);
  await transaction.wait();
  console.log(`Deposit from ${signer1.address} amount ${depositAmount}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
