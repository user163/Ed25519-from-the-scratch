# Ed25519-from-the-scratch

Implementation of the different parts of Ed25519. This Python implementation is not intended for a real world application, but to illustrate the different parts of Ed25519 and their interaction.

Ed25519 is described in [RFC 8032][4].

---------

**Part 1 : Point addition**  

In *100_point_addition.py*, point addition and point doubling are implemented in affine coordinates, see [Addition on twisted Edwards curves][1] and [Doubling on twisted Edwards curves][2] in Wikipedia, and extended homogeneous coordinates, see [5.1.4 Point Addition][3] in RFC 8032 and [Extended coordinates][5] in Wikipedia.  
In contrast to the extended homogeneous formulas, the affine formulas contain modular divisions. Modular divisions are relatively expensive, unlike other modular operations (such as multiplication, addition, subtraction). Therefore the calculations with the extended homogeneous formulas are faster, although the formulas themselves are more complex and contain more operations (but just no divisions), see [Twisted Edwards Curves Revisited][6].  
Since many point additions/doublings are performed in point multiplication (because of the usually large scalars), the performance gain is potentiated when using the extended homogeneous coordinates, which is why in practice these are implemented rather than the affine coordinates.

The tests in *point_addition.py* check the implementation for different test vectors.

---------

**Part 2 : Point multiplication** 

The point multiplication is implemented in a time-constant manner, since otherwise information about the private key is leaked.

One possible implementation is the [Montgomery Ladder][2_3]. However, in the context of Ed25519, multiplication is done with a fixed point (the generator/base point), for which there are more performant solutions. In the context of X25519, however, where multiplication is done with different points (namely the various public keys of the opposite sides), the Montgomery Ladder is still the most efficient algorithm, [see An Explainer On Ed25519 Clamping][2_1] and [What's the Curve25519 clamping all about?][2_2]. 
In this implementation, for simplicity, the Montgmomery Ladder is used for Ed25519 as well.

Typical algorithms of point multiplication use the bit representation of the scalar to control the add/double calls, see e.g. [Double-and-add][2_4] on Wikipedia. Such implementations are generally not time-constant:
- Often the highest set bit is used as the upper bound of the bit field. Since the highest set bit varies, this leads to different sized bitfields and thus different execution times. To mitigate this vulnerability, Ed25519 **by definition** sets the most significant bit in the private key (the first 32 bytes of the Sha512 hash of the seed) to 0 (bit 255, note: zero based numbering) and the next most significant bit to 1 (bit 254), (this bit manipulation is one of two, see the Clamping section for more details). Thus all public keys have bit 254 as the highest set bit, which implies equal bit fields and execution times.
The algorithm implemented here is intended to be robust even without this key fix. Therefore, a fixed size bit field of 256 bits (0 to bit 255) is used. This size is sufficient for all required operations: on the one hand, the private key used by Ed25519 requires only 255 bits by definition (s. above). On the other hand, the generator has order l, so that for all scalars s: s*G = (s%l)*G with s%l < l. The highest set bit of l is 252. For s%l, therefore, the maximum bit that can be set is 252, so that the size of 256 bits is also sufficient here.
- Different operations are often performed for 0-bit and 1-bit. This leads to different execution times, whereby information about the bit constellation of the key can be leaked. To avoid this, identical operations must be performed for 0-bit and 1-bit. The Montgomery Ladder does exactly that.

Since the add and doubling operations of the extended homogeneous formulas are the most performant, these are used for the point multiplication.

The tests in *point_multiplication.py* perform the point multiplication for a set of test vectors.

---------

**Part 3: Point compression and decompression**

In *300_point_compression.py*, point compression and decompression are implemented.

Ed25519 encodes the x and y coordinate of a point to 32 bytes (because of x and y mod p) in **little endian order**. This must be taken into account when converting integer -> bytes and bytes -> integer.

Also, Ed25519 compresses points. This results in a shorter public key (32 instead of 64 bytes). The y coordinate is used. Because of y mod p, the most significant bit (ms bit) in the most significant byte (ms byte) is not set. This location is used to store the parity (even/odd) of the x coordinate. x is even/odd if the least significant bit (ls bit) in least significant byte (ls byte) is 0/1:

```none
x, little endian: 0. byte (ls),            1. byte, ..., 31. byte (ms)
                  _ _ _ _   _ _ _ P
             ms bit               ls bit
					  
y, little endian: 0. byte (ls),            1. byte, ..., 31. byte (ms)
                                                         0 1 _ _   _ _ _ _ 
                                                    ms bit               ls bit
```

I.e. the compressed key has a length of 256 bits (32 bytes), (x and y coordinates have a length of 255 bits (32 bytes) each).
																 
There is no mathematical necessity for the y coordinate to be used, the x coordinate can be used as well. According to [this post][3_1] on SE the choice of the y coordinate has patent reasons.

When decompressing a point, it is exploited that the modulus is congruent to 5 modulo 8 (p mod 8 = 5) and the Legendre solution is used, see [Prime or prime power modulus][3_2]. The details are described in [RFC 8032, Chapter 5.1.3 Decoding][3_3] and an example implementation in Python is given in [RFC 8032, Chapter 6 Ed25519 Python Illustration][3_4].
A derivation or more in-depth explanation of the mathematical formulas can be found in [Re-Deriving the edwards25519 Decoding Formulas][3_5]. 

The tests compress and decompress the base point and a number of other points.

--------------

**Part 4: Clamping**

Clamping is the modification of certain bits of the scalar s used to generate the public key. Note that for Ed25519 the scalar (unlike X25519) is not the secret key (or seed), but the first 32 bytes of the SHA-512 hashed secret key (this is described in more detail in the part *Key generation*).  
Clamping is done for security reasons.

The following modifications are made:
- M1: The most significant bit in the most significant byte is set to 0, and the second most significant bit is set to 1.
- M2: The three least significant bits in the least significant byte are set to 0:

scalar s, in little endian order (used by Ed25519):

```
      0. byte (ls byte), 1. byte, ...		31. byte (ms byte)
      _ _ _ _   _ 0 0 0           		0 1 _ _   _ _ _ _
 ms bit               ls bit               ms bit               ls bit
```

What is the purpose of M1 and M2?
- M1:   
M1 ensures that all keys have the same most significant bit during point multiplication. This ensures that some implementations of the Montgomery Ladder, which are not time constant with different most significant bits, are also time constant, so that no information is leaked to the scalar s. This bit manipulation was already mentioned in Part 2: Point Multiplication.

  In the context of Ed25519, multiplication is done with a fixed point (namely the base point), for which there are more performant algorithms than the Montgomery Ladder. In the context of X25519, however, multiplication is done with different points (namely the public keys of the respective opposite sides). In this case, the Montgomery Ladder is still the best performing algorithm.   
M1 is therefore primarily relevant for X25519 and not for Ed25519. Of course, if an implementation of Ed25519 uses the Montgomery Ladder (like this one), it is also relevant for Ed25519.

- M2:  
Curves with a cofactor unequal 1 (like Curve25519 or edwards25519 with the cofactor 8) have besides the subgroup of large order (l) also subgroups of smaller order. For the cofactor 8 these are the orders 1, 2, 4 and 8. If a point from this group is multiplied by 8, the identity/neutral element I results.   
Setting the bits according to M2 corresponds to a left shift by 8 bits and thus a multiplication by 8.   
For X25519, s is multiplied by the public key of the other side. In a small soubgroup attack, the other side sends keys from small order subgroups and can use them to obtain information about the secret key. By setting the bits according to M2 the generation of the shared secret becomes: s * soG = s' * 8 * soG = s' * I = I (I denotes the identity element). I.e. if the point multiplication yields the identity element, this means that the public key soG belongs to a small order subgroup and the processing has to be aborted (attempted attack or mistake on the other side).  
As can be seen from the description, setting the bits according to M2 is only relevant for X25519, but not for Ed25519.

Further reading:  
[*Order and Cofactor of Elliptic Curve* and following sections][4_1]  
[*Order of subgroups formed by Elliptic Curves with a Cofactor*][4_2]

Why is clamping used for Ed25519 when it is actually only relevant for X25519?  
The Montgomery curve curve25519 (on which X25519 is performed) and the twisted Edwards curve edwards25519 (on which Ed25519 is performed) are related to each other: birationally equivalence. This means that there is a mapping, i.e. for practice Ed25519 keys can be transformed to X25519 keys:

```
    edwards25519 (Ed25519)			  ->	curve25519 (X25519)
    ---------------------------------------------------------------------------------------------------
    seed (secret key in the context of Ed25519)
    s_clamped						s_clamped (secret key in the context of X25519)
    public = s_clamped * G				public' = s_clamped * G'
```

During the transformation, s_clamped does not change. Since clamping twice does not change anything, the implicit clamping of X25519 does not change s_clamped. However, this does not mean that the implicit clamping in the context of X25519 is not required. It is necessary with respect to fresh X25519 secret keys (i.e. X25519 secret keys that have been generated with a PRNG and are therefore not clamped).

By the way, the generation of Ed25519 keys from X25519 keys is not possible, because for this a seed would have to be found whose first 32 bytes of its SHA512 hash would have to correspond to the (clamped or unclamped) s_clamped and this is not possible because cryptographic hash functions (like SHA512) are not reversible.  

In *400_clamping.py* clamping and its test is implemented.

Further literature on the subject of clamping:  
[*An Explainer On Ed25519 Clamping*][4_3]  
[*What’s the Curve25519 clamping all about?*][4_4]

---------------

**Part 5: Generation of the secret and public key**

In Ed25519 the secret key (or seed) is a randomly (i.e. with a CSPRNG) generated 32 bytes sequence. This is hashed with SHA-512. The first 32 bytes are first clamped and then used to derive the public key. The second 32 bytes are needed for signing and are used as prefix to the message to be signed (more about this in the part Signing/Verification).

The public key is compressed (32 bytes, little endian).

Sometimes the combination secret key|public key, i.e. a 64 bytes value, is specified as secret key, see [*Why are NaCl secret keys 64 bytes for signing, but 32 bytes for box?*][5_1].  

In *500_key_generation.py* the generation of the secret and public key is implemented. The first two tests use test vectors, the last test shows the key generation using a random secret key.

[1]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Addition_on_twisted_Edwards_curves
[2]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Doubling_on_twisted_Edwards_curves
[3]: https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.4
[4]: https://datatracker.ietf.org/doc/html/rfc8032
[5]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Extended_coordinates
[6]: https://eprint.iacr.org/2008/522.pdf

[2_1]: https://www.jcraige.com/an-explainer-on-ed25519-clamping
[2_2]: https://neilmadden.blog/2020/05/28/whats-the-curve25519-clamping-all-about/
[2_3]: https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Montgomery_ladder
[2_4]: https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add

[3_1]: https://crypto.stackexchange.com/q/106106
[3_2]: https://en.wikipedia.org/wiki/Quadratic_residue#Prime_or_prime_power_modulus
[3_3]: https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.3
[3_4]: https://datatracker.ietf.org/doc/html/rfc8032#section-6
[3_5]: https://words.filippo.io/dispatches/edwards25519-formulas/

[4_1]: https://cryptobook.nakov.com/asymmetric-key-ciphers/elliptic-curve-cryptography-ecc#order-and-cofactor-of-elliptic-curve
[4_2]: https://crypto.stackexchange.com/questions/75900/order-of-subgroups-formed-by-elliptic-curves-with-a-cofactor
[4_3]: https://www.jcraige.com/an-explainer-on-ed25519-clamping
[4_4]: https://neilmadden.blog/2020/05/28/whats-the-curve25519-clamping-all-about/

[5_1]: https://crypto.stackexchange.com/q/54353
