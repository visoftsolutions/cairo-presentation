import { loadFixture } from "@nomicfoundation/hardhat-network-helpers";
import { expect } from "chai";
import { ethers } from "hardhat";
import { Treasury, Token } from "../typechain-types";
import { BigNumberish } from "ethers";
import { Signer } from "ethers";

describe("Treasury", function () {
  // We define a fixture to reuse the same setup in every test.
  // We use loadFixture to run this setup once, snapshot that state,
  // and reset Hardhat Network to that snapshot in every test.

  async function deployTreasuryAndFactRegistry() {
    const [factRegistryOwner, treasuryOwner] = await ethers.getSigners();

    const FactRegistry = await ethers.getContractFactory("FactRegistry");
    const factRegistry = await FactRegistry.connect(factRegistryOwner).deploy();

    const Treasury = await ethers.getContractFactory("Treasury");
    const treasury = await Treasury.connect(treasuryOwner).deploy(0, factRegistry.address);

    return { factRegistry, factRegistryOwner, treasury, treasuryOwner };
  }

  async function deployToken() {
    const [tokenOwner] = await ethers.getSigners();

    const Token = await ethers.getContractFactory("Token");
    const token = await Token.deploy("Token", "TKN");

    return { token, tokenOwner };
  }

  async function registerValut(
    treasury: Treasury,
    token: Token,
    account: Signer,
  ) {
    let contractTransaction = await treasury.connect(account).registerValut(token.address);
    let contractReceipt = await contractTransaction.wait();
    for (let i = 0; contractReceipt.events && i < contractReceipt.events.length; ++i) {
      let event = contractReceipt.events[i];
      let accountAddress = event.args?.at(0);
      let tokenAddress = event.args?.at(1);
      let valutId = parseInt(event.args?.at(2));
      if (accountAddress == await account.getAddress() && tokenAddress == token.address) {
        return valutId;
      }
    }
    throw new Error("valutId not fount in events");
  }

  async function mintAndTransferToTreasury(
    treasury: Treasury,
    token: Token,
    tokenOwner: Signer,
    account: Signer,
    amount: BigNumberish
  ) {
    await token.connect(tokenOwner).mint(account.getAddress(), amount);
    await token.connect(account).approve(treasury.address, amount);
    await treasury.connect(account).deposit(token.address, amount);
  }

  describe("Deployment", function () {
    it("Should get right initial balance", async function () {
      const { treasury } = await loadFixture(deployTreasuryAndFactRegistry);
      const { token } = await loadFixture(deployToken);

      expect(await treasury.balanceOf(token.address)).to.equal(0);
    });
    it("Should get right valut ids", async function () {
      const { treasury } = await loadFixture(deployTreasuryAndFactRegistry);
      const { token } = await loadFixture(deployToken);
      const signers = await ethers.getSigners();

      for (let i = 0; i < signers.length; ++i) {
        let signer = signers[i];
        expect(await treasury.connect(signer).getValutId(token.address)).to.equal(0);
      }
    });
  });

  describe("Basic transfers", () => {
    it("Should transfer tokens", async () => {
      const { treasury } = await loadFixture(deployTreasuryAndFactRegistry);
      const { token, tokenOwner } = await loadFixture(deployToken);
      const [account1] = await ethers.getSigners();

      await registerValut(treasury, token, account1);

      await mintAndTransferToTreasury(
        treasury,
        token,
        tokenOwner,
        account1,
        100
      );
      let tokenBalanceOfResult = await token
        .connect(account1)
        .balanceOf(account1.address);
      let treasuryBalanceOfResult = await treasury
        .connect(account1)
        .balanceOf(token.address);

      expect(tokenBalanceOfResult).to.equal(0);
      expect(treasuryBalanceOfResult).to.equal(100);
    });
    it("Should withdraw tokens", async () => {
      const { treasury } = await loadFixture(deployTreasuryAndFactRegistry);
      const { token, tokenOwner } = await loadFixture(deployToken);
      const [account1] = await ethers.getSigners();

      await registerValut(treasury, token, account1);

      await mintAndTransferToTreasury(
        treasury,
        token,
        tokenOwner,
        account1,
        100
      );
      await treasury.connect(account1).withdraw(token.address, 100);
      let tokenBalanceOfResult = await token
        .connect(account1)
        .balanceOf(account1.address);
      let treasuryBalanceOfResult = await treasury
        .connect(account1)
        .balanceOf(token.address);

      expect(tokenBalanceOfResult).to.equal(100);
      expect(treasuryBalanceOfResult).to.equal(0);
    });
    it("Should set proper balances", async () => {
      const { treasury, treasuryOwner } = await loadFixture(deployTreasuryAndFactRegistry);
      const { token, tokenOwner } = await loadFixture(deployToken);
      const [account1, account2] = await ethers.getSigners();

      let account1ValutId = await registerValut(treasury, token, account1);
      let account2ValutId = await registerValut(treasury, token, account2);

      await mintAndTransferToTreasury(
        treasury,
        token,
        tokenOwner,
        account1,
        100
      );

      let programOutput = [
        account1ValutId,
        100,
        70,
        account2ValutId,
        0,
        30,
      ];

      await treasury.connect(treasuryOwner).updateState(programOutput);
      let treasuryBalanceOfAccount1 = await treasury
        .connect(account1)
        .balanceOf(token.address);
      let treasuryBalanceOfAccount2 = await treasury
        .connect(account2)
        .balanceOf(token.address);
      // let treasuryLastOutputHash = await treasury
      //   .connect(account1)
      //   .getLastOutputHash();
      // let treasuryLastFact = await treasury
      //   .connect(account1)
      //   .getLastFact();

      expect(treasuryBalanceOfAccount1).to.equal(70);
      expect(treasuryBalanceOfAccount2).to.equal(30);
      // console.log(treasuryLastOutputHash);
      // console.log(treasuryLastFact);
    });
  });
});
