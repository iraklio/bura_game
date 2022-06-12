# Declare this file as a StarkNet contract.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from starkware.starknet.common.syscalls import (
    get_caller_address
)

from starkware.cairo.common.math_cmp import is_le, is_in_range, is_not_zero
from starkware.cairo.common.math import ( 
    abs_value, 
    sign,
    assert_nn, 
    assert_nn_le, 
    assert_le, 
    unsigned_div_rem, 
    signed_div_rem, 
    assert_in_range, 
    sqrt
    )

const NULL_VALUE = 99
const C6 = 0
const C7 = 1
const C8 = 2
const C9 = 3
const C10 = 4
const CJ = 5
const CQ = 6
const CK = 7
const CA = 8
const D6 = 9
const D7 = 10
const D8 = 11
const D9 = 12
const D10 = 13
const DJ = 14
const DQ = 15
const DK = 16
const DA = 17
const H6 = 18
const H7 = 19
const H8 = 20
const H9 = 21
const H10 = 22
const HJ = 23
const HQ = 24
const HK = 25
const HA = 26
const S6 = 27
const S7 = 28
const S8 = 29
const S9 = 30
const S10 = 31
const SJ = 32
const SQ = 33
const SK = 34
const SA = 35


@storage_var
func win_loss(s,r,t) -> (res : felt):
end

@storage_var
func bet() -> (res : felt):
end
@storage_var
func trump()->(c:felt):
end
@storage_var
func cards(player:felt, idx:felt)->(c:felt):
end

@storage_var
func challenge(idx:felt)->(c:felt):
end

@storage_var
func card_idx(idx:felt)->(c:felt):
end

@storage_var
func piles(player:felt) -> (pile:felt):
end

# Define a storage variable.
@storage_var
func player1()->(address:felt):
end

@storage_var
func player2()->(address:felt):
end

@storage_var
func challenger() -> (address : felt):
end

@storage_var
func responder() -> (address : felt):
end

@storage_var
func head() -> (res : felt):
end


@storage_var
func deck(idx: felt) -> (card:felt):
end

@storage_var
func points(idx: felt) -> (card:felt):
end


@external
func join_game{ syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> ():

    let (sender) = get_caller_address()
    let (p1) = player1.read()
    if p1 == 0:
        player1.write(sender)
        return()
    else:
        let (p2) = player2.read()
        if p2 == 0:            
            player2.write(sender)
            start_game()
            return()
        else:
            return()        
        end
    end
end


@external
func leave_game{ syscall_ptr : felt*,  pedersen_ptr : HashBuiltin*, range_check_ptr}():

    let (sender) = get_caller_address()
    let (p1) = player1.read()
    let (p2) = player2.read()
    assert p2 = 0
    assert p1 = sender
    player1.write(0)
    return()
end


func start_game{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals

    let ( local p1) = player1.read()
    let ( local p2) = player2.read()
    
    let (c1) = draw_next_card()    
    let (c2) = draw_next_card()
    let (c3) = draw_next_card()
    let (c4) = draw_next_card()
    let (c5) = draw_next_card()
    let (c6) = draw_next_card()

    cards.write(p1, 1, c1)
    cards.write(p2, 1, c2)
    cards.write(p1, 2, c3)
    cards.write(p2, 2, c4)   
    cards.write(p1, 3, c5)    
    cards.write(p2, 3, c6)

    challenge.write(1, NULL_VALUE)
    challenge.write(2, NULL_VALUE)
    challenge.write(3, NULL_VALUE)

    challenger.write(p1)
    responder.write(p2) 

    let (t) = deck.read(11)
    let (div,_) = unsigned_div_rem(t,9)
    trump.write(div)

    return()
end

@external
func send_challenge1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx:felt) -> ():

    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (sender) = get_caller_address()
    let (ch) = challenger.read()    
    assert sender = ch

    let (cc) = cards.read(sender, idx)
    challenge.write(1,cc)
    cards.write(sender, idx, NULL_VALUE)
    card_idx.write(1, idx)

    return()
end

@external
func send_challenge2{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2) -> ():

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0

    let (sender) = get_caller_address()
    let (ch) = challenger.read()
    assert sender = ch

    let (c1) = cards.read(sender, idx1)
    challenge.write(1,c1)
    card_idx.write(1, idx1)
    cards.write(sender, idx1, NULL_VALUE)    

    let (c2) = cards.read(sender, idx2)
    challenge.write(2,c2)
    card_idx.write(2, idx2)    
    cards.write(sender, idx2, NULL_VALUE)
    return()
end




@external
func send_response1new{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx):
    alloc_locals

    assert (idx-1)*(idx-2)*(idx-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = responder.read()
    let (ch) = challenger.read()    
    assert sender = rp    

    let (challenger_card) = challenge.read(1)
    let (responder_card) = cards.read(sender, idx)

    let (challenger_suit, challenger_rank) = unsigned_div_rem(challenger_card, 9)    
    let (responder_suit, responder_rank) = unsigned_div_rem(responder_card, 9)

    #reset challenge
    challenge.write(1, NULL_VALUE)
    #cards.write(sender, idx, NULL_VALUE) 

    if challenger_suit == responder_suit:        
        let (res) = is_le(challenger_rank, responder_rank)
        tempvar range_check_ptr = range_check_ptr
        tempvar syscall_ptr : felt* = syscall_ptr
        tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #responder wins the round
        if res == 1:        
            #update piles
            update_pile(rp, challenger_rank)
            update_pile(rp, responder_rank)
            #draw new card for responder
            let (next_card) = draw_next_card()
            cards.write(rp, idx, next_card)            
            #draw new card for challenger
            let (next_card2) = draw_next_card()
            let (idx2) = card_idx.read(1)
            cards.write(ch, idx2, next_card2)
            #swap responder and challenger
            challenger.write(rp)
            responder.write(ch)
            #keep track of implicit arguments so they don't get revoked
            tempvar range_check_ptr = range_check_ptr       
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #challenger wins the round
        else:
            #update piles            
            update_pile(ch, challenger_rank)
            update_pile(ch, responder_rank) 
            #draw new card for challenger
            let (next_card) = draw_next_card()
            let (idx2) = card_idx.read(1)
            cards.write(ch, idx2, next_card)            
            #draw new card for responder
            let (next_card2) = draw_next_card()            
            cards.write(rp, idx, next_card2)
            #keep track of implicit arguments so they don't get revoked
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr 
        end
    else:
        let (tr) = trump.read()
        #responder wins the round
        if tr == responder_suit:
            #update piles
            update_pile(rp, challenger_rank)
            update_pile(rp, responder_rank)
            #draw new card for responder
            let (next_card) = draw_next_card()
            cards.write(rp, idx, next_card)            
            #draw new card for challenger
            let (next_card2) = draw_next_card()
            let (idx2) = card_idx.read(1)
            cards.write(ch, idx2, next_card2)
            #swap responder and challenger            
            challenger.write(rp)
            responder.write(ch)
            #keep track of implicit arguments so they don't get revoked
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #challenger wins the round
        else:
            #update piles
            update_pile(ch, challenger_rank)
            update_pile(ch, responder_rank)
            #draw new card for challenger
            let (next_card) = draw_next_card()
            let (idx2) = card_idx.read(1)
            cards.write(ch, idx2, next_card)            
            #draw new card for responder
            let (next_card2) = draw_next_card()            
            cards.write(rp, idx, next_card2)
            #keep track of implicit arguments so they don't get revoked
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        end
    end
    return ()
end


@external
func send_response1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx):
    alloc_locals

    assert (idx-1)*(idx-2)*(idx-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = responder.read()
    let (ch) = challenger.read()    
    assert sender = rp    

    let (ch_card) = challenge.read(1)
    let (rp_card) = cards.read(sender, idx)

    let (ch_suit, ch_rank) = unsigned_div_rem(ch_card, 9)    
    let (rp_suit, rp_rank) = unsigned_div_rem(rp_card, 9)
    let (tr_suit) =  trump.read()

    let (s) = is_not_zero(rp_suit - ch_suit)
    let (t)= is_not_zero(rp_suit - tr_suit)
    let (r) = is_le(ch_rank, rp_rank)

    let (wl) = win_loss.read(s,t,r)

    #responder wins
    if wl == 1:
        #update piles
        update_pile(rp, ch_rank)
        update_pile(rp, rp_rank)
        #draw new card for responder
        let (next_card) = draw_next_card()
        cards.write(rp, idx, next_card)            
        #draw new card for challenger
        let (next_card2) = draw_next_card()
        let (idx2) = card_idx.read(1)
        cards.write(ch, idx2, next_card2)
        #swap responder and challenger
        challenger.write(rp)
        responder.write(ch)
        #keep track of implicit arguments so they don't get revoked
        # tempvar range_check_ptr = range_check_ptr       
        # tempvar syscall_ptr : felt* = syscall_ptr
        # tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr    
    #challenger wins
    else:
        #update piles
        update_pile(ch, ch_rank)
        update_pile(ch, rp_rank)
        #draw new card for challenger
        let (next_card) = draw_next_card()
        let (idx2) = card_idx.read(1)
        cards.write(ch, idx2, next_card)            
        #draw new card for responder
        let (next_card2) = draw_next_card()            
        cards.write(rp, idx, next_card2)
        #keep track of implicit arguments so they don't get revoked
        # tempvar range_check_ptr = range_check_ptr
        # tempvar syscall_ptr : felt* = syscall_ptr
        # tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
    end


    #reset challenge
    challenge.write(1, NULL_VALUE)

    

    
    return ()
end


@external
func send_response2{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2):
    alloc_locals

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = responder.read()
    let (ch) = challenger.read()    
    assert sender = rp    

    let (ch_card1) = challenge.read(1)
    let (ch_card2) = challenge.read(2)
    let (rp_card1) = cards.read(sender, idx1)
    let (rp_card2) = cards.read(sender, idx2)

    let (ch_suit1, ch_rank1) = unsigned_div_rem(ch_card1, 9)    
    let (ch_suit2, ch_rank2) = unsigned_div_rem(ch_card2, 9)    

    let (rp_suit1, rp_rank1) = unsigned_div_rem(rp_card1, 9)
    let (rp_suit2, rp_rank2) = unsigned_div_rem(rp_card2, 9)

    #reset challenge
    challenge.write(1, NULL_VALUE)
    challenge.write(2, NULL_VALUE)

    return ()
end



@view
func get_challenge{ syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx) -> (res: felt):
    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (t) = challenge.read(idx)
    return (t)
end

@view
func get_trump{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (t) = trump.read()
    return (t)
end

@view
func get_pile{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(p:felt)->(res:felt):
    let (s) = piles.read(p)
    return (s)
end


@view
func get_player1{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = player1.read()
    return (p)
end

@view
func get_player2{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = player2.read()
    return (p)
end


@view
func get_challenger{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = challenger.read()
    return (p)
end

@view
func get_responder{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = responder.read()
    return (p)
end


@view
func get_head{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (res) = head.read()
    return (res)
end

func draw_next_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (idx) = head.read()
    assert_nn_le(idx, 35)
    let (crd) = deck.read(idx)
    head.write(idx+1)
    return(crd)
end

func update_pile{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(player, rank):
    let (res) = piles.read(player)    
    let (pts) = points.read(rank)
    piles.write(player, res + pts)
    return()
end

@view
func get_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(player, idx) -> (res: felt):
    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (res) = cards.read(player, idx)
    return(res)
end



@constructor
func constructor{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():

    
    win_loss.write(1,1,1,value=0)
    win_loss.write(1,0,1,value=1)    
    win_loss.write(1,1,0,value=0)
    win_loss.write(1,0,0,value=1)    
    win_loss.write(0,1,1,value=1)
    win_loss.write(0,0,1,value=1)    
    win_loss.write(0,1,0,value=0)
    win_loss.write(0,0,0,value=0)

    deck.write(0,value=C6)
    deck.write(1,value=H10)
    deck.write(2,value=CA)
    deck.write(3,value=SQ)
    deck.write(4,value=D7)
    deck.write(5,value=CJ)
    deck.write(6,value=CK)
    deck.write(7,value=C8)
    deck.write(8,value=HK)
    deck.write(9,value=HQ)
    deck.write(10,value=S9)
    deck.write(11,value=S8)
    deck.write(12,value=SK)
    deck.write(13,value=D9)
    deck.write(14,value=SA)
    deck.write(15,value=H7)
    deck.write(16,value=C9)
    deck.write(17,value=D10)
    deck.write(18,value=S7)
    deck.write(19,value=HA)
    deck.write(20,value=D6)
    deck.write(21,value=DJ)
    deck.write(22,value=S6)
    deck.write(23,value=SJ)
    deck.write(24,value=DK)
    deck.write(25,value=DA)
    deck.write(26,value=C10)
    deck.write(27,value=CQ)
    deck.write(28,value=H9)
    deck.write(29,value=D8)
    deck.write(30,value=H6)
    deck.write(31,value=HJ)
    deck.write(32,value=C7)
    deck.write(33,value=S10)
    deck.write(34,value=H8)
    deck.write(35,value=DQ)

    points.write(0,value=0)
    points.write(1,value=0)
    points.write(2,value=0)
    points.write(3,value=0)
    points.write(4,value=10)
    points.write(5,value=2)
    points.write(6,value=3)
    points.write(7,value=4)
    points.write(8,value=11)
    return()
end







