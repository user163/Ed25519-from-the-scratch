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

[1]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Addition_on_twisted_Edwards_curves
[2]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Doubling_on_twisted_Edwards_curves
[3]: https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.4
[4]: https://datatracker.ietf.org/doc/html/rfc8032
[5]: https://en.wikipedia.org/wiki/Twisted_Edwards_curve#Extended_coordinates
[6]: https://eprint.iacr.org/2008/522.pdf
