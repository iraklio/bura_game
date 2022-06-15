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
    assert_not_equal,
    assert_lt,
    sqrt
    )


const WINNING_SCORE = 21
const NULL_CARD = 99
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
func round_point()->(c:felt):
end

@storage_var
func round_point_caller()->(c:felt):
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

@storage_var
func scores(player:felt) -> (score:felt):
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

    challenge.write(1, NULL_CARD)
    challenge.write(2, NULL_CARD)
    challenge.write(3, NULL_CARD)

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
    assert_not_equal(cc, NULL_CARD)

    challenge.write(1,cc)
    cards.write(sender, idx, NULL_CARD)
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
    let (c2) = cards.read(sender, idx2)

    assert_not_equal(c1, NULL_CARD)
    assert_not_equal(c2, NULL_CARD)

    let (c1_suit, _) = unsigned_div_rem(c1, 9)    
    let (c2_suit, _) = unsigned_div_rem(c2, 9)
    assert c1_suit = c2_suit

    challenge.write(1,c1)
    card_idx.write(1, idx1)
    cards.write(sender, idx1, NULL_CARD)
    
    challenge.write(2,c2)
    card_idx.write(2, idx2)    
    cards.write(sender, idx2, NULL_CARD)
    return()
end


@external
func send_challenge3{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2, idx3) -> ():

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert (idx3-1)*(idx3-2)*(idx3-3) = 0

    let (sender) = get_caller_address()
    let (ch) = challenger.read()
    assert sender = ch

    let (c1) = cards.read(sender, idx1)
    let (c2) = cards.read(sender, idx2)
    let (c3) = cards.read(sender, idx3)

    assert_not_equal(c1, NULL_CARD)
    assert_not_equal(c2, NULL_CARD)
    assert_not_equal(c3, NULL_CARD)

    let (c1_suit, _) = unsigned_div_rem(c1, 9)    
    let (c2_suit, _) = unsigned_div_rem(c2, 9)
    let (c3_suit, _) = unsigned_div_rem(c3, 9)

    assert c1_suit = c2_suit
    assert c2_suit = c3_suit

    challenge.write(1,c1)
    card_idx.write(1, idx1)
    cards.write(sender, idx1, NULL_CARD)
    
    challenge.write(2,c2)
    card_idx.write(2, idx2)    
    cards.write(sender, idx2, NULL_CARD)

    challenge.write(3,c3)
    card_idx.write(3, idx3)    
    cards.write(sender, idx3, NULL_CARD)
    return()
end

@external
func send_response1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx)->(c1:felt):
    alloc_locals

    assert (idx-1)*(idx-2)*(idx-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = responder.read()
    let (ch) = challenger.read()    
    assert sender = rp    

    let (ch_card) = challenge.read(1)
    let (rp_card) = cards.read(sender, idx)

    assert_not_equal(rp_card, NULL_CARD)

    let (_, ch_rank) = unsigned_div_rem(ch_card, 9)    
    let (_, rp_rank) = unsigned_div_rem(rp_card, 9)

    let (wl) = win_loss_calc(ch_card, rp_card)

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
        return(rp_card)
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
        return(NULL_CARD)
    end
    #reset challenge
    #challenge.write(1, NULL_CARD)
    #return ()
end


@external
func send_response2{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2)->(c1:felt,c2:felt):
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

    assert_not_equal(rp_card1, NULL_CARD)
    assert_not_equal(rp_card2, NULL_CARD)

    let (tr_suit) = trump.read()

    let ( _, ch_rank1) = unsigned_div_rem(ch_card1, 9)    
    let ( _, ch_rank2) = unsigned_div_rem(ch_card2, 9)    

    let ( _, rp_rank1) = unsigned_div_rem(rp_card1, 9)
    let ( _, rp_rank2) = unsigned_div_rem(rp_card2, 9)

    let (wl11) = win_loss_calc(ch_card1, rp_card1)
    let (wl22) = win_loss_calc(ch_card2, rp_card2)

    let (wl12) = win_loss_calc(ch_card1, rp_card2)
    let (wl21) = win_loss_calc(ch_card2, rp_card1)    
    let (wl) = max(wl11 + wl22, wl12 + wl21)

    #responder wins
    if wl == 2:
        #update piles
        update_pile(rp, ch_rank1)
        update_pile(rp, rp_rank1)
        update_pile(rp, ch_rank2)
        update_pile(rp, rp_rank2)
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()
        cards.write(rp, idx1, next_card1)            
        #draw 1st new card for challenger
        let (other_next_card1) = draw_next_card()
        let (other_idx1) = card_idx.read(1)
        cards.write(ch, other_idx1, other_next_card1)
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()
        cards.write(rp, idx2, next_card2)            
        #draw 2nd new card for challenger
        let (other_next_card2) = draw_next_card()
        let (other_idx2) = card_idx.read(2)
        cards.write(ch, other_idx2, other_next_card2)
        #swap responder and challenger
        challenger.write(rp)
        responder.write(ch)        
        return(rp_card1, rp_card2)
    #challenger wins
    else:
        #update piles
        update_pile(ch, ch_rank1)
        update_pile(ch, rp_rank1)
        update_pile(ch, ch_rank2)
        update_pile(ch, rp_rank2)
        #draw 1st new card for challenger
        let (other_next_card1) = draw_next_card()
        let (other_idx1) = card_idx.read(1)
        cards.write(ch, other_idx1, other_next_card1)            
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()            
        cards.write(rp, idx1, next_card1)
        #draw 2st new card for challenger
        let (other_next_card2) = draw_next_card()
        let (other_idx2) = card_idx.read(2)
        cards.write(ch, other_idx2, other_next_card2)            
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()            
        cards.write(rp, idx2, next_card2)
        return(NULL_CARD,NULL_CARD)        
    end    
    
end


@external
func send_response3{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2, idx3)->(c1:felt,c2:felt,c3:felt):
    alloc_locals
    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert (idx3-1)*(idx3-2)*(idx3-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = responder.read()
    let (ch) = challenger.read()    
    assert sender = rp    

    let ( local ch_card1) = challenge.read(1)
    let ( local ch_card2) = challenge.read(2)
    let ( local ch_card3) = challenge.read(3)

    let (rp_card1) = cards.read(sender, idx1)
    let (rp_card2) = cards.read(sender, idx2)
    let (rp_card3) = cards.read(sender, idx3)

    assert_not_equal(rp_card1, NULL_CARD)
    assert_not_equal(rp_card2, NULL_CARD)
    assert_not_equal(rp_card3, NULL_CARD)

    let (tr_suit) = trump.read()

    let ( _, ch_rank1) = unsigned_div_rem(ch_card1, 9)    
    let ( _, ch_rank2) = unsigned_div_rem(ch_card2, 9)    
    let ( _, ch_rank3) = unsigned_div_rem(ch_card3, 9)    

    let ( _, rp_rank1) = unsigned_div_rem(rp_card1, 9)
    let ( _, rp_rank2) = unsigned_div_rem(rp_card2, 9)
    let ( _, rp_rank3) = unsigned_div_rem(rp_card3, 9)

    # 1,2,3 # 1,3,2
    # 2,1,3 # 2,3,1
    # 3,1,2 # 3,2,1
    let (wl11) = win_loss_calc(ch_card1, rp_card1)
    let (wl22) = win_loss_calc(ch_card2, rp_card2)
    let (wl33) = win_loss_calc(ch_card3, rp_card3)    
    let (wl23) = win_loss_calc(ch_card2, rp_card3)
    let (wl32) = win_loss_calc(ch_card3, rp_card2)    
    let (wl12) = win_loss_calc(ch_card1, rp_card2)
    let (wl21) = win_loss_calc(ch_card2, rp_card1)           
    let (wl31) = win_loss_calc(ch_card3, rp_card1)
    let (wl13) = win_loss_calc(ch_card1, rp_card3)    

    let (wl_1) = max(wl11 + wl22 + wl33, wl11 + wl23 + wl32)
    let (wl_2) = max(wl12 + wl21 + wl33, wl12 + wl23 + wl31)
    let (wl_3) = max(wl13 + wl21 + wl32, wl13 + wl22 + wl31)

    let (wl_12) = max(wl_1, wl_2)
    let (wl_23) = max(wl_2, wl_3)

    let (wl) = max(wl_12, wl_23)

    #responder wins
    if wl == 3:
        #update piles
        update_pile(rp, ch_rank1)
        update_pile(rp, rp_rank1)
        update_pile(rp, ch_rank2)
        update_pile(rp, rp_rank2)
        update_pile(rp, ch_rank3)
        update_pile(rp, rp_rank3)
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()
        cards.write(rp, idx1, next_card1)            
        #draw 1st new card for challenger
        let (other_next_card1) = draw_next_card()
        let (other_idx1) = card_idx.read(1)
        cards.write(ch, other_idx1, other_next_card1)
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()
        cards.write(rp, idx2, next_card2)            
        #draw 2nd new card for challenger
        let (other_next_card2) = draw_next_card()
        let (other_idx2) = card_idx.read(2)
        cards.write(ch, other_idx2, other_next_card2)
        #draw 3nd new card for responder
        let (next_card3) = draw_next_card()
        cards.write(rp, idx3, next_card3)            
        #draw 3nd new card for challenger
        let (other_next_card3) = draw_next_card()
        let (other_idx3) = card_idx.read(3)
        cards.write(ch, other_idx3, other_next_card3)
        #swap responder and challenger
        challenger.write(rp)
        responder.write(ch)
        return(rp_card1, rp_card2, rp_card3)        
    #challenger wins
    else:
        #update piles
        update_pile(ch, ch_rank1)
        update_pile(ch, rp_rank1)
        update_pile(ch, ch_rank2)
        update_pile(ch, rp_rank2)
        update_pile(ch, ch_rank3)
        update_pile(ch, rp_rank3)

        #draw 1st new card for challenger
        let (other_next_card1) = draw_next_card()
        let (other_idx1) = card_idx.read(1)
        cards.write(ch, other_idx1, other_next_card1)            
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()            
        cards.write(rp, idx1, next_card1)

        #draw 2st new card for challenger
        let (other_next_card2) = draw_next_card()
        let (other_idx2) = card_idx.read(2)
        cards.write(ch, other_idx2, other_next_card2)                    
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()            
        cards.write(rp, idx2, next_card2)        

        #draw 3rd new card for challenger
        let (other_next_card3) = draw_next_card()
        let (other_idx3) = card_idx.read(3)
        cards.write(ch, other_idx3, other_next_card3)            
        #draw 3rd new card for responder
        let (next_card3) = draw_next_card()            
        cards.write(rp, idx3, next_card3)
        return(NULL_CARD,NULL_CARD,NULL_CARD)
    end    
end

#Round point can be raised up to 6
@external
func raise_round_point{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    let (sender) = get_caller_address()
    let (previous_caller) = round_point_caller.read()        
    assert_not_equal(sender, previous_caller)
    let (previous_round_point) = round_point.read()
    assert_lt(previous_round_point,6)
    round_point.write(previous_round_point + 1)
    round_point_caller.write(sender)
    return()
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
func get_round_point{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = round_point.read()
    return (p)
end

@view
func get_round_point_caller{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = round_point_caller.read()
    return (p)
end

@view
func get_head{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (res) = head.read()
    return (res)
end

func draw_next_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (idx) = head.read()
    if idx == 36:
        return (NULL_CARD)
    end    
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

func win_loss_calc{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(ch_card,rp_card) -> (wl:felt):
    alloc_locals
    let (ch_suit, ch_rank) = unsigned_div_rem(ch_card, 9)    
    let (rp_suit, rp_rank) = unsigned_div_rem(rp_card, 9)
    let (tr_suit) =  trump.read()

    let (local s) = is_not_zero(rp_suit - ch_suit)
    let (local t) = is_not_zero(rp_suit - tr_suit)
    let (local r) = is_le(ch_rank, rp_rank)

    let (wl) = win_loss.read(s,t,r)
    return(wl=wl)
end

func max{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(a,b) -> (res:felt):    
    let (r) = is_le(a, b)
    if r==1:
        return(b)
    else:
        return(a)
    end
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







