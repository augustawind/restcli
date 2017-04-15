from restcli import parser


def test_assign_headers():
    arg = "Authorization:'JWT abc123.foo'"
    tokens = parser.lex(arg)
    expected = ((parser.ACTIONS.assign.name, ["Authorization:JWT abc123.foo"]),
                (parser.ACTIONS.append.name, None),
                (parser.ACTIONS.delete.name, None))
    assert contents_equal(tokens, expected)


def contents_equal(*seqs):
    """Return True if the contents of each sequence are equal.
    
    Specifically, this function checks that each sequence has the same length,
    and that each item in each sequence is equal to (==) exactly one item in
    every other sequence, regardless of ordering.
    """
    if len(seqs) < 2:
        raise TypeError('contents_equal expected at least 2 arguments,'
                        ' got %s' % (len(seqs)))

    head = seqs[0]
    tail = seqs[1:]
    prev_len = len(head)

    for seq in tail:
        # Check that each sequence has the same length
        next_len = len(seq)
        if next_len != prev_len:
            return False
        prev_len = next_len

        # Check that each sequence has the same contents
        for x in seq:
            for y in head:
                if x == y:
                    break
            else:
                return False

    return True
