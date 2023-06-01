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

Ed25519 encodes the x and y coordinate of a point to 32 bytes (because of x and y mod p) in little endian order. This must be taken into account when converting integer -> bytes and bytes -> integer.

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
