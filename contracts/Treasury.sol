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
        require(_factRegistry.isValid(fact), "MISSING_CAIRO_PROOF");
        // bytes32 outputHash = keccak256(abi.encode(programOutput));
        // _lastOutputHash = outputHash;
        // bytes32 fact = keccak256(abi.encodePacked(_cairoProgramHash, outputHash));
        // _lastFact = fact;
        // require(_factRegistry.isValid(fact), "MISSING_CAIRO_PROOF");

        for (uint256 i = 0; i < programOutput.length; i += 3) {
            uint256 valutId = programOutput[i];
            uint256 amountBefore = programOutput[i + 1];
            uint256 amountAfter = programOutput[i + 2];
            require(valutId != 0, "valutId should not be zero");
            require(_balances[valutId] == amountBefore, "input state does not match");
            _balances[valutId] = amountAfter;
        }
        return true;
    }

    function registerValut(address token) public {
        require(getValutId(token) == 0, "valut already registered");
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
        require(valutId != 0, "valudId should not be zero");
        require(token != address(0), "token address should not be zero");
        IERC20 tokenContract = IERC20(token);
        require(tokenContract.transferFrom(_msgSender(), address(this), amount), "deposit failed");
        _balances[valutId] += amount;
    }

    function withdraw(address token, uint256 amount) public {
        uint256 valutId = getValutId(token);
        require(valutId != 0, "valudId should not be zero");
        require(token != address(0), "token address should not be zero");
        uint256 balanceBeforeWithdrawal = _balances[_valuts[_msgSender()][token]];
        require(balanceBeforeWithdrawal >= amount, "withdraw amount exceeds balance");
        IERC20 tokenContract = IERC20(token);
        require(tokenContract.transfer(_msgSender(), amount), "withdraw failed");
        unchecked {
            _balances[valutId] = balanceBeforeWithdrawal - amount;
        }
    }
}
