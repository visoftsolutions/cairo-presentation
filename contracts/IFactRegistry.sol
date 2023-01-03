// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

interface IFactRegistry {
    /*
      Returns true if the given fact was previously registered in the contract.
    */
    function isValid(bytes32 fact) external view returns (bool);
}
