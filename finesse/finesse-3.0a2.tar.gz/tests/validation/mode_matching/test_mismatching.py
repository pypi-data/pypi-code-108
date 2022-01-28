import finesse


def test_dbs_mismatch():
    model = finesse.Model()
    model.parse(
        """
    l l1
    l l2
    l l3
    l l4
    dbs dbs1
    link(l1, dbs1.p1)
    link(l2, dbs1.p2)
    link(l3, dbs1.p3)
    link(l4, dbs1.p4)
    fd E1o dbs1.p1.o f=0
    fd E2o dbs1.p2.o f=0
    fd E3o dbs1.p3.o f=0
    fd E4o dbs1.p4.o f=0

    modes(maxtem=0)

    gauss g1 l1.p1.o w0=1m z=0
    gauss g2 l2.p1.o w0=1.1m z=0
    gauss g3 l3.p1.o w0=1.2m z=0
    gauss g4 l4.p1.o w0=1.3m z=0
    """
    )

    sol = model.run()
    assert sol["E3o"] < sol["E2o"] < sol["E1o"] < sol["E4o"]
