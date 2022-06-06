// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.6.6 <0.9.0;

contract BuraGame {
    uint256 public bet;

    address public player1;
    address public player2;

    address public challenger;
    address public responder;

    uint8 public head = 0;
    uint8 public trump;

    uint8[] private deck = [
        0,
        22,
        8,
        33,
        10,
        5,
        7,
        2,
        25,
        24,
        30,
        29,
        34,
        12,
        35,
        19,
        3,
        13,
        28,
        26,
        9,
        14,
        27,
        32,
        16,
        17,
        4,
        6,
        21,
        11,
        18,
        23,
        1,
        31,
        20,
        15
    ];

    uint8[] private hand1;
    uint8[] private hand2;

    uint8[] private pile1;
    uint8[] private pile2;

    uint8[] public challenge;
    uint8[] private response;

    // function balance() public view returns(uint256) {
    //     return address(this).balance;
    // }

    function holding() public view returns (uint8[] memory) {
        require(
            msg.sender == player1 || msg.sender == player2,
            "Only players can see the cards"
        );
        if (msg.sender == player1) return hand1;
        else return hand2;
    }

    function holdingFmt() public view returns (string memory) {
        require(
            msg.sender == player1 || msg.sender == player2,
            "Only players can see the cards"
        );
        if (msg.sender == player1) return handToString(hand1);
        else return handToString(hand2);
    }

    /*
       This funciton allows player1 and player2 to join the table in that order. player1 != player2
       player1 sets the bet amount of the table. Bet of player to should match to the bet amount set by the 1st player
    */
    function join() public payable {
        require(
            (player1 == address(0)) ||
                (player2 == address(0) && player1 != msg.sender)
        );
        if (player1 == address(0)) {
            player1 = msg.sender;
            bet = msg.value;
        } else {
            require(bet == msg.value, "Wrong bet ammount");
            player2 = msg.sender;
            start();
        }
    }

    /*
        Allow 1st player to leave the table if the 2nd player has not yet joined.
        If both players are at the table players can no longer allowed to leave.
        This is a payable function, that refunds the bet amount to the player if he
        decides to leaves the table.
    */
    function leave() public payable {
        require(
            player1 != address(0) && player2 == address(0),
            "Can not leave the table if both players have joined"
        );
        player1 = address(0);
        payable(msg.sender).transfer(address(this).balance);
    }

    /*
        Start the game: deal 3 cards per hand and declare the trump.
        Currently, challender is set to player1. 
        TODO: Challanger selection should be randomized
    */
    function start() private {
        //require(player1 != address(0) && player2 != address(0) && hand1.length == 0 && hand2.length == 0);
        challenger = player1;
        responder = player2;
        trump = deck[deck.length - 1] / 9;
        hand1.push(deck[head++]);
        hand2.push(deck[head++]);
        hand1.push(deck[head++]);
        hand2.push(deck[head++]);
        hand1.push(deck[head++]);
        hand2.push(deck[head++]);
    }

    /*
        Challender issues a challenge! Check that sender is indeed a challenger and that 
        challenge has valid state. Then sort cards in ascending order to simplify 
        further calculations. 
    */
    function sendChallenge(uint8[] memory cards) public {
        require(msg.sender == challenger, "Only challenger can make this call");
        require(isValidChallenge(cards), "Invalid challenge has been issued");
        challenge = sort3(cards);
        updateHand(challenger, cards);
    }

    /*
        Responder issues a response! Check that sender is indeed a responder and that 
        response has valid state. Then sort cards in ascending order to simplify 
        further calculations. 
     */
    function sendResponse(uint8[] memory cards) public payable returns (bool) {
        require(msg.sender == responder, "Only responder can make this call");
        require(isValidResponse(cards), "Invalid response has been issued");
        response = sort3(cards);
        updateHand(responder, cards);

        bool isOverride = isChallengeOverride();
        if (isOverride) {
            //updatePile also resets challenge and respond arrays
            updatePile(responder);
            //Responder was able to bit the challenger for the round, and now becomes a challenger, so swap responder and challenger
            (responder, challenger) = (challenger, responder);
        } else {
            //updatePile also resets challenge and respond arrays
            updatePile(challenger);
        }
        if (head < 36) {
            refillHands();
        } else if ((hand1[0] == 99) && (hand1[1] == 99) && (hand1[2] == 99)) {
            uint8 pc1 = pileCount(player1);
            uint8 pc2 = pileCount(player1);
            if (pc1 > pc2) {
                payable(player1).transfer(address(this).balance);
            } else if (pc1 < pc2) {
                payable(player2).transfer(address(this).balance);
            } else {
                payable(player1).transfer(address(this).balance / 2);
                payable(player2).transfer(address(this).balance / 2);
            }
            flush();
        }
        return isOverride;
    }

    function stop() public payable {
        require(msg.sender == challenger, "Only challenger can claim the win");
        if (pileCount(challenger) >= 31) {
            payable(challenger).transfer(address(this).balance);
        } else {
            payable(responder).transfer(address(this).balance);
        }
        flush();
    }

    function flush() private {
        player1 = address(0);
        player2 = address(0);
        challenger = address(0);
        responder = address(0);
        head = 0;
        bet = 0;
        hand1 = new uint8[](0);
        hand2 = new uint8[](0);
        pile1 = new uint8[](0);
        pile2 = new uint8[](0);
        challenge = new uint8[](0);
        response = new uint8[](0);
    }

    function pileCount(address player) private view returns (uint8) {
        uint8 count = 0;
        uint8[] memory pile = getPile(player);
        for (uint8 i = 0; i < pile.length; i++) {
            if (pile[i] % 9 == 4) {
                //Jack = 2 points
                count += 2;
            } else if (pile[i] % 9 == 5) {
                //Queen = 3 points
                count += 3;
            } else if (pile[i] % 9 == 6) {
                //King = 4 points
                count += 4;
            } else if (pile[i] % 9 == 7) {
                //10 = 10 points
                count += 10;
            } else if (pile[i] % 9 == 8) {
                //Ace = 11 points
                count += 11;
            }
        }
        return count;
    }

    function handToString(uint8[] memory hand)
        private
        pure
        returns (string memory)
    {
        string memory out = "";
        for (uint8 i = 0; i < hand.length; i++) {
            if (hand[i] != 99) {
                string memory s = "C";
                if (hand[i] / 9 == 1) s = "D";
                else if (hand[i] / 9 == 2) s = "H";
                else if (hand[i] / 9 == 3) s = "S";

                string memory r = "6";
                if (hand[i] % 9 == 1) r = "7";
                else if (hand[i] % 9 == 2) r = "8";
                else if (hand[i] % 9 == 3) r = "9";
                else if (hand[i] % 9 == 4) r = "J";
                else if (hand[i] % 9 == 5) r = "Q";
                else if (hand[i] % 9 == 6) r = "K";
                else if (hand[i] % 9 == 7) r = "10";
                else if (hand[i] % 9 == 8) r = "A";
                out = string(abi.encodePacked(out, r, s, " "));
            }
        }
        return out;
    }

    function refillHands() private {
        if (challenge.length == 1) {
            drawCard(challenger);
            drawCard(responder);
        } else if (challenge.length == 2) {
            drawCard(challenger);
            drawCard(responder);
            drawCard(challenger);
            drawCard(responder);
        } else {
            drawCard(challenger);
            drawCard(responder);
            drawCard(challenger);
            drawCard(responder);
            drawCard(challenger);
            drawCard(responder);
        }
    }

    function drawCard(address player) private {
        if (head < deck.length) {
            if (player1 == player) {
                if (hand1[0] == 99) hand1[0] = deck[head++];
                else if (hand1[1] == 99) hand1[1] = deck[head++];
                else if (hand1[2] == 99) hand1[2] = deck[head++];
            } else {
                if (hand2[0] == 99) hand2[0] = deck[head++];
                else if (hand2[1] == 99) hand2[1] = deck[head++];
                else if (hand2[2] == 99) hand2[2] = deck[head++];
            }
        }
    }

    function isChallengeOverride() private view returns (bool) {
        if (challenge.length == 1) {
            return higher(response[0], challenge[0]);
        } else if (challenge.length == 2) {
            return
                higher(response[0], challenge[0]) &&
                higher(response[1], challenge[1]);
        } else {
            return
                higher(response[0], challenge[0]) &&
                higher(response[1], challenge[1]) &&
                higher(response[2], challenge[2]);
        }
    }

    /*
        Set the hand of a player
    */
    function updateHand(address player, uint8[] memory cards) private {
        if (player == player1) {
            for (uint8 i = 0; i < cards.length; i++) {
                for (uint8 j = 0; j < hand1.length; j++) {
                    if (hand1[j] == cards[i]) {
                        hand1[j] = 99;
                    }
                }
            }
        } else {
            for (uint8 i = 0; i < cards.length; i++) {
                for (uint8 j = 0; j < hand2.length; j++) {
                    if (hand2[j] == cards[i]) {
                        hand2[j] = 99;
                    }
                }
            }
        }
    }

    /*
        get the hand a player
    */
    function getHand(address player) private view returns (uint8[] memory) {
        if (player == player1) {
            return hand1;
        } else {
            return hand2;
        }
    }

    /*
        get the pile of a player
    */
    function getPile(address player) private view returns (uint8[] memory) {
        if (player == player1) {
            return pile1;
        } else {
            return pile2;
        }
    }

    /*
        Updated the pile for the winner of the round. Reset challenge and reponse arrays
    */

    function updatePile(address player) private {
        if (player == player1) {
            for (uint8 i = 0; i < challenge.length; i++) {
                pile1.push(challenge[i]);
            }
            for (uint8 i = 0; i < response.length; i++) {
                pile1.push(response[i]);
            }
        } else {
            for (uint8 i = 0; i < challenge.length; i++) {
                pile2.push(challenge[i]);
            }
            for (uint8 i = 0; i < response.length; i++) {
                pile2.push(response[i]);
            }
        }
        challenge = new uint8[](0);
        response = new uint8[](0);
    }

    /*
        Check that cards are really held by the challenger and that challenge is consistent with the rules of the game
    */
    function isValidChallenge(uint8[] memory cards)
        private
        view
        returns (bool)
    {
        if (cards.length == 0 || cards.length > 3) {
            return false;
        }
        uint8[] memory hand = getHand(challenger);
        //check that card is really held by the challenger
        if (!contains(cards[0], hand)) return false;

        if (cards.length == 1) {
            return true;
        } else {
            for (uint8 i = 1; i < cards.length; i++) {
                //check that card is really held by the challenger
                if (!contains(cards[i], hand)) return false;
                if (cards[i - 1] / 9 != cards[i] / 9) return false;
            }
            return true;
        }
    }

    //Check that cards are really held by the responder and that reposonse.length = challenge.length
    function isValidResponse(uint8[] memory cards) private view returns (bool) {
        if (cards.length != challenge.length) {
            return false;
        }
        uint8[] memory hand = getHand(responder);
        for (uint8 i = 0; i < cards.length; i++) {
            if (!contains(cards[i], hand)) return false;
        }
        return true;
    }

    //check if a card is contained in a hand
    function contains(uint8 card, uint8[] memory hand)
        private
        pure
        returns (bool)
    {
        if (card < 0 || card > 35) return false;

        for (uint8 i = 0; i < hand.length; i++) {
            if (card == hand[i]) return true;
        }
        return false;
    }

    //Check if card a is higher then card b. Take into consideration the trump suit
    function higher(uint8 a, uint8 b) private view returns (bool) {
        if (a / 9 == b / 9) {
            return a % 9 > b % 9;
        } else {
            return a / 9 == trump;
        }
    }

    //Sort upto 3 card arrays
    function sort3(uint8[] memory arr) private view returns (uint8[] memory) {
        require(arr.length < 4, "Can only sort arrays of length less then 4");
        if (arr.length <= 1) {
            return arr;
        } else if (arr.length == 2) {
            if (higher(arr[0], arr[1])) (arr[0], arr[1]) = (arr[1], arr[0]);
            return arr;
        } else {
            if (higher(arr[0], arr[1])) (arr[0], arr[1]) = (arr[1], arr[0]);
            if (higher(arr[1], arr[2])) (arr[1], arr[2]) = (arr[2], arr[1]);
            if (higher(arr[0], arr[1])) (arr[0], arr[1]) = (arr[1], arr[0]);
            return arr;
        }
    }
}
