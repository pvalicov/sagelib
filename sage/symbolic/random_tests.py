from sage.misc.prandom import randint, random
import operator
from sage.rings.all import QQ
import sage.calculus.calculus
import sage.symbolic.pynac
from sage.symbolic.constants import *

def _mk_full_functions():
    r"""
    A simple function that returns a list of all Pynac functions of known
    arity, sorted by name.

    EXAMPLES::

        sage: from sage.symbolic.random_tests import _mk_full_functions
        sage: [f for (one,f,arity) in _mk_full_functions()] # random
        [Ei, abs, arccos, arccosh, arccot, arccoth, arccsc, arccsch,
        arcsec, arcsech, arcsin, arcsinh, arctan, arctan2, arctanh,
        arg, beta, binomial, ceil, conjugate, cos, cosh, cot, coth,
        csc, csch, dickman_rho, dilog, dirac_delta, elliptic_e,
        elliptic_ec, elliptic_eu, elliptic_f, elliptic_kc,
        elliptic_pi, erf, exp, factorial, floor, heaviside, imag_part,
        integrate, kronecker_delta, log, polylog, real_part, sec,
        sech, sgn, sin, sinh, tan, tanh, unit_step, zeta, zetaderiv]

    Note that this doctest will fail whenever a Pynac function is added or
    removed.  In that case, it is very likely that the doctests for
    random_expr will fail as well.  That's OK; just fix the doctest
    to match the new output.
    """
    items = sage.symbolic.pynac.symbol_table['functions'].items()
    items.sort()
    return [(1.0, f, f.number_of_arguments())
            for (name, f) in items
            if hasattr(f, 'number_of_arguments') and
               f.number_of_arguments() > 0]

# For creating simple expressions

fast_binary = [(0.4, operator.add), (0.1, operator.sub), (0.5, operator.mul)]
fast_unary = [(0.8, operator.neg), (0.2, operator.abs)]
fast_nodes = [(0.9, fast_binary, 2), (0.1, fast_unary, 1)]

# For creating expressions with the full power of Pynac's simple expression
# subset (with no quantifiers/operators; that is, no derivatives, integrals,
# etc.)
full_binary = [(0.3, operator.add), (0.1, operator.sub), (0.3, operator.mul), (0.2, operator.div), (0.1, operator.pow)]
full_unary = [(0.8, operator.neg), (0.2, operator.inv)]
full_functions = _mk_full_functions()
full_nullary = [(1.0, c) for c in [pi, e]] + [(0.05, c) for c in
        [golden_ratio, log2, euler_gamma, catalan, khinchin, twinprime,
            mertens, brun]]
full_internal = [(0.6, full_binary, 2), (0.2, full_unary, 1),
        (0.2, full_functions)]

def normalize_prob_list(pl, extra=()):
    r"""
    INPUT:

    - ``pl`` - A list of tuples, where the first element of each tuple is
      a floating-point number (representing a relative probability).  The
      second element of each tuple may be a list or any other kind of object.

    - ``extra`` - A tuple which is to be appended to every tuple in ``pl``.

    This function takes such a list of tuples (a "probability list") and
    normalizes the probabilities so that they sum to one.  If any of the
    values are lists, then those lists are first normalized; then
    the probabilities in the list are multiplied by the main probability
    and the sublist is merged with the main list.

    For example, suppose we want to select between group A and group B with
    50% probability each.  Then within group A, we select A1 or A2 with 50%
    probability each (so the overall probability of selecting A1 is 25%);
    and within group B, we select B1, B2, or B3 with probabilities in
    a 1:2:2 ratio.

    EXAMPLES::

        sage: from sage.symbolic.random_tests import *
        sage: A = [(0.5, 'A1'), (0.5, 'A2')]
        sage: B = [(1, 'B1'), (2, 'B2'), (2, 'B3')]
        sage: top = [(50, A, 'Group A'), (50, B, 'Group B')]
        sage: normalize_prob_list(top)
        [(0.250000000000000, 'A1', 'Group A'), (0.250000000000000, 'A2', 'Group A'), (0.1, 'B1', 'Group B'), (0.2, 'B2', 'Group B'), (0.2, 'B3', 'Group B')]
    """
    if len(pl) == 0:
        return pl
    result = []
    total = sum([float(p[0]) for p in pl])
    for p in pl:
        prob = p[0]
        val = p[1]
        if len(p) > 2:
            p_extra = p[2:]
        else:
            p_extra = extra
        if isinstance(val, list):
            norm_val = normalize_prob_list(val, extra=p_extra)
            for np in norm_val:
                result.append(((prob/total)*np[0], np[1]) + np[2:])
        else:
            result.append(((prob/total), val) + p_extra)
    return result

def choose_from_prob_list(lst):
    r"""
    INPUT:

    - ``lst`` - A list of tuples, where the first element of each tuple
      is a nonnegative float (a probability), and the probabilities sum
      to one.

    OUTPUT:

    A tuple randomly selected from the list according to the given
    probabilities.

    EXAMPLES::

        sage: from sage.symbolic.random_tests import *
        sage: v = [(0.1, False), (0.9, True)]
        sage: choose_from_prob_list(v)
        (0.900000000000000, True)
        sage: true_count = 0
        sage: for _ in range(10000):
        ...       if choose_from_prob_list(v)[1]:
        ...           true_count += 1
        sage: true_count
        9033
        sage: true_count - (10000 * 9/10)
        33
    """
    r = random()
    for i in range(len(lst)-1):
        if r < lst[i][0]:
            return lst[i]
        r -= lst[i][0]
    return lst[-1]

def random_integer_vector(n, length):
    r"""
    Give a random list of length *length*, consisting of nonnegative
    integers that sum to *n*.

    This is an approximation to IntegerVectors(n, length).random_element().
    That gives values uniformly at random, but might be slow; this
    routine is not uniform, but should always be fast.  

    (This routine is uniform if *length* is 1 or 2; for longer vectors,
    we prefer approximately balanced vectors, where all the values
    are around `n/{length}`.)

    EXAMPLES::

        sage: from sage.symbolic.random_tests import *
        sage: random_integer_vector(100, 2)
        [11, 89]
        sage: random_integer_vector(100, 2)
        [51, 49]
        sage: random_integer_vector(100, 2)
        [4, 96]
        sage: random_integer_vector(10000, 20)
        [332, 529, 185, 738, 82, 964, 596, 892, 732, 134, 834, 765, 398, 608, 358, 300, 652, 249, 586, 66]
    """
    if length == 0:
        return []
    elif length == 1:
        return [n]
    elif length == 2:
        v = randint(0, n)
        return [v, n-v]
    else:
        v = randint(0, 2*n//length)
        return [v] + random_integer_vector(n-v, length-1)

def random_expr_helper(n_nodes, internal, leaves, verbose):
    r"""
    Produce a random symbolic expression of size *n_nodes* (or slightly
    larger).  Internal nodes are selected from the *internal* probability
    list; leaves are selected from *leaves*.  If *verbose* is True,
    then a message is printed before creating an internal node.

    EXAMPLES::

        sage: from sage.symbolic.random_tests import *
        sage: random_expr_helper(9, [(0.5, operator.add, 2), (0.5, operator.neg, 1)], [(0.5, 1), (0.5, x)], True)
        About to apply <built-in function add> to [1, x]
        About to apply <built-in function add> to [x, x + 1]
        About to apply <built-in function neg> to [1]
        About to apply <built-in function neg> to [-1]
        About to apply <built-in function neg> to [1]
        About to apply <built-in function add> to [2*x + 1, -1]
        2*x
    """
    if n_nodes == 1:
        return choose_from_prob_list(leaves)[1]
    else:
        r = choose_from_prob_list(internal)
        n_nodes -= 1
        n_children = r[2]
        n_spare_nodes = n_nodes - n_children
        if n_spare_nodes <= 0:
            n_spare_nodes = 0
        nodes_per_child = random_integer_vector(n_spare_nodes, n_children)
        children = [random_expr_helper(n+1, internal, leaves, verbose) for n in nodes_per_child]
        if verbose:
            print "About to apply %r to %r" % (r[1], children)
        return r[1](*children)

def random_expr(size, nvars=1, ncoeffs=None, var_frac=0.5, internal=full_internal, nullary=full_nullary, nullary_frac=0.2, coeff_generator=QQ.random_element, verbose=False):
    r"""
    Produce a random symbolic expression of the given size.  By
    default, the expression involves (at most) one variable, an arbitrary
    number of coefficients, and all of the symbolic functions and constants
    (from the probability lists full_internal and full_nullary).  It is
    possible to adjust the ratio of leaves between symbolic constants,
    variables, and coefficients (var_frac gives the fraction of variables,
    and nullary_frac the fraction of symbolic constants; the remaining
    leaves are coefficients).

    The actual mix of symbolic constants and internal nodes can be modified
    by specifying different probability lists.

    To use a different type for coefficients, you can specify
    coeff_generator, which should be a function that will return
    a random coefficient every time it is called.

    This function will often raise an error because it tries to create
    an erroneous expression (such as a division by zero).

    EXAMPLES::

        sage: from sage.symbolic.random_tests import *
        sage: set_random_seed(2)
        sage: random_expr(50, nvars=3, coeff_generator=CDF.random_element) # random
        (euler_gamma - v3^(-e) + (v2 - e^(-e/v2))^(((2.85879036573 -
        1.18163393202*I)*v2 + (2.85879036573 - 1.18163393202*I)*v3)*pi
        - 0.247786879678 + 0.931826724898*I)*arccsc((0.891138386848 -
        0.0936820840629*I)/v1) - (0.553423153995 - 0.5481180572*I)*v3
        + 0.149683576515 - 0.155746451854*I)*v1 + arccsch(pi +
        e)*elliptic_eu(khinchin*v2, 1.4656989704 + 0.863754357069*I)
        sage: random_expr(5, verbose=True) # random
        About to apply dilog to [1]
        About to apply arcsec to [0]
        About to apply <built-in function add> to [1/6*pi^2, arcsec(0)]
        1/6*pi^2 + arcsec(0)
    """
    vars = [(1.0, sage.calculus.calculus.var('v%d' % (n+1))) for n in range(nvars)]
    if ncoeffs is None:
        ncoeffs = size
    coeffs = [(1.0, coeff_generator()) for _ in range(ncoeffs)]
    leaves = [(var_frac, vars), (1.0 - var_frac - nullary_frac, coeffs), (nullary_frac, nullary)]
    leaves = normalize_prob_list(leaves)

    internal = normalize_prob_list(internal)

    return random_expr_helper(size, internal, leaves, verbose)
