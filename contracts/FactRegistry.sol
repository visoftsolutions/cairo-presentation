// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

import "./IFactRegistry.sol";

contract FactRegistry is IFactRegistry {
    function isValid(bytes32) external pure returns (bool) {
        return true;
    }
}
