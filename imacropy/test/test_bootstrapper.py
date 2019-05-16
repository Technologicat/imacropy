# -*- coding: utf-8 -*-

# Use a relative import; the test framework runs us from the top level
# using 'macropy3 -m imacropy.test.test_bootstrapper'.
from .simplelet import macros, let

def main():
    x = let((y, 21))[2*y]
    assert x == 42
    print("All tests PASSED")

if __name__ == "__main__":
    main()
