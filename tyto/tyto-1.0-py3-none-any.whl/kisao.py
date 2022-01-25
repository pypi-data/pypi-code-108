from .tyto import Ontology, EBIOntologyLookupService, installation_path, multi_replace

KISAO = Ontology(uri='http://www.biomodels.net/kisao/KISAO_FULL#', endpoints=[EBIOntologyLookupService])
