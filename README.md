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
