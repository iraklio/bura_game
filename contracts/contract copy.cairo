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
func card1(idx:felt)->(c:felt):
end

@storage_var
func card2(idx:felt)->(c:felt):
end

@storage_var
func challenge( idx:felt)->(c:felt):
end

@storage_var
func pile1() -> (pile:felt):
end

@storage_var
func pile2() -> (pile:felt):
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

    let (p1) = player1.read()
    let (p2) = player2.read()

    challenger.write(p1)
    responder.write(p2)
    let (t) = deck.read(11)
    let (div,_) = unsigned_div_rem(t,9)
    trump.write(div)

    let (c1) = draw_next_card()
    card1.write(1, c1)

    let (c2) = draw_next_card()
    card2.write(1, c2)

    let (c3) = draw_next_card()
    card1.write(2, c3)

    let (c4) = draw_next_card()
    card2.write(2,c4)

    let (c5) = draw_next_card()
    card1.write(3,c5)

    let (c6) = draw_next_card()
    card2.write(3,c6)

    challenge.write(1, NULL_VALUE)
    challenge.write(2, NULL_VALUE)
    challenge.write(3, NULL_VALUE)

    return()
end

@external
func send_challenge1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx:felt) -> ():

    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (sender) = get_caller_address()
    let (ch) = challenger.read()
    let (p1) = player1.read()
    assert sender = ch

    let (cc) = card1.read(idx)
    challenge.write(1,cc)
    card1.write(idx,NULL_VALUE)
    #return()
    
    # if sender == p1:
    #     let (cc) = card1.read(idx)
    #     challenge.write(1,cc)
    #     card1.write(idx,NULL_VALUE)
    #     return()
    # else:
    #     let (cc) = card2.read(1)
    #     challenge.write(1,cc)
    #     card2.write(1,NULL_VALUE)
    #     return()
    # end 
    return()
end


@external
func send_response1{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(idx:felt):
    #alloc_locals
    assert (idx-1)*(idx-2)*(idx-3) = 0
    let (_reponder) = get_caller_address()
    let (rp) = responder.read()
    let (p1) = player1.read()
    let (p2) = player2.read()
    assert _reponder = rp

    #make sure that its single card challenge
    let (ch1) = challenge.read(1)
    let (ch2) = challenge.read(2)
    let (ch3) = challenge.read(3)
    assert_nn_le(ch1,35)
    assert ch2 = NULL_VALUE
    assert ch3 = NULL_VALUE

    # local syscall_ptr : felt* = syscall_ptr

    let (cc1) = challenge.read(1)
    let (suit1, rank1) = unsigned_div_rem(cc1, 9)

    if idx == 1:
        #if rp == p1:            
        # let (cc2) = card1_1.read()
            #tempvar syscall_ptr = syscall_ptr
            # let (suit2, rank2) = unsigned_div_rem(cc2, 9)
            # if suit1 == suit2:
            #     let (res) = is_le(rank1, rank2)
            #     #responder wins the round
            #     if res == 1: 
            #         card1_1.write(NULL_VALUE)
            #         challenge_1.write(NULL_VALUE)
            #         update_pile(p1, cc1)
            #         update_pile(p1, cc2)
            #    #     return (show=1)
            #     else:
            #   #      return (show=0)
            #     end
            # end            
        #else:            
            #let ( cc2) = card2_1.read()
            #tempvar syscall_ptr = syscall_ptr
            # let ( suit2, rank2) = unsigned_div_rem(cc2, 9)
            # if suit1 == suit2:
            #     let (res) = is_le(rank1, rank2)
            #     #responder wins the round
            #     if res == 1:
            #         card2_1.write(NULL_VALUE)
            #         challenge_1.write(NULL_VALUE)
            #         update_pile(p2, cc1)
            #         update_pile(p2, cc2)
            #  #       return (show=1)
            #     else:
            # #        return (show=0)
            #     end
            # end
        #end
    else:

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


func update_pile{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(player:felt, card:felt) -> ():    
    return()
end


func draw_next_card{syscall_ptr:felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (res: felt):
    let (idx) = head.read()
    assert_nn_le(idx, 35)
    let (crd) = deck.read(idx)
    head.write(idx+1)
    return(crd)
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
    return()
end







