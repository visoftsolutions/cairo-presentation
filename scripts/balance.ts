import { ethers } from "hardhat";

const ACCOUNT_ADDRESS1 = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const ACCOUNT_ADDRESS2 = "0xFa6C7c032A499A3c92b78Ff4fE0c2945264c26E0";
const TREASURY_ADDRESS = "0x082d29217832234868aCC671C1B0B58e79E1Ea2F";
const TOKEN_ADDRESS = "0x3B5E0cD3587B5FC8f77173CEDB70a1D8dD2De5Ac";

async function main() {
  const Treasury = await ethers.getContractFactory("Treasury");
  const treasury = Treasury.attach(TREASURY_ADDRESS);

  let balance1 = await treasury.connect(ACCOUNT_ADDRESS1).balanceOf(TOKEN_ADDRESS);
  let balance2 = await treasury.connect(ACCOUNT_ADDRESS2).balanceOf(TOKEN_ADDRESS);

  console.log(`balance of ${ACCOUNT_ADDRESS1} is ${balance1}`);
  console.log(`balance of ${ACCOUNT_ADDRESS2} is ${balance2}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
