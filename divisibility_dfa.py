""" Constructs a DFA to test for divisibility by a given number. """
import random

class DFA(object):
    """ Represents a DFA.

    Does not support state removal.
    Every label must be distinct (aka no NFA shenanigans.
    """
    def __init__(self, num_states):
        # DFA = a graph where the edges have labels
        # The states are represented implicitly by a number label
        self.num_states = num_states

        self.adj_mat = [
            [list() for _ in xrange(num_states)]
            for _ in xrange(num_states)
        ]
        self.rev_mat = [
            [list() for _ in xrange(num_states)]
            for _ in xrange(num_states)
        ]
        self.start_state = 0

    def set_start(self, st):
        self.start_state = st

    def add_edge(self, start, end, label):
        self.adj_mat[start][end].append(label)
        self.rev_mat[end][start].append(label)

    def equation(self, state, is_accept):
        """ An equations is of the form
            R_i = R_1 regex + R_2 regex + ... + R_n regex + regex
        Represent it as the list
            (regex_1, regex_2, ...)
        where regex_i is None if it does not appear in the term
        """
        equation = [None] * (self.num_states + 1)
        # Get all edges that end in the given state
        edges = self.rev_mat[state]

        # The DFA can have multiedges so we need to check for it here
        for i in xrange(self.num_states):
            incoming = edges[i]
            if not incoming:
                continue
            equation[i] = '|'.join(incoming)
        for i in xrange(self.num_states):
            if equation[i] is not None and '|' in equation[i]:
                equation[i] = '(%s)' % equation[i]
        # Handle accept states correctly
        if state == self.start_state:
            equation[-1] = ''
        return equation


def build_dfa(b, d):
    """
    b: binary, decimal, or hexadecimal
    d: The divisor to test by.

    Returns a DFA that accepts iff the given input is a valid
    base 10 number divisble by d.
    """
    # The DFA has d + 1 states
    # Start state: checks that input is non-empty.
    # d states: represent number == i mod d. State 0 is an accept state
    # Every state goes to the failing state if it doesn't get a digit
    assert b in ('binary', 'decimal', 'hexadecimal'), 'Invalid base'
    dfa = DFA(d + 1)
    dfa.set_start(d)

    if b == 'binary':
        digits = ('0', '1')
        base = 2
    elif b == 'decimal':
        digits = [str(i) for i in range(10)]
        base = 10
    elif b == 'hexadecimal':
        digits = [str(i) for i in range(10)] + ['A', 'B', 'C', 'D', 'E', 'F']
        base = 16
    else:
        # Do error checking if I wasn't lazy
        pass

    # Start state
    for digit in digits:
        val = int(digit, 16)
        dfa.add_edge(d, val % d, '%s' % digit)

    # The d intermediates
    # On seeing a new digit 0-9, multiply by 10 and add the digit
    for i in xrange(d):
        for digit in digits:
            val = int(digit, 16)
            dfa.add_edge(i, (base * i + val) % d, digit)

    return dfa


def dfa_to_regex(dfa, accept):
    """ Converts a DFA to an equivalent regular expression.

    This assumes there's only one accept state in the entire DFA.

    (This code is super messy and super awful.)

    Uses the Brzozowski method.
    """
    N = dfa.num_states

    equations = [dfa.equation(i, i == accept) for i in xrange(N)]
    # TODO change when this supports multiple accept states
    to_substitute = set(xrange(N)) - set([accept])
    # Don't know how to minimize final length, so eliminate in
    # random order
    to_substitute = list(to_substitute)
    random.shuffle(to_substitute)

    for state in to_substitute:
        # Replace the self loop
        # Going to be very liberal with the parantheses to
        # make extra sure this works in the right order. Definitely
        # going to have more than needed here.
        self_label = equations[state][state]
        if self_label is not None:
            # Now do the rest. Prepend r* to every coefficient
            equations[state][state] = None
            for i in xrange(N+1):
                label2 = equations[state][i]
                if label2 is not None:
                    equations[state][i] = '%s(%s)*' % (label2, self_label)

        # Substitute
        replaced_with = equations[state]
        for i in xrange(N):
            eqn = equations[i]
            if eqn[state] is None:
                continue
            coeff = eqn[state]
            terms = [replaced_with[i] + coeff if replaced_with[i] is not None else None for i in xrange(N+1)]
            # Set to zero before substitution
            eqn[state] = None
            for in_eqn_i in xrange(N+1):
                if eqn[in_eqn_i] is None:
                    eqn[in_eqn_i] = terms[in_eqn_i]
                elif terms[in_eqn_i] is None:
                    # do nothing
                    pass
                else:
                    # Add the two (aka add or)
                    eqn[in_eqn_i] = '(%s|%s)' % (eqn[in_eqn_i], terms[in_eqn_i])
        # Delete this equation
        equations[state] = [None] * (N+1)
    # Two coefficients should be left, the self loop and the constant
    assert equations[accept].count(None) == N-1, 'Not all substitutions carried through correctly'
    return '^%s(%s)*$' % (equations[accept][-1], equations[accept][accept])


if __name__ == '__main__':
    # Some tests
    # Not comprehensive because Python can't handle the bigger regexes (lol)
    import re
    for b in ('binary', 'decimal', 'hexadecimal'):
        for d in range(2, 4):
            dfa = build_dfa(b, d)
            reg = dfa_to_regex(dfa, 0)
            print b, d, len(reg)
            print reg

            assert re.match(reg, '') is None, 'matches empty string'
            for i in range(0, 5000 * d):
                if b == 'binary':
                    s = bin(i)[2:]
                elif b == 'hexadecimal':
                    s = hex(i)[2:].upper()
                else:
                    s = str(i)
                m = re.match(reg, s)
                assert (m is None if i % d != 0 else m is not None), '%d %d' % (d, i)
