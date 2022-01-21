from nexusmaker import Record


def test_simple():
    r = Record(
        ID=1, Parameter_ID=2, Language_ID=3, Language='English', Parameter='Hand', Item='hand',
        Annotation='?', Cognacy=None, Loan="L"
    )
    assert r.ID == 1
    assert r.Parameter_ID == 2
    assert r.Language_ID == 3
    assert r.Language == 'English'
    assert r.Parameter == 'Hand'
    assert r.Item == 'hand'
    assert r.Annotation == '?'
    assert r.Loan == "L"
    assert r.Cognacy == None


def test_is_loan():
    assert not Record(Loan="").is_loan
    assert not Record(Loan=None).is_loan
    assert Record(Loan="L").is_loan
    assert Record(Loan="English").is_loan
    assert Record(Loan=True).is_loan
    assert Record(Loan="B").is_loan
    assert Record(Loan="S").is_loan
    assert Record(Loan="X").is_loan
    assert Record(Loan="x").is_loan


def test_get_token():
    r = Record(
        ID=1, Parameter_ID=2, Language_ID=3, Language='English', Parameter='Hand', Item='hand',
        Annotation='?', Cognacy=None, Loan="L"
    )
    assert r.get_taxon() == "English_3"
    r = Record(
        ID=1, Parameter_ID=2, Language_ID=None, Language='English', Parameter='Hand', Item='hand',
        Annotation='?', Cognacy=None, Loan="L"
    )
    assert r.get_taxon() == "English"
