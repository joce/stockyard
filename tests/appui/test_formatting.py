from appui import _formatting as fmt


def test_as_percent():
    assert fmt.as_percent(None) == "N/A"
    assert fmt.as_percent(0) == "0.00%"
    assert fmt.as_percent(100) == "100.00%"
    assert fmt.as_percent(12.34) == "12.34%"
    assert fmt.as_percent(12.34444) == "12.34%"
    assert fmt.as_percent(12.34555) == "12.35%"
    assert fmt.as_percent(-20) == "-20.00%"
    assert fmt.as_percent(-892.76324765) == "-892.76%"


def test_as_float():
    assert fmt.as_float(None) == "N/A"
    assert fmt.as_float(1234.5678) == "1234.57"
    assert fmt.as_float(1234.5678, 3) == "1234.568"


def test_as_shrunk_int():
    assert fmt.as_shrunk_int(None) == "N/A"
    assert fmt.as_shrunk_int(1) == "1"
    assert fmt.as_shrunk_int(10) == "10"
    assert fmt.as_shrunk_int(200) == "200"
    assert fmt.as_shrunk_int(1234) == "1.23K"
    assert fmt.as_shrunk_int(1000000) == "1.00M"
    assert fmt.as_shrunk_int(1000000000) == "1.00B"
    assert fmt.as_shrunk_int(1000000000000) == "1.00T"
