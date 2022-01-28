from .interest_rate import earnings

def FinState(API_key, country='kr'):
    if country == 'kr':
        from ._kr_financial_statements import KRFinState
        return KRFinState(API_key)

def InfluenceDiagram(labels, source, target, value, title="Influence Diagram", returnTrue=False):
    from ._influence_diagram import InfluenceDiagram
    return InfluenceDiagram(labels=labels, source=source, target=target, value=value, title=title, returnTrue=returnTrue)

