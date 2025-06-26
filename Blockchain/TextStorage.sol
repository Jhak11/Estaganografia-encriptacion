// SPDX-License-Identifier: MIT
//version del compilador solidity
// pragma solidity ^0.8.0;

/*// Declaración del contrato
contract TextStorage {

    // Variables de estado
    string private storedText;

    //almacenar texto
    function storeText(string memory _text) public {
        storedText = _text;
    }

    //recuperar texto
    function retrieveText() public view returns (string memory) {
        return storedText;
    }
}*/

pragma solidity ^0.8.0;

contract TextStorage {
    string private storedText;
    address private owner;

    constructor() {
        owner = msg.sender; // El que despliega es el dueño
    }

    function storeText(string memory _text) public {
        require(msg.sender == owner, "No tienes permiso para modificar el texto");
        storedText = _text;
    }

    function retrieveText() public view returns (string memory) {
        return storedText;
    }
}