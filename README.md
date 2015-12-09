Generates regular expressions that test divisibilty of
numbers by building the DFA, then converting them into
a regular expression.

Wrote over a few hours with very little regards to
optimization or code readability, so don't read too much
into it.

If you run the code on your own, note the size of the
regex grows exponentially. Going up to divisibility by
10 is safe. Anything past 15 may take up all your memory.
