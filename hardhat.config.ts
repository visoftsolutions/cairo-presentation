import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: "0.8.17",
  networks: {
    goerli: {
      url: "https://eth-goerli.g.alchemy.com/v2/DxDV89UmF7aRrlPaKrKcUcKhe1uDNUqN",
      accounts: [
        "0xc8b486d1cd5cb4835025983c1e41bfcb91421e3e83dca926514394204409b9a8",
        "0x435aa22562edbdce8e72101ec2d04c5ed9ce1d9c93378e45a51bb928c49ca04b"
      ]
    }
  }
};

export default config;
