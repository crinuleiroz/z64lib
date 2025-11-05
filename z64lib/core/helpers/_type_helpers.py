def sign_extend(func, n_bits):
    sign = 1 << (n_bits - 1)
    return (func & (sign - 1)) - (func & sign)