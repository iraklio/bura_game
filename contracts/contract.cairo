# Declare this file as a StarkNet contract.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.cairo_builtins import BitwiseBuiltin

from starkware.cairo.common.bitwise import bitwise_and
from starkware.starknet.common.syscalls import get_caller_address
from starkware.cairo.common.hash import hash2
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


const WINNING_SCORE = 11
const NULL_CARD = 99
const TWO_TO_128_MINUS_ONE = 340282366920938463463374607431768211455 #2^128-1 
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
func round_point_challenge_sent()->(c:felt):
end

@storage_var
func round_point_caller()->(c:felt):
end

@storage_var
func cards(player:felt, idx:felt)->(c:felt):
end

# @storage_var
# func challenge(idx:felt)->(c:felt):
# end

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
func mover()->(address:felt):
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


@storage_var
func seed1() -> (seed:felt):
end

@storage_var
func seed2() -> (seed:felt):
end

@external
func join_game{ syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(seed):

    let (sender) = get_caller_address()
    let (p1) = player1.read()
    if p1 == 0:
        player1.write(sender)
        seed1.write(seed)
        return()
    else:
        let (p2) = player2.read()
        if p2 == 0:            
            player2.write(sender)
            seed2.write(seed)
            start_game()
            return()
        else:
            return()        
        end
    end
end

@external
func leave_game{syscall_ptr : felt*,  pedersen_ptr : HashBuiltin*, range_check_ptr}():

    let (sender) = get_caller_address()
    let (p1) = player1.read()
    let (p2) = player2.read()
    assert p2 = 0
    assert p1 = sender
    player1.write(0)
    return()
end


func start_game{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}():
    alloc_locals

    let (local p1) = player1.read()
    let (local p2) = player2.read()

    fisher_yates_shuffle()
    
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

    #randomly choose the challenger
    let (s1) = seed1.read()
    let (d1) = bitwise_and(s1, TWO_TO_128_MINUS_ONE)
    let (_, odd_or_even) = unsigned_div_rem(d1,2)
    if odd_or_even == 0:
        mover.write(p1)        
    else:
        mover.write(p2)        
    end

    #randomly choose the the trump
    let (s2) = seed2.read()
    let (d2) = bitwise_and(s2, TWO_TO_128_MINUS_ONE)
    let (_, trump_idx) = unsigned_div_rem(d2,36)
    let (t) = deck.read(trump_idx)
    let (div,_) = unsigned_div_rem(t,9)
    trump.write(div)

    return()
end

@external
func send_challenge1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx:felt) -> ():

    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (sender) = get_caller_address()
    let (ch) = mover.read()    
    assert sender = ch
    card_idx.write(1, idx)
    let (rp) = get_other()
    mover.write(rp)
    return()
end

@external
func send_challenge2{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2) -> ():

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert_not_equal(idx1, idx2)

    let (sender) = get_caller_address()
    let (ch) = mover.read()
    assert sender = ch

    let (c1) = cards.read(sender, idx1)
    let (c2) = cards.read(sender, idx2)

    let (c1_suit, _) = unsigned_div_rem(c1, 9)    
    let (c2_suit, _) = unsigned_div_rem(c2, 9)
    assert c1_suit = c2_suit

    card_idx.write(1, idx1)
    card_idx.write(2, idx2)

    let (rp) = get_other()
    mover.write(rp)
    return()
end

@external
func send_challenge3{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx1, idx2, idx3) -> ():

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert (idx3-1)*(idx3-2)*(idx3-3) = 0

    assert_not_equal(idx1, idx2)
    assert_not_equal(idx2, idx3)
    assert_not_equal(idx1, idx3)

    let (sender) = get_caller_address()
    let (ch) = mover.read()
    assert sender = ch

    let (c1) = cards.read(sender, idx1)
    let (c2) = cards.read(sender, idx2)
    let (c3) = cards.read(sender, idx3)

    let (c1_suit, _) = unsigned_div_rem(c1, 9)    
    let (c2_suit, _) = unsigned_div_rem(c2, 9)
    let (c3_suit, _) = unsigned_div_rem(c3, 9)

    assert c1_suit = c2_suit
    assert c2_suit = c3_suit

    card_idx.write(1, idx1)
    card_idx.write(2, idx2)
    card_idx.write(3, idx3)    
    
    let (rp) = get_other()
    mover.write(rp)
    return()
end

@external
func send_response1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(idx)->(c1:felt):
    alloc_locals

    assert (idx-1)*(idx-2)*(idx-3) = 0
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = mover.read()
    let (ch) = get_other()    
    assert sender = rp    

    let (idx2) = card_idx.read(1)
    let (ch_card) = cards.read(ch, idx2)
    let (rp_card) = cards.read(rp, idx)

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
        cards.write(ch, idx2, next_card2)
        return(rp_card)
    #challenger wins
    else:
        #update piles
        update_pile(ch, ch_rank)
        update_pile(ch, rp_rank)
        #draw new card for challenger
        let (next_card) = draw_next_card()        
        cards.write(ch, idx2, next_card)            
        #draw new card for responder
        let (next_card2) = draw_next_card()            
        cards.write(rp, idx, next_card2)
        mover.write(ch)
        return(NULL_CARD)
    end    
end

@external
func send_response2{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(idx1, idx2)->(c1:felt,c2:felt):
    alloc_locals

    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert_not_equal(idx1, idx2)

    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = mover.read()
    let (ch) = get_other()    
    assert sender = rp    

    let (other_idx1) = card_idx.read(1)
    let (other_idx2) = card_idx.read(2)

    let (ch_card1) = cards.read(ch, other_idx1)
    let (ch_card2) = cards.read(ch, other_idx2)
    let (rp_card1) = cards.read(rp, idx1)
    let (rp_card2) = cards.read(rp, idx2)

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
        cards.write(ch, other_idx1, other_next_card1)
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()
        cards.write(rp, idx2, next_card2)            
        #draw 2nd new card for challenger
        let (other_next_card2) = draw_next_card()        
        cards.write(ch, other_idx2, other_next_card2)        
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
        cards.write(ch, other_idx1, other_next_card1)            
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()            
        cards.write(rp, idx1, next_card1)
        #draw 2st new card for challenger
        let (other_next_card2) = draw_next_card()        
        cards.write(ch, other_idx2, other_next_card2)            
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()      
        cards.write(rp, idx2, next_card2)
        mover.write(ch)      
        return(NULL_CARD,NULL_CARD)        
    end    
    
end

@external
func send_response3{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(idx1, idx2, idx3)->(c1:felt,c2:felt,c3:felt):
    alloc_locals
    assert (idx1-1)*(idx1-2)*(idx1-3) = 0
    assert (idx2-1)*(idx2-2)*(idx2-3) = 0
    assert (idx3-1)*(idx3-2)*(idx3-3) = 0
    assert_not_equal(idx1, idx2)
    assert_not_equal(idx2, idx3)
    assert_not_equal(idx1, idx3)
    #make sure response was sent by the responder
    let (sender) = get_caller_address()
    let (rp) = mover.read()
    let (ch) = get_other()    
    assert sender = rp

    let (other_idx1) = card_idx.read(1)
    let (other_idx2) = card_idx.read(2)    
    let (other_idx3) = card_idx.read(3)

    let ( local ch_card1) = cards.read(ch, other_idx1)
    let ( local ch_card2) = cards.read(ch, other_idx2)
    let ( local ch_card3) = cards.read(ch, other_idx3)

    let (rp_card1) = cards.read(rp, idx1)
    let (rp_card2) = cards.read(rp, idx2)
    let (rp_card3) = cards.read(rp, idx3)

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
        cards.write(ch, other_idx1, other_next_card1)
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()
        cards.write(rp, idx2, next_card2)            
        #draw 2nd new card for challenger
        let (other_next_card2) = draw_next_card()        
        cards.write(ch, other_idx2, other_next_card2)
        #draw 3nd new card for responder
        let (next_card3) = draw_next_card()
        cards.write(rp, idx3, next_card3)            
        #draw 3nd new card for challenger
        let (other_next_card3) = draw_next_card()        
        cards.write(ch, other_idx3, other_next_card3)               
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
        cards.write(ch, other_idx1, other_next_card1)            
        #draw 1st new card for responder
        let (next_card1) = draw_next_card()            
        cards.write(rp, idx1, next_card1)

        #draw 2st new card for challenger
        let (other_next_card2) = draw_next_card()        
        cards.write(ch, other_idx2, other_next_card2)                    
        #draw 2nd new card for responder
        let (next_card2) = draw_next_card()            
        cards.write(rp, idx2, next_card2)
        #draw 3rd new card for challenger
        let (other_next_card3) = draw_next_card()        
        cards.write(ch, other_idx3, other_next_card3)            
        #draw 3rd new card for responder
        let (next_card3) = draw_next_card()            
        cards.write(rp, idx3, next_card3)
        mover.write(ch)                
        return(NULL_CARD,NULL_CARD,NULL_CARD)
    end    
end

func round_restart{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(round_win):
    #TO DO. Implement logic of what happens when game is over, and player wins
    alloc_locals

    round_point.write(1)
    round_point_challenge_sent.write(0)
    round_point_caller.write(0)    

    let (local m) = mover.read()   
    let (local o) = get_other()

    piles.write(m,value=0)    
    piles.write(o,value=0)    
    head.write(0)
    fisher_yates_shuffle()
    
    let (c1) = draw_next_card()    
    let (c2) = draw_next_card()
    let (c3) = draw_next_card()
    let (c4) = draw_next_card()
    let (c5) = draw_next_card()
    let (c6) = draw_next_card()

    if round_win == 1:        
        cards.write(m, 1, c1)
        cards.write(o, 1, c2)
        cards.write(m, 2, c3)
        cards.write(o, 2, c4)   
        cards.write(m, 3, c5)    
        cards.write(o, 3, c6)
    else:
        mover.write(o)
        cards.write(o, 1, c1)
        cards.write(m, 1, c2)
        cards.write(o, 2, c3)
        cards.write(m, 2, c4)   
        cards.write(o, 3, c5)    
        cards.write(m, 3, c6)
    end

    #randomly choose the the trump
    let (s2) = seed2.read()
    let (d2) = bitwise_and(s2, TWO_TO_128_MINUS_ONE)
    let (_, trump_idx) = unsigned_div_rem(d2,36)
    let (t) = deck.read(trump_idx)
    let (div,_) = unsigned_div_rem(t,9)
    trump.write(div)
    return()
end

#mover can claim the win at any time during the round. 
@external
func claim_win{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}()->(round_win:felt, game_win:felt):    
    alloc_locals
    let (caller) = get_caller_address()
    let (m) = mover.read()    
    assert caller = m

    let (local pile) = piles.read(m)
    let (local round_win) = is_le(31, pile)
    let (local rpts) = round_point.read()
    let (local score) = scores.read(m)

    if round_win == 1:        
        scores.write(m, score + rpts)
    else:
        scores.write(m, score - rpts)                
    end

    let (local score2) = scores.read(m)
    let (local game_win) = is_le(WINNING_SCORE, score2)

    if game_win == 1:
        return(round_win, game_win)
    else:
        round_restart(round_win)   
        return(round_win, game_win)     
    end
end

#Round point can be raised up to 6
# @external
# func raise_round_point_challenge{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
#     let (sender) = get_caller_address()
#     let (previous_caller) = round_point_caller.read()
#     assert_not_equal(sender, previous_caller)
#     let (previous_round_point) = round_point.read()
#     assert_lt(previous_round_point,6)
#     round_point_caller.write(sender)
#     round_point_challenge_sent.write(1)
#     return()
# end

# @external
# func raise_round_point_responce{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(resp):

#     assert resp*(resp-1) = 0
#     let (caller) = get_caller_address()
#     let (previous_caller) = round_point_caller.read()   
#     assert_not_equal(caller, previous_caller)
#     let (previous_round_point) = round_point.read()

#     if resp == 1:
#         round_point.write(previous_round_point + 1)
#         round_point_challenge_sent.write(0)
#     else:
#         #Responder does not accept the raise. Round is over.
#         assign_round_win_loss_raise_not_accepted(previous_caller)
#     end   
    
#     return()
# end


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
func get_score{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(p:felt)->(res:felt):
    let (s) = scores.read(p)
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
func get_mover{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = mover.read()
    return (p)
end

@view
func get_other{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (m) = mover.read()
    let (p1) = player1.read()
    let (p2) = player2.read()
    if m == p1:
        return (p2)
    else:
        return (p1)
    end    
end

@view
func get_round_point{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = round_point.read()
    return (p)
end

@view
func get_round_point_challenge_sent{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (p) = round_point_challenge_sent.read()
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

func draw_next_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}() -> (res: felt):
    alloc_locals
    let (local idx) = head.read()        
    let (local crd) = deck.read(idx)    
    head.write(idx+1)

    if idx == 35:
        tempvar syscall_ptr = syscall_ptr
        tempvar pedersen_ptr = pedersen_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar bitwise_ptr = bitwise_ptr
        head.write(0)        
        fisher_yates_shuffle()        
    else:
        tempvar syscall_ptr = syscall_ptr
        tempvar pedersen_ptr = pedersen_ptr
        tempvar range_check_ptr = range_check_ptr
        tempvar bitwise_ptr = bitwise_ptr
    end

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

func fisher_yates_shuffle{ syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}():
    alloc_locals
    let (s1) = seed1.read()
    let (s2) = seed2.read()
    let (h1) = fisher_yates_helper(s1, s2, 35, 34, 33, 32, 31)
    let (h2) = fisher_yates_helper(s2, h1, 30, 29, 28, 27, 26)
    let (h3) = fisher_yates_helper(h1, h2, 25, 24, 23, 22, 21)
    let (h4) = fisher_yates_helper(h2, h3, 20, 19, 18, 17, 16)
    let (h5) = fisher_yates_helper(h3, h4, 15, 14, 13, 12, 11)
    let (h6) = fisher_yates_helper(h4, h5, 10,  9,  8,  7,  6)
    let (h7) = fisher_yates_helper(h5, h6,  5,  4,  3,  2,  1)
    #update seeds for need round shuffle
    seed1.write(h6)
    seed2.write(h7)
    return ()
end

func fisher_yates_helper{ syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr, bitwise_ptr: BitwiseBuiltin*}(x,y, i1, i2, i3, i4, i5) -> (h):
    alloc_locals
    let (h) = hash2{hash_ptr = pedersen_ptr}(x,y)
    let (d0) = bitwise_and(h, TWO_TO_128_MINUS_ONE)
    let (d1, r1) = unsigned_div_rem(d0,i1)
    swap_cards(r1, i1)
    let (d2, r2) = unsigned_div_rem(d1,i2)
    swap_cards(r2, i2)
    let (d3, r3) = unsigned_div_rem(d2,i3)
    swap_cards(r3, i3)
    let (d4, r4) = unsigned_div_rem(d3,i4)
    swap_cards(r4, i4)
    let (d5, r5) = unsigned_div_rem(d4,i5)    
    swap_cards(r5, i5)
    return (h=h)
end

func swap_cards{ syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(i,j):

    let (a_i) = deck.read(i)
    let (a_j) = deck.read(j)
    deck.write(i, a_j)
    deck.write(j, a_i)
    return()
end

@view
func get_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx) -> (res: felt):
    assert (idx-1)*(idx-2)*(idx-3) = 0    
    let (sender) = get_caller_address()    
    let (res) = cards.read(sender, idx)
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

    round_point.write(1)

    return()
end

