
from starkware.cairo.common.registers import get_label_location

const C6 = 0
const C7 = 1
const C8 = 2
const C9 = 3
const CT = 4
const CJ = 5
const CQ = 6
const CK = 7
const CA = 8
const D6 = 9
const D7 = 10
const D8 = 11
const D9 = 12
const DT = 13
const DJ = 14
const DQ = 15
const DK = 16
const DA = 17
const H6 = 18
const H7 = 19
const H8 = 20
const H9 = 21
const HT = 22
const HJ = 23
const HQ = 24
const HK = 25
const HA = 26
const S6 = 27
const S7 = 28
const S8 = 29
const S9 = 30
const ST = 31
const SJ = 32
const SQ = 33
const SK = 34
const SA = 35

func initial_deck(index) -> (card:felt):
    
    let (deck_address) = get_label_location(deck)
    return ([deck_address + index])

    deck:
    dw C6
    dw HT
    dw CA
    dw SQ
    dw D7
    dw CJ
    dw CK
    dw C8
    dw HK
    dw HQ
    dw S9
    dw S8
    dw SK
    dw D9
    dw SA
    dw H7
    dw C9
    dw DT
    dw S7
    dw HA
    dw D6
    dw DJ
    dw S6
    dw SJ
    dw DK
    dw DA
    dw CT
    dw CQ
    dw H9
    dw D8
    dw H6
    dw HJ
    dw C7
    dw ST
    dw H8
    dw DQ

end
