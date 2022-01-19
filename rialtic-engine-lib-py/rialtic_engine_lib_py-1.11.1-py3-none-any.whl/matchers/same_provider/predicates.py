from enginelib.matchers.same_provider.taxonomy import TaxonomyData


def valid_taxonomy_code(code: str) -> bool:
    return TaxonomyData.is_taxonomy_code_valid(code)


def match_taxonomy_codes(code1: str, code2: str) -> bool:
    medicare_specialty_code1 = TaxonomyData.medicare_specialty_code(code1)
    medicare_specialty_code2 = TaxonomyData.medicare_specialty_code(code2)
    return medicare_specialty_code1 == medicare_specialty_code2
