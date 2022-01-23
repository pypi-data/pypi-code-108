from ..noun import Noun
from ..possessive import Possessive
from ..preposition import Preposition
from ..adjective import Adjective
from ..np import NP
from ..pp import PP


class TestPossessives:
    @staticmethod
    def PossNP() -> None:
        nouns: list[Noun] = []
        nouns.append(Noun.create_from_xml("data/noun/árasán_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/bó_fem.xml"))
        nouns.append(Noun.create_from_xml("data/noun/comhlacht_masc3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/dealbh_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/éiceachóras_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/francfurtar_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fliúit_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fadhb_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fobhríste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/garáiste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/haematóma_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/iasacht_fem3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/jab_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/leabharlann_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/máthair_fem5.xml"))
        nouns.append(Noun.create_from_xml("data/noun/nóta_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/ócáid_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/pacáiste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/rás_masc3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sobaldráma_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sábh_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/stábla_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sráid_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/tábhairne_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/ubh_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/x-gha_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/zombaí_masc4.xml"))

        possessives: list[Possessive] = []
        possessives.append(Possessive.create_from_xml("data/possessive/mo_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/do_poss.xml"))
        possessives.append(
            Possessive.create_from_xml("data/possessive/a_poss_masc.xml")
        )
        possessives.append(Possessive.create_from_xml("data/possessive/a_poss_fem.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/ár_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/bhur_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/a_poss_pl.xml"))

        adj: Adjective = Adjective.create_from_xml("data/adjective/mór_adj1.xml")

        with open("test-poss-np.txt", "w") as f:
            for n in nouns:
                for poss in possessives:
                    np: NP = NP.create_from_noun_adjective_possessive(n, adj, poss)
                    f.write(
                        poss.getFriendlyNickname()
                        + "\t"
                        + np.sgNom[0].value
                        + "\t"
                        + np.sgGen[0].value
                        + "\t"
                        + np.plNom[0].value
                        + "\t"
                        + np.plGen[0].value
                    )
                    f.write("\n")
                    print(np.print())
                f.write("\n")

    @staticmethod
    def PrepPossNP() -> None:
        nouns: list[Noun] = []
        nouns.append(Noun.create_from_xml("data/noun/árasán_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/bó_fem.xml"))
        nouns.append(Noun.create_from_xml("data/noun/comhlacht_masc3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/dealbh_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/éiceachóras_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/francfurtar_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fliúit_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fadhb_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/fobhríste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/garáiste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/haematóma_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/iasacht_fem3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/jab_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/leabharlann_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/máthair_fem5.xml"))
        nouns.append(Noun.create_from_xml("data/noun/nóta_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/ócáid_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/pacáiste_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/rás_masc3.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sobaldráma_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sábh_masc1.xml"))
        nouns.append(Noun.create_from_xml("data/noun/stábla_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/sráid_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/tábhairne_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/ubh_fem2.xml"))
        nouns.append(Noun.create_from_xml("data/noun/x-gha_masc4.xml"))
        nouns.append(Noun.create_from_xml("data/noun/zombaí_masc4.xml"))

        possessives: list[Possessive] = []
        possessives.append(Possessive.create_from_xml("data/possessive/mo_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/do_poss.xml"))
        possessives.append(
            Possessive.create_from_xml("data/possessive/a_poss_masc.xml")
        )
        possessives.append(Possessive.create_from_xml("data/possessive/a_poss_fem.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/ár_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/bhur_poss.xml"))
        possessives.append(Possessive.create_from_xml("data/possessive/a_poss_pl.xml"))

        adj: Adjective = Adjective.create_from_xml("data/adjective/mór_adj1.xml")

        prepositions: list[Preposition] = []
        prepositions.append(Preposition.create_from_xml("data/preposition/ag_prep.xml"))
        prepositions.append(Preposition.create_from_xml("data/preposition/ar_prep.xml"))
        prepositions.append(Preposition.create_from_xml("data/preposition/as_prep.xml"))
        prepositions.append(
            Preposition.create_from_xml("data/preposition/chuig_prep.xml")
        )
        prepositions.append(Preposition.create_from_xml("data/preposition/de_prep.xml"))
        prepositions.append(Preposition.create_from_xml("data/preposition/do_prep.xml"))
        prepositions.append(
            Preposition.create_from_xml("data/preposition/faoi_prep.xml")
        )
        prepositions.append(Preposition.create_from_xml("data/preposition/i_prep.xml"))
        prepositions.append(Preposition.create_from_xml("data/preposition/le_prep.xml"))
        prepositions.append(Preposition.create_from_xml("data/preposition/ó_prep.xml"))
        prepositions.append(
            Preposition.create_from_xml("data/preposition/roimh_prep.xml")
        )
        prepositions.append(
            Preposition.create_from_xml("data/preposition/thar_prep.xml")
        )
        prepositions.append(
            Preposition.create_from_xml("data/preposition/trí_prep.xml")
        )
        prepositions.append(Preposition.create_from_xml("data/preposition/um_prep.xml"))

        with open("test-prep-poss-np.txt", "w") as f:
            for prep in prepositions:
                for n in nouns:
                    for poss in possessives:
                        np: NP = NP.create_from_noun_adjective_possessive(n, adj, poss)
                        pp: PP = PP.create(prep, np)
                        f.write(
                            "["
                            + prep.getLemma()
                            + " + "
                            + poss.getFriendlyNickname()
                            + "]\t"
                            + pp.sg[0].value
                            + "\t"
                            + pp.pl[0].value
                        )
                        f.write("\n")
                        print(pp.print())
                    f.write("\n")
