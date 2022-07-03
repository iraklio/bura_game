
from starkware.cairo.common.registers import get_label_location

from starkware.cairo.common.math_cmp import is_le, is_in_range, is_not_zero
from starkware.cairo.common.math import unsigned_div_rem


func max{range_check_ptr}(a,b) -> (res:felt):    
    let (r) = is_le(a, b)
    if r==1:
        return(b)
    else:
        return(a)
    end
end


func win_loss_calc{range_check_ptr}(c1, c2, trump) -> (wl:felt):
    alloc_locals
    let (s1, r1) = unsigned_div_rem(c1, 9)    
    let (s2, r2) = unsigned_div_rem(c2, 9)    

    let (local s) = is_not_zero(s2 - s1)
    let (local t) = is_not_zero(s2 - trump)
    let (local r) = is_le(r1, r2)

    let win_loss_key = 2 * 2 * s + 2 * t + r

    let (wl) = win_loss_lookup(win_loss_key)
    return(wl=wl)
end


func win_loss_lookup(win_loss_key) -> (wl:felt):
    
    let (data_address) = get_label_location(data)
    return ([data_address + win_loss_key])

    data:
    dw 0
    dw 1
    dw 0
    dw 1
    dw 1
    dw 1
    dw 0
    dw 0 
end

func points_lookup(rank) -> (pts:felt):
    
    let (data_address) = get_label_location(data)
    return ([data_address + rank])

    data:
    dw 0   # 6
    dw 0   # 7
    dw 0   # 8
    dw 0   # 9
    dw 10  # T
    dw 2   # J
    dw 3   # Q
    dw 4   # K
    dw 11  # A
end
