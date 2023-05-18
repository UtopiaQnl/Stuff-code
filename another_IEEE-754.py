import struct
from itertools import islice

from numpy import single as float32


def float_to_bin_parts(number, bits=64):
    if bits == 32:  # single precision
        int_pack = 'I'
        float_pack = 'f'
        exponent_bits = 8
        mantissa_bits = 23
        exponent_bias = 127
    elif bits == 64:  # double precision. all python floats are this
        int_pack = 'Q'
        float_pack = 'd'
        exponent_bits = 11
        mantissa_bits = 52
        exponent_bias = 1023
    else:
        raise ValueError('bits argument must be 32 or 64')
    bin_iter = iter(bin(struct.unpack(int_pack, struct.pack(float_pack, number))[0])[2:].rjust(bits, '0'))
    return [''.join(islice(bin_iter, x)) for x in (1, exponent_bits, mantissa_bits)]



initial_number = float32(0.0000000000003)
print("Элементы числа %.51f типа float:" % initial_number)
print(float_to_bin_parts(initial_number, 32))
sign, exponent, mantissa = float_to_bin_parts(initial_number, 32)

print(f'\n{mantissa}')
mantissa2 = '1' + mantissa
print(f'{mantissa2}\n')
print("Исходный порядок в десятичном виде " + str(int(exponent, 2)))

print("Настоящий порядок в двоичном виде " + str(bin(int(exponent, 2) - 127)))
print("Настоящая мантисса в двоичном виде " + str("1." + mantissa))

exponent = int(exponent, 2) - 127 - 23
print("Порядок после переноса запятой (в десятичной системе) " + str(exponent))

print(f"Мантисса ({'1' + mantissa}) после переноса запятой (в десятичной системе) " + str(int("1" + mantissa, 2)))
mantissa = int("1" + mantissa, 2)

recon_number = mantissa * (2.0 ** exponent)

if sign == '1':
    recon_number *= -1

print("Реконструированное число {0:.52}".format(recon_number))