# edwards25519 parameters
a = -1
d = 37095705934669439343138083508754565189542113879843219016388785533085940283555 
p = 2**255 - 19 # prime, order of Gallois field GF(p)
Gx = 15112221349535400772501151409588531511454012693041857206046113283949847762202
Gy = 46316835694926478169428394003475163141307993866256225615783033603165251855960
l = 2**252 + 27742317777372353535851937790883648493 # order of G, = order of subgroup generated by G 

def add_extended_homogeneous(Q1, Q2):
    (X1, Y1, Z1, T1) = Q1
    (X2, Y2, Z2, T2) = Q2
    A = ((Y1 - X1) * (Y2 - X2)) % p
    B = ((Y1 + X1) * (Y2 + X2)) % p
    C = (T1 * 2 * d * T2) % p
    D = (Z1 * 2 * Z2) % p
    E = (B - A) % p
    F = (D - C) % p
    G = (D + C) % p
    H = (B + A) % p
    X3 = (E * F) % p
    Y3 = (G * H) % p
    T3 = (E * H) % p
    Z3 = (F * G) % p
    return (X3, Y3, Z3, T3)

def double_extended_homogeneous(Q):
    (X1, Y1, Z1, T1) = Q
    A = (X1 * X1) % p
    B = (Y1 * Y1) % p
    C = (2 * Z1 * Z1) % p
    H = (A + B) % p
    E = (H - (X1 + Y1) * (X1 + Y1)) % p
    G = (A - B) % p
    F = (C + G) % p
    X3 = (E * F) % p
    Y3 = (G * H) % p
    T3 = (E * H) % p
    Z3 = (F * G) % p
    return (X3, Y3, Z3, T3)

def affine_to_extended_homogeneous(q):
    (x1, y1) = q
    X1 = x1
    Y1 = y1
    Z1 = 1
    T1 = (x1 * y1) % p
    return (X1, Y1, Z1, T1)

def extended_homogeneous_to_affine(Q):
    (X1, Y1, Z1, T1) = Q
    Z1_inv = pow(Z1, -1, p)
    x1 = (X1 * Z1_inv) % p
    y1 = (Y1 * Z1_inv) % p
    return (x1, y1)

# Montgomery Ladder, time constant for scalars up to 256 bits
def point_multiplication(s, P):
    Q = (0, 1, 1, 0)                  # neutral element
    bits = bin(s)[2:]                 # bit encoding of s
    bitsPadded = bits.rjust(256, '0') # the bit representation of all scalars is extended with leading 0 to 256 bit 
    for b in bitsPadded:              # for each step, the same operations are done, no matter if the bit is 0 or 1
        if b == '0':
            P = add_extended_homogeneous(Q, P)
            Q = double_extended_homogeneous(Q)
        else:
            Q = add_extended_homogeneous(Q, P)
            P = double_extended_homogeneous(P)
    return Q

'''
test vectors
0*G = [0, 1]
1*G = [15112221349535400772501151409588531511454012693041857206046113283949847762202, 46316835694926478169428394003475163141307993866256225615783033603165251855960]
2*G = [24727413235106541002554574571675588834622768167397638456726423682521233608206, 15549675580280190176352668710449542251549572066445060580507079593062643049417]
3*G = [46896733464454938657123544595386787789046198280132665686241321779790909858396, 8324843778533443976490377120369201138301417226297555316741202210403726505172]
4*G = [14582954232372986451776170844943001818709880559417862259286374126315108956272, 32483318716863467900234833297694612235682047836132991208333042722294373421359]
5*G = [33467004535436536005251147249499675200073690106659565782908757308821616914995, 43097193783671926753355113395909008640284023746042808659097434958891230611693]
(l-1)*G = [42783823269122696939284341094755422415180979639778424813682678720006717057747, 46316835694926478169428394003475163141307993866256225615783033603165251855960]  
l*G = [0, 1]
'''

# Convention: use suffix _2 for affine and _4 for extended homogeneous points

#
# test point_multiplication
#

G_2 = (Gx, Gy)
G_4 = affine_to_extended_homogeneous(G_2)

res0G_4 = point_multiplication(0, G_4)
res1G_4 = point_multiplication(1, G_4)
res2G_4 = point_multiplication(2, G_4)
res3G_4 = point_multiplication(3, G_4)
res4G_4 = point_multiplication(4, G_4)
res5G_4 = point_multiplication(5, G_4)
resKG_4 = point_multiplication(l - 1, G_4)
resLG_4 = point_multiplication(l, G_4)
resMG_4 = point_multiplication(l + 1, G_4)
resNG_4 = point_multiplication(l + 2, G_4)

res0G_2 = extended_homogeneous_to_affine(res0G_4)
res1G_2 = extended_homogeneous_to_affine(res1G_4)
res2G_2 = extended_homogeneous_to_affine(res2G_4)
res3G_2 = extended_homogeneous_to_affine(res3G_4)
res4G_2 = extended_homogeneous_to_affine(res4G_4)
res5G_2 = extended_homogeneous_to_affine(res5G_4)
resKG_2 = extended_homogeneous_to_affine(resKG_4)
resLG_2 = extended_homogeneous_to_affine(resLG_4)
resMG_2 = extended_homogeneous_to_affine(resMG_4)
resNG_2 = extended_homogeneous_to_affine(resNG_4)

print(res0G_2)
print(res1G_2)
print(res2G_2)
print(res3G_2)
print(res4G_2)
print(res5G_2)
print(resKG_2)
print(resLG_2)
print(resMG_2)
print(resNG_2)
