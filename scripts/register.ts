import { BigNumber } from "ethers";
import { ethers } from "hardhat";

const OWNER_ADDRESS = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const OWNER_ADDRESS2 = "0xFa6C7c032A499A3c92b78Ff4fE0c2945264c26E0";
const TOKEN_ADDRESS = "0xA65Cef3f906817AECd744E27401deb473579c150";
const TREASURY_ADDRESS = "0xD7E6bF61e079CaBaE9232C9F5E0A10bA6acd6603";

async function main() {
  const signer = await ethers.getSigner(OWNER_ADDRESS);
  console.log(`Using signer with address: ${signer.address}`);

  const Treasury = await ethers.getContractFactory("Treasury");
  const treasury = Treasury.connect(signer).attach(TREASURY_ADDRESS);

  let valutId = await treasury.getValutId(TOKEN_ADDRESS);
  if (valutId == BigNumber.from("0")) {
    let contractTransaction = await treasury.connect(signer).registerValut(TOKEN_ADDRESS);
    await contractTransaction.wait();
  }

  valutId = await treasury.getValutId(TOKEN_ADDRESS);
  console.log(`Your valut id is: ${valutId}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
