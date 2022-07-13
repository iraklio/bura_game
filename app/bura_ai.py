class Card:
    def __init__(self, s, r) -> None:
        self.suit = s
        self.rank = r


class Bura:
    def __init__(self) -> None:

        self.hand = []
        self.trump = None

        self.open_pile = []
        self.blind_pile_count = None

    def send_challenge(self):

        c1 = self.hand[0]
        c2 = self.hand[1]
        c3 = self.hand[2]

        if c1.suit == c2.suit and c2.suit == c3.suit:
            return [c1, c2, c3]
        elif c1.suit == c2.suit:
            return [c1, c2]
        elif c2.suit == c3.suit:
            return [c2, c3]
        elif c1.suit == c3.suit:
            return [c1, c3]
        else:
            if c1.rank in ["6", "7", "8", "9"] and c1.suit != self.trump:
                return [c1]
            if c2.rank in ["6", "7", "8", "9"] and c2.suit != self.trump:
                return [c2]
            if c3.rank in ["6", "7", "8", "9"] and c3.suit != self.trump:
                return [c3]
            if c1.rank in ["J", "Q", "K"] and c1.suit != self.trump:
                return [c1]
            if c2.rank in ["J", "Q", "K"] and c2.suit != self.trump:
                return [c2]
            if c3.rank in ["J", "Q", "K"] and c3.suit != self.trump:
                return [c3]

            return [c1]

    def send_response(self, ch) -> list:

        c1 = self.hand[0]
        c2 = self.hand[1]
        c3 = self.hand[2]

        if len(ch) == 1:
            for c in self.hand:
                if c.suit == ch[0].suit:
                    if c.rank > ch[0].rank:
                        return [c]
                elif c.suit == self.trump:
                    return [c]

            return []
        elif len(ch) == 2:
            chs = sort(ch, self.trump)
            o1 = chs[0]
            o2 = chs[1]

            if less(o1, c1, self.trump) and less(o2, c2, self.trump):
                return [c1, c2]
            if less(o1, c1, self.trump) and less(o2, c3, self.trump):
                return [c1, c3]
            if less(o1, c2, self.trump) and less(o2, c3, self.trump):
                return [c2, c3]

            return []

        elif len(ch) == 3:
            chs = sort(ch, self.trump)
            o1 = chs[0]
            o2 = chs[1]
            o2 = chs[2]
            if (
                less(o1, c1, self.trump)
                and less(o2, c2, self.trump)
                and less(o2, c2, self.trump)
            ):
                return [c1, c2, c3]

            return []


def less(c1, c2, trump) -> bool:
    if c1.suit == c2.suit:
        if c1.rank < c2.rank:
            return True
        else:
            return False
    else:
        if c2.suit == trump:
            return True
        else:
            return False


def sort(cards, trump) -> list:

    if len(cards) == 0 or len(cards) == 1:
        return cards

    if len(cards) == 2:
        c1 = cards[0]
        c2 = cards[1]
        if less(c1, c2, trump):
            return [c1, c2]
        else:
            return [c2, c1]

    if len(cards) == 3:
        c1 = cards[0]
        c2 = cards[1]
        c3 = cards[2]
        if less(c2, c1, trump):
            (c1, c2) = (c2, c1)
        if less(c3, c2, trump):
            (c2, c3) = (c3, c2)
        if less(c2, c1, trump):
            (c1, c2) = (c2, c1)
        return [c1, c2, c3]

