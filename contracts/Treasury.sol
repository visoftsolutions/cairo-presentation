// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

// Uncomment this line to use console.log
// import "hardhat/console.sol";

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./IFactRegistry.sol";

struct Entry {
    uint256 valutId;
    uint256 amountBefore;
    uint256 amountAfter;
}

contract Treasury is Context, Ownable {
    uint256 private _cairoProgramHash;
    address private _cairoVerifier;
    IFactRegistry private _factRegistry;

    uint256 private _lastValutId;
    // account -> token -> valutId
    mapping (address => mapping (address => uint256)) private _valuts;
    // valutId -> balance
    mapping (uint256 => uint256) _balances;

    event ValutRegistration(
        address account,
        address token,
        uint256 id
    );

    constructor(uint256 cairoProgramHash_, address cairoVerifier_) {
        _cairoProgramHash = cairoProgramHash_;
        _cairoVerifier = cairoVerifier_;
        _factRegistry = IFactRegistry(cairoVerifier_);
        _lastValutId = 0;
    }

    function updateState(uint256[] memory programOutput) public onlyOwner returns (bool) {
        // Ensure that a corresponding proof was verified.
        bytes32 outputHash = keccak256(abi.encodePacked(programOutput));
        bytes32 fact = keccak256(abi.encodePacked(_cairoProgramHash, outputHash));
        require(_factRegistry.isValid(fact), "Treasury: invalid cairo proof");
        
        for (uint256 i = 0; i < programOutput.length; i += 3) {
            uint256 valutId = programOutput[i];
            uint256 amountBefore = programOutput[i + 1];
            uint256 amountAfter = programOutput[i + 2];
            require(valutId != 0, "Treasury: invalid valutId");
            require(_balances[valutId] == amountBefore, "Treasury: invalid input state");
            _balances[valutId] = amountAfter;
        }
        return true;
    }

    function registerValut(address token) public {
        require(getValutId(token) == 0, "Treasury: valutId already registered");
        _lastValutId += 1;
        _valuts[_msgSender()][token] = _lastValutId;
        emit ValutRegistration(_msgSender(), token, _lastValutId);
    }

    function getValutId(address token) public view returns (uint256) {
        return _valuts[_msgSender()][token];
    }

    function balanceOf(address token) public view returns (uint256) {
        return _balances[_valuts[_msgSender()][token]];
    }

    function getCairoProgramHash() public view returns (uint256) {
        return _cairoProgramHash;
    }

    function getCairoVerifierAddress() public view returns (address) {
        return _cairoVerifier;
    }

    function deposit(address token, uint256 amount) public {
        uint256 valutId = getValutId(token);
        require(valutId != 0, "Treasury: invalid valutId");
        require(token != address(0), "Treasury: invalid token address");
        IERC20 tokenContract = IERC20(token);
        tokenContract.transferFrom(_msgSender(), address(this), amount);
        _balances[valutId] += amount;
    }

    function withdraw(address token, uint256 amount) public {
        uint256 valutId = getValutId(token);
        require(valutId != 0, "Treasury: invalid valutId");
        require(token != address(0), "Treasury: invalid token address");
        uint256 balanceBeforeWithdrawal = _balances[_valuts[_msgSender()][token]];
        require(balanceBeforeWithdrawal >= amount, "Treasury: insufficient balance");
        IERC20 tokenContract = IERC20(token);
        tokenContract.transfer(_msgSender(), amount);
        unchecked {
            _balances[valutId] = balanceBeforeWithdrawal - amount;
        }
    }
}
