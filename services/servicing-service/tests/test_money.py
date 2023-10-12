"""Money-correctness tests (currently FAIL — float drift). CI is continue-on-error."""


def test_float_payment_drift():
    # apply 0.1 ten times to a 1.00 balance; float makes this != 0.0
    balance = 1.0
    for _ in range(10):
        balance = balance - 0.1
    assert balance == 0.0, f"float drift left balance at {balance!r} (should be 0.0)"
