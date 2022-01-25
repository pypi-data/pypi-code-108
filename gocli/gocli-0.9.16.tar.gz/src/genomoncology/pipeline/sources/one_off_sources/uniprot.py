import xml.etree.cElementTree as etree
import json

from cytoolz.curried import curry, assoc

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from ..base import LazyFileSource


@curry
class UniprotFileSource(LazyFileSource):
    def __init__(self, filename, **meta):
        self.filename = filename
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(
                self.meta, __TYPE__, DocType.UNIPROT_RECORD.value
            )

    def get_features_to_ignore(self):
        return [
            "splice variant",
            "mutagenesis site",
            "sequence variant",
            "non-consecutive residues",
            "non-standard amino acid",
            "non-terminal residue",
            "sequence conflict",
            "strand",
            "unsure residue",
        ]

    def __iter__(self):  # pragma: no mccabe
        yield self.create_header()

        context = etree.iterparse(self.filename, events=["start", "end"])
        # uniprot_id (accessions, but only grab first one)
        uniprot_id = None
        # protein name
        in_protein_rec_name = False
        is_in_component = False
        protein = None
        # gene name
        in_gene_name = False
        gene = None
        # features
        features_to_ignore = self.get_features_to_ignore()
        current_feature = None
        all_features = []
        # protein length
        protein_length = None
        # alternative names
        is_in_alternative_name = True
        alternative_names = []
        # canonical protein sequence ids
        current_uniprot_np_id = None
        no_molecule_canonical_nm_id = []
        no_molecule_canonical_np_id = []
        uniprot_canonical_nm_id = []
        uniprot_canonical_np_id = []
        is_in_refseq = False
        is_canonical_refseq = False
        molecule_tag_present = False
        for event, elem in context:
            tag = elem.tag.replace("{http://uniprot.org/uniprot}", "")
            # accession
            if event == "start" and tag == "accession" and uniprot_id is None:
                uniprot_id = elem.text
                continue
            # protein name
            if event == "start" and tag == "component":
                is_in_component = True
                continue
            if event == "end" and tag == "component":
                is_in_component = False
                continue
            if event == "start" and tag == "recommendedName":
                in_protein_rec_name = True
                continue
            if (
                in_protein_rec_name
                and not is_in_component
                and event == "end"
                and tag == "fullName"
            ):
                protein = elem.text
                in_protein_rec_name = False
                continue
            # alternative name
            if event == "start" and tag == "alternativeName":
                is_in_alternative_name = True
                continue
            if is_in_alternative_name and event == "end" and tag == "fullName":
                alternative_names.append(elem.text)
                is_in_alternative_name = False
                continue
            # gene name
            if event == "start" and tag == "gene":
                in_gene_name = True
                continue
            if (
                in_gene_name
                and event == "end"
                and tag == "name"
                and "type" in elem.attrib
                and elem.attrib["type"] == "primary"
            ):
                gene = elem.text
                in_gene_name = False
                continue
            # features
            if (
                event == "start"
                and tag == "feature"
                and "type" in elem.attrib
                and elem.attrib["type"] not in features_to_ignore
            ):
                current_feature = {"type": elem.attrib["type"]}
                if "description" in elem.attrib:
                    current_feature["description"] = elem.attrib["description"]
                continue
            if (
                current_feature is not None
                and event == "start"
                and tag == "position"
            ):
                current_feature["start"] = int(elem.attrib["position"])
                current_feature["end"] = int(elem.attrib["position"])
                continue
            if (
                current_feature is not None
                and event == "start"
                and tag == "begin"
            ):
                if "position" in elem.attrib:
                    current_feature["start"] = int(elem.attrib["position"])
                else:
                    # we will replace this later
                    current_feature["start"] = None
                continue
            if (
                current_feature is not None
                and event == "start"
                and tag == "end"
            ):
                if "position" in elem.attrib:
                    current_feature["end"] = int(elem.attrib["position"])
                else:
                    # we will replace this later
                    current_feature["end"] = None
                continue
            if (
                event == "end"
                and tag == "feature"
                and "type" in elem.attrib
                and elem.attrib["type"] not in features_to_ignore
            ):
                # add the current feature to the features list
                all_features.append(current_feature)
                current_feature = None
                continue
            # protein length
            if (
                event == "start"
                and tag == "sequence"
                and "length" in elem.attrib
            ):
                protein_length = elem.attrib["length"]
                continue
            # canonical np/nm ids
            if (
                event == "start"
                and tag == "dbReference"
                and elem.attrib["type"] == "RefSeq"
            ):
                is_in_refseq = True
                # get the current uniprot np id (in case it's canonical)
                if current_uniprot_np_id is None:
                    current_uniprot_np_id = elem.attrib["id"]
                continue
            if event == "start" and tag == "molecule" and is_in_refseq:
                molecule_tag_present = True
                # see if this is actually canonical np or not
                the_id = elem.attrib["id"]
                if the_id.endswith("-1"):
                    is_canonical_refseq = True
                    uniprot_canonical_np_id.append(current_uniprot_np_id)
                else:
                    # clear out the current nm that we previously set
                    current_uniprot_np_id = None
                continue
            if (
                event == "start"
                and tag == "property"
                and is_in_refseq
                and (is_canonical_refseq or not molecule_tag_present)
            ):
                # if no molecule tag was present, then also
                # set the canonical np
                if not molecule_tag_present:
                    no_molecule_canonical_np_id.append(current_uniprot_np_id)
                    no_molecule_canonical_nm_id.append(elem.attrib["value"])
                    current_uniprot_np_id = None
                else:
                    # since this is canonical, set the canonical nm id
                    uniprot_canonical_nm_id.append(elem.attrib["value"])
                continue
            if event == "end" and tag == "dbReference" and is_in_refseq:
                is_in_refseq = False
                is_canonical_refseq = False
                molecule_tag_present = False
                current_uniprot_np_id = None
                continue
            # end of entry record
            if event == "end" and tag == "entry":
                # process features (replace None start/ends)
                self.process_features(all_features)

                return_d = {
                    "uniprot_id": uniprot_id,
                    "gene": gene,
                    "protein_full_name": protein,
                    "protein_length": protein_length,
                    "protein_alternate_names": alternative_names,
                    "uniprot_canonical_nm_id": uniprot_canonical_nm_id
                    if len(uniprot_canonical_nm_id) > 0
                    else no_molecule_canonical_nm_id,
                    "uniprot_canonical_np_id": uniprot_canonical_np_id
                    if len(uniprot_canonical_np_id) > 0
                    else no_molecule_canonical_np_id,
                    "features": [
                        json.dumps(feature) for feature in all_features
                    ],
                    "__type__": DocType.UNIPROT_RECORD,
                }
                uniprot_id = None
                gene = None
                protein = None
                is_in_component = False
                in_protein_rec_name = False
                current_feature = None
                all_features = []
                protein_length = None
                alternative_names = []
                uniprot_canonical_nm_id = []
                uniprot_canonical_np_id = []
                no_molecule_canonical_nm_id = []
                no_molecule_canonical_np_id = []
                current_uniprot_np_id = None
                is_canonical_refseq = False
                is_in_refseq = False
                molecule_tag_present = False
                elem.clear()
                yield return_d

    def process_features(self, features):
        # if start/end is none, set it to be whatever the other value is
        # so they are the same. If both are none, no changes
        for feature in features:
            if feature.get("start") is None and feature.get("end") is not None:
                feature["start"] = feature["end"]
            elif (
                feature.get("end") is None and feature.get("start") is not None
            ):
                feature["end"] = feature["start"]

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "meta": self.meta,
            "fields": [
                "gene",
                "protein_full_name",
                "uniprot_id",
                "protein_length",
                "alternative_names",
                "uniprot_canonical_nm_id",
                "uniprot_canonical_np_id",
                "features",
            ],
        }
