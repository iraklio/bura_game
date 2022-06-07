# Declare this file as a StarkNet contract.
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

from starkware.starknet.common.syscalls import (
    get_caller_address
)

from starkware.cairo.common.math_cmp import is_le, is_in_range
from starkware.cairo.common.math import ( 
    abs_value, 
    assert_nn, 
    assert_nn_le, 
    assert_le, 
    unsigned_div_rem, 
    signed_div_rem, 
    assert_in_range, 
    sqrt
    )


const NULL_VALUE = 99


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
    return()
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

    let (challenger_card) = challenge.read(1)
    let (responder_card) = cards.read(sender, idx)

    let (challenger_suit, challenger_rank) = unsigned_div_rem(challenger_card, 9)    
    let (responder_suit, responder_rank) = unsigned_div_rem(responder_card, 9)

    #reset challenge and card
    challenge.write(1, NULL_VALUE)
    cards.write(sender, idx, NULL_VALUE) 

    if challenger_suit == responder_suit:        
        let (res) = is_le(challenger_rank, responder_rank)
        tempvar range_check_ptr = range_check_ptr
        tempvar syscall_ptr : felt* = syscall_ptr
        tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #responder wins the round
        if res == 1:
            update_pile(rp, challenger_rank)
            update_pile(rp, responder_rank) 
            tempvar range_check_ptr = range_check_ptr       
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #challenger wins the round
        else:            
            update_pile(ch, challenger_rank)
            update_pile(ch, responder_rank) 
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr 
        end
    else:
        let (tr) = trump.read()
        #responder wins the round
        if tr == responder_suit:
            update_pile(rp, challenger_rank)
            update_pile(rp, responder_rank) 
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        #challenger wins the round
        else:
            update_pile(ch, challenger_rank)
            update_pile(ch, responder_rank) 
            tempvar range_check_ptr = range_check_ptr
            tempvar syscall_ptr : felt* = syscall_ptr
            tempvar pedersen_ptr : HashBuiltin* = pedersen_ptr
        end
    end
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



@constructor
func constructor{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    deck.write(0,value=0)
    deck.write(1,value=22)
    deck.write(2,value=8)
    deck.write(3,value=33)
    deck.write(4,value=10)
    deck.write(5,value=5)
    deck.write(6,value=7)
    deck.write(7,value=2)
    deck.write(8,value=25)
    deck.write(9,value=24)
    deck.write(10,value=30)
    deck.write(11,value=29)
    deck.write(12,value=34)
    deck.write(13,value=12)
    deck.write(14,value=35)
    deck.write(15,value=19)
    deck.write(16,value=3)
    deck.write(17,value=13)
    deck.write(18,value=28)
    deck.write(19,value=26)
    deck.write(20,value=9)
    deck.write(21,value=14)
    deck.write(22,value=27)
    deck.write(23,value=32)
    deck.write(24,value=16)
    deck.write(25,value=17)
    deck.write(26,value=4)
    deck.write(27,value=6)
    deck.write(28,value=21)
    deck.write(29,value=11)
    deck.write(30,value=18)
    deck.write(31,value=23)
    deck.write(32,value=1)
    deck.write(33,value=31)
    deck.write(34,value=20)
    deck.write(35,value=15)

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







