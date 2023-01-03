import { BigNumber } from "ethers";
import { ethers } from "hardhat";

const OWNER_ADDRESS = "0x69EA62095caD5211899720f1EB4dbE716205796C";
const TOKEN_ADDRESS = "0xA65Cef3f906817AECd744E27401deb473579c150";

async function main() {
  const signer = await ethers.getSigner(OWNER_ADDRESS);

  console.log(`Using signer with address: ${signer.address}`);

  const Token = await ethers.getContractFactory("Token");
  const token = Token.connect(signer).attach(TOKEN_ADDRESS);

  let mintAmount = BigNumber.from("10").pow("18").mul("1000");

  let transaction = await token.connect(signer).mint(signer.address, mintAmount);
  await transaction.wait();

  console.log(`minted ${mintAmount} to ${signer.address}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
