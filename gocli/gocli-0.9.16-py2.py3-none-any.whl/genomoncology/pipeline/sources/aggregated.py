import copy
from cytoolz.curried import curry, assoc
from cytoolz import reduceby

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from .base import LazyFileSource
from .delimited import do_split, DelimitedFileSource


def dict_seq_reducer(seq, dict_key, value_keys, add_kv_dict=None):
    """
    Reduce a sequence of dicts to single dict of dicts,
    optionally adding additional k,v pairs
    """
    reduced_dict = dict()
    for element in seq:
        if len(element["REF"]) > 1400 or len(element["ALT"]) >= 1400:
            continue
        reduced_dict[element[dict_key]] = dict()
        for key in value_keys:
            reduced_dict[element[dict_key]][key] = element[key]
        if add_kv_dict:
            for k, v in add_kv_dict.items():
                reduced_dict[element[dict_key]][k] = v
    return reduced_dict


@curry
class AggregatedFileSource(LazyFileSource):
    def __init__(
        self,
        filename,
        aggregate_key,
        backup_key=None,
        delimiter="\t",
        include_header=True,
        **meta,
    ):
        self.delimiter = delimiter
        self.aggregate_key = aggregate_key
        self.backup_key = backup_key
        self.include_header = include_header
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        iterator = super(AggregatedFileSource.func, self).__iter__()

        self.columns = next(iterator).strip().split(self.delimiter)

        if self.include_header:
            yield self.create_header()

        aggregated_d = reduceby(
            self.get_key_value, self.get_aggregate_value, iterator, dict
        )

        for key, value in aggregated_d.items():
            value["key"] = key
            value["__type__"] = DocType.AGGREGATE.value
            yield value

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    def get_key_value(self, x):
        column_index = self.columns.index(self.aggregate_key)
        elements = do_split(self.delimiter, x.replace("\n", ""))
        if column_index < len(elements) and elements[column_index] != "":
            key = elements[column_index]
        else:
            key = elements[self.columns.index(self.backup_key)].split(", ")[0]
        return key

    def get_aggregate_value(self, acc, x):
        hold_d = copy.deepcopy(acc)
        value_l = do_split(self.delimiter, x.replace("\n", ""))
        for i in range(len(value_l)):
            value = value_l[i] if value_l[i] != "" else "None"
            if self.columns[i] in hold_d:
                hold_d[self.columns[i]] = hold_d[self.columns[i]] + [value]
            else:
                hold_d[self.columns[i]] = [value]
        return hold_d


@curry
class AggregatedOmimFileSource(LazyFileSource):
    def __init__(self, filename, delimiter="\t", include_header=True, **meta):
        self.delimiter = delimiter
        self.include_header = include_header
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):  # pragma: no mccabe

        # noinspection PyUnresolvedReferences
        iterator = super(AggregatedOmimFileSource.func, self).__iter__()

        try:
            while True:
                row = [
                    data.strip()
                    for data in next(iterator).split(self.delimiter)
                ]
                if row[0].startswith("# Chromosome"):
                    self.columns = row
                    break
        except StopIteration:
            raise Exception("No header found!")

        if self.include_header:
            yield self.create_header()

        num_header_cols = len(self.columns)

        # Step 1: Get all the rows that do not have the main key
        # (we will deal with these rows later). And start aggregating
        # the rows together that have the same value for the main key.
        aggregated_records = {}
        backup_key_aggregated_records = []
        for row in iterator:
            if row.startswith("#"):
                continue  # this is a comment row and not data
            row_data = [data.strip() for data in row.split(self.delimiter)]

            if len(row_data) != num_header_cols:
                raise Exception(
                    f"Row {row_data} has {len(row_data)} "
                    f"columns but header row has {num_header_cols}."
                )

            key, is_main_key = self.get_key(row_data)
            if is_main_key:
                # combine this record with any others with this same key
                aggregated_value = aggregated_records.get(key, {})
                aggregated_records[key] = self.get_aggregate_value(
                    aggregated_value, row_data
                )
            else:
                # duplicate this row into multiple (one per backup key value)
                # and then we will deal with them later.
                for backup_key_value in key:
                    record = copy.deepcopy(row_data)
                    backup_key_index = self.columns.index(
                        self.get_backup_key()
                    )
                    record[backup_key_index] = backup_key_value
                    backup_key_aggregated_records.append(record)

        # Step 2: Now, deal with the records that did not have the main key,
        # but instead had the backup key.
        self.handle_leftover_rows(
            backup_key_aggregated_records, aggregated_records
        )

        # Step 3: for each aggregated record, yield the info
        for key, value in aggregated_records.items():
            value["key"] = key
            value["__type__"] = DocType.AGGREGATE.value
            yield value

    def get_main_key(self):
        return "Approved Symbol"

    def get_backup_key(self):
        return "Gene Symbols"

    def get_key(self, row_data):
        main_key_col_index = self.columns.index(self.get_main_key())
        if row_data[main_key_col_index] != "":
            return row_data[main_key_col_index], True
        else:
            # get the backup key
            backup_key_col_index = self.columns.index(self.get_backup_key())
            backup_key_values = row_data[backup_key_col_index].split(", ")
            return backup_key_values, False

    def get_aggregate_value(self, acc, row_data):
        hold_d = copy.deepcopy(acc)
        for i in range(len(row_data)):
            value = row_data[i] if row_data[i] != "" else "None"
            if self.columns[i] in hold_d:
                hold_d[self.columns[i]] = hold_d[self.columns[i]] + [value]
            else:
                hold_d[self.columns[i]] = [value]
        return hold_d

    def handle_leftover_rows(
        self, backup_key_rows, aggregated_records
    ):  # pragma: no mccabe
        backup_key_aggregated = {}
        for row_data in backup_key_rows:
            backup_key_index = self.columns.index(self.get_backup_key())
            backup_key = row_data[backup_key_index]
            if backup_key:
                chromosome_index = self.columns.index("# Chromosome")
                chromosome = row_data[chromosome_index]
                # check to see if there are any aggregated
                # records for this backup key
                existing_aggregated_record = aggregated_records.get(
                    backup_key, {}
                )

                if existing_aggregated_record:
                    # only merge this row with the existing aggregated
                    # record if the chromosomes match (x/y are considered
                    # a match)
                    aggregated_record_chr = existing_aggregated_record.get(
                        "# Chromosome", []
                    )
                    if (
                        chromosome in aggregated_record_chr
                        or (
                            chromosome == "chrX"
                            and "chrY" in aggregated_record_chr
                        )
                        or (
                            chromosome == "chrY"
                            and "chrX" in aggregated_record_chr
                        )
                    ):
                        aggregated_records[
                            backup_key
                        ] = self.get_aggregate_value(
                            existing_aggregated_record, row_data
                        )
                else:
                    # no pre-aggregated records already exist for this gene
                    # so create a new record
                    aggregated_value = backup_key_aggregated.get(
                        backup_key, {}
                    )
                    backup_key_aggregated[
                        backup_key
                    ] = self.get_aggregate_value(aggregated_value, row_data)
        # at the end here, add all of the backup_key_aggregated
        # records to the aggregated_records dict
        aggregated_records.update(backup_key_aggregated)

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }


@curry
class AggregatedCOSMICSources(LazyFileSource):
    def __init__(self, filename, cosmic_tsv, include_header=True, **meta):
        self.cosmic_vcf = filename
        self.cosmic_tsv = cosmic_tsv
        self.include_header = include_header
        self.meta = meta
        self.vcf_record_file_name = "vcf_records.txt"

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.AGGREGATE.value)

        super().__init__(filename)

    def __iter__(self):  # pragma: no mccabe
        # noinspection PyUnresolvedReferences

        self.log_file = open("cosmic_logs.txt", "w")

        if self.include_header:
            yield self.create_header()

        # iterate through TSV, aggregate together, and return map
        # from genomic_mutation_id to the aggregated records with that value
        self.log_file.write(
            "Step 1: Process the TSV file (parse and aggregate).\n"
        )
        (
            g_m_id_to_tsv_records,
            cosmic_tsv_no_g_m_id_dict,
        ) = self.parse_tsv_records()

        self.log_file.write(
            "Step 2: Loop through the VCF records and match "
            "them to aggregated TSV records.\n"
        )
        # iterate through the VCF, creating one value per row
        vcf_file_source = DelimitedFileSource(
            filename=self.cosmic_vcf,
            columns=[
                "#CHROM",
                "POS",
                "ID",
                "REF",
                "ALT",
                "QUAL",
                "FILTER",
                "INFO",
            ],
            delimiter="\t",
            skip_comment=True,
            comment_char="##",
            include_header=False,
        )

        merged_records = []
        vcfs_with_no_tsvs = []
        vcf_records_merged = 0
        for row in vcf_file_source:
            # do not include header
            if row["#CHROM"] == "#CHROM":
                continue

            # skip over too long REF/ALTs
            if len(row["REF"]) > 1400 or len(row["ALT"]) >= 1400:
                continue

            # get all of the values from this row
            row_dict = {}
            for col_name in ["#CHROM", "POS", "REF", "ALT", "ID", "INFO"]:
                row_dict[col_name] = row[col_name]

            # process vcf info
            self.process_vcf_info(row_dict)

            # merge this VCF record with a TSV
            merged_record = self.merge_vcf_with_tsv(
                row_dict, g_m_id_to_tsv_records
            )
            if merged_record is None:
                vcfs_with_no_tsvs.append(row_dict)
            else:
                merged_records.append(merged_record)
                vcf_records_merged += 1

            # add some logging to tell how far along we are.
            if vcf_records_merged % 1000 == 0:
                self.log_file.write(
                    f"{vcf_records_merged} VCF rows have "
                    f"been processed and merged with an "
                    f"aggregated TSV row.\n"
                )
        self.log_file.write(
            f"{vcf_records_merged} VCF rows " f"have been processed.\n"
        )

        self.log_file.write(
            "Seeing if there are any VCF records without a match.\n"
        )

        # See if there are any VCF records without a TSV match.
        # This indicates an error in the data and the script should stop.
        if len(vcfs_with_no_tsvs) > 0:
            vcf_no_match_text = "\n".join([str(v) for v in vcfs_with_no_tsvs])
            exception_text = (
                f"{len(vcfs_with_no_tsvs)} VCF rows do not "
                f"have a corresponding aggregated TSV match. "
                f"Those records are: \n"
                f"{vcf_no_match_text} \n"
            )
            self.log_file.write(exception_text)
            raise Exception(exception_text)
        else:
            self.log_file.write("All VCF records matched to a TSV record.\n")

        # At this point, we have a list of dictionaries, one per VCF line.
        # Each VCF line has been matched to a particular aggregated TSV
        # grouping based on GENOMIC_MUTATION_ID/LEGACY_ID/Gene.
        # Now, we need to do one final merge step where we merge
        # these merged records together if they have the same
        # GENOMIC_MUTATION_ID.
        self.log_file.write(
            "Step 3: Merge and yield records with the same "
            "GENOMIC_MUTATION_ID.\n"
        )
        g_m_id_merged_records = self.merge_records_with_g_m_id(merged_records)

        # yield these merged records
        self.log_file.write("Step 4: Yielding the merged records.\n")
        for _, value in g_m_id_merged_records.items():
            if value.get("#CHROM"):
                value["__type__"] = DocType.AGGREGATE.value
                yield value

        self.log_file.write(
            "Step 4: Yield the TSV records that do not have a "
            "GENOMIC_MUTATION_ID.\n"
        )
        for _, tsv_with_no_g_m_id in cosmic_tsv_no_g_m_id_dict.items():
            tsv_with_no_g_m_id["AA"] = [
                tsv_with_no_g_m_id.pop("Mutation AA", "")
            ]
            tsv_with_no_g_m_id["CDS"] = [
                tsv_with_no_g_m_id.pop("Mutation CDS", "")
            ]
            tsv_with_no_g_m_id["MUTATION_ID"] = [
                tsv_with_no_g_m_id.pop("MUTATION_ID", "")
            ]
            tsv_with_no_g_m_id["Gene name"] = [
                tsv_with_no_g_m_id.pop("Gene name", "")
            ]
            tsv_with_no_g_m_id["LEGACY_ID"] = tsv_with_no_g_m_id.pop(
                "LEGACY_MUTATION_ID", ""
            )
            tsv_with_no_g_m_id["__type__"] = DocType.AGGREGATE.value
            # manually set hgvs_g to None so that it doesn't
            # get calculated in the transform step
            tsv_with_no_g_m_id["hgvs_g"] = None
            yield tsv_with_no_g_m_id

        self.log_file.close()

    def merge_records_with_g_m_id(self, tsv_vcf_merged_records):
        merged_records = {}
        for tsv_vcf_merged_record in tsv_vcf_merged_records:
            g_m_id = tsv_vcf_merged_record.get("GENOMIC_MUTATION_ID")
            existing_merged_record = merged_records.get(g_m_id, {})
            merged_records[g_m_id] = self.do_merge_records(
                existing_merged_record, tsv_vcf_merged_record
            )
        return merged_records

    def do_merge_records(
        self, existing_record, new_record
    ):  # pragma: no mccabe
        # The main three fields that will differ for each record that
        # we are aggregating together are MUTATION_ID, CDS, and AA.
        # Let's stripe these values.
        striped_fields = ["MUTATION_ID", "CDS", "AA", "Gene name"]
        for field in striped_fields:
            existing_record[field] = existing_record.get(field, []) + [
                new_record.get(field)
            ]
        # We may also have other fields whose values differ, but this is
        # likely just bad data in cosmic, not actual differences. In this case
        # we will overwrite the field values with the info from the record with
        # the highest value of CNT.
        fields_that_may_differ = [
            "CNT",
            "LEGACY_ID",
            "TISSUES",
            "TISSUES_FREQ",
            "RESISTANCE_MUTATION",
        ]
        if "CNT" not in existing_record or (
            "CNT" in existing_record
            and new_record.get("CNT") > existing_record["CNT"]
        ):
            # we need to overwrite the values!
            for field in fields_that_may_differ:
                existing_record[field] = new_record.get(field)
        # set the rest of the fields
        for field_name, field_value in new_record.items():
            if field_name not in striped_fields + fields_that_may_differ:
                existing_record[field_name] = field_value
        return existing_record

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "meta": self.meta,
            "file_path": self.name,
        }

    def merge_vcf_with_tsv(self, vcf_record, g_m_id_to_tsvs):
        # For each row in the VCF file, find a matching TSV
        # record. To "match", the GENE/Gene name values need to match,
        # the GENOMIC_MUTATION_ID/ID (COSV) values need to match,
        # and the LEGACY_MUTATION_ID/LEGACY_ID values need to match.

        g_m_id = vcf_record.get("ID")
        gene = vcf_record.get("GENE")
        legacy_id = vcf_record.get("LEGACY_ID")

        # get the list of the TSV records that have
        # this genomic_mutation_id
        tsv_records_with_g_m_id = g_m_id_to_tsvs.get(g_m_id, [])
        matching_tsv = None
        for tsv_record in tsv_records_with_g_m_id:
            if gene == tsv_record.get(
                "Gene name"
            ) and legacy_id == tsv_record.get("LEGACY_MUTATION_ID"):
                # this is a match!
                matching_tsv = tsv_record
                break

        if matching_tsv is None:
            return None

        # If we made it down here, we have a matching TSV record!
        # Remove this particular record from tsv_records_with_g_m_id
        # because this has matched a VCF line and will not match any
        # other VCF lines.
        _ = tsv_records_with_g_m_id.remove(matching_tsv)
        if len(tsv_records_with_g_m_id) == 0:
            g_m_id_to_tsvs.pop(g_m_id)

        # Now, merge the matching_tsv record with the vcf line.
        # Note: for any shared fields (there shouldn't be any),
        # the VCF record will overwrite the TSV.
        matching_tsv.update(vcf_record)
        return matching_tsv

    def parse_tsv_records(self):

        self.log_file.write("Parsing the TSV file.\n")

        (
            cosmic_tsv_dict,
            cosmic_tsv_no_g_m_id_dict,
        ) = self.aggregate_cosmic_tsv()

        self.log_file.write(
            "Processing the tissue frequencies for the TSVs.\n"
        )

        # add tissue frequency
        cosmic_tsv_dict = self.process_tissue_freqs(cosmic_tsv_dict)
        cosmic_tsv_no_g_m_id_dict = self.process_tissue_freqs(
            cosmic_tsv_no_g_m_id_dict
        )

        # Group the aggregated TSV records by GENOMIC_MUTATION_ID.
        # This is basically just done to speed up performance in the
        # merge step following this. Multiple mutation_ids can have
        # the same genomic mutation id, so this dictionary will have a
        # key that's a particular genomic id and the value is a list
        # of the aggregated TSV dictionaries that have that g_m_id.
        self.log_file.write(
            "Grouping the TSV records by GENOMIC_MUTATION_ID "
            "for a quicker aggregation with the VCF files.\n"
        )
        g_m_id_to_tsv_records = self.group_tsv_by_g_m_id(cosmic_tsv_dict)
        return g_m_id_to_tsv_records, cosmic_tsv_no_g_m_id_dict

    def cosmic_key_value(self, element, is_tsv_no_g_m_id=False):
        if is_tsv_no_g_m_id:
            return element["LEGACY_MUTATION_ID"]
        return element["MUTATION_ID"], element["GENOMIC_MUTATION_ID"]

    def group_tsv_by_g_m_id(self, cosmic_tsv_dict):
        g_m_id_to_tsv_map = {}
        for key, tsv_record_info in cosmic_tsv_dict.items():
            mut_id, g_m_id = key
            record_copy = copy.deepcopy(tsv_record_info)
            record_copy["MUTATION_ID"] = mut_id
            record_copy["GENOMIC_MUTATION_ID"] = g_m_id
            g_m_id_to_tsv_map.setdefault(g_m_id, []).append(record_copy)
            # set the map's value for this key to None (for memory improvement)
            cosmic_tsv_dict[key] = None
        return g_m_id_to_tsv_map

    def aggregate_cosmic_tsv(self):
        # This method reads through the cosmic TSV and aggregates
        # records together that have the same MUTATION_ID and
        # GENOMIC_MUTATION_ID.

        # Read in the TSV source
        cosmic_tsv_source = DelimitedFileSource(
            filename=self.cosmic_tsv,
            columns=COSMIC_TSV_COLUMNS,
            delimiter="\t",
            include_header=False,
        )

        cosmic_tsv_dict = {}
        cosmic_tsv_no_g_m_id_dict = {}
        for tsv_record in cosmic_tsv_source:
            # Note: if there is no GENOMIC_MUTATION_ID, we will
            # aggregate on LEGACY_MUTATION_ID instead.
            is_tsv_no_g_m_id = tsv_record["GENOMIC_MUTATION_ID"] == ""
            merged_dict = (
                cosmic_tsv_no_g_m_id_dict
                if is_tsv_no_g_m_id
                else cosmic_tsv_dict
            )
            key = self.cosmic_key_value(tsv_record, is_tsv_no_g_m_id)
            aggregated_tsv_record = merged_dict.setdefault(
                key,
                {
                    "CNT": 0,
                    "TISSUES": {},
                    "TISSUES_FREQ": {},
                    "RESISTANCE_MUTATION": {},
                },
            )
            aggregated_tsv_record = self.aggregate(
                aggregated_tsv_record, tsv_record, is_tsv_no_g_m_id
            )
            merged_dict[key] = aggregated_tsv_record

        return cosmic_tsv_dict, cosmic_tsv_no_g_m_id_dict

    def handle_tsv_no_g_m_id(self, agg, x):
        # add MUTATION_ID to the aggregated dict
        mutation_id = x.get("MUTATION_ID")
        if "MUTATION_ID" not in agg:
            agg["MUTATION_ID"] = mutation_id
        else:
            # throw exception if the mutation_id for this row
            # does not match the mutation_id previously found
            # for this mutation ID
            if mutation_id != agg["MUTATION_ID"]:
                raise Exception(
                    f"TSV data error for record with no "
                    f"GENOMIC_MUTATION_ID. "
                    f"The record with LEGACY_MUTATION_ID "
                    f"{x.get('LEGACY_MUTATION_ID')} "
                    f"has more than one value for MUTATION_ID. "
                    f"Values found are: "
                    f"{agg['Mutation ID']} and {mutation_id}."
                )

        # add Mutation AA to the aggregated dict
        mutation_aa = x.get("Mutation AA")
        if "Mutation AA" not in agg:
            agg["Mutation AA"] = mutation_aa
        else:
            # throw exception if the mutation_aa for this row
            # does not match the mutation_aa previously found
            # for this mutation ID
            if mutation_aa != agg["Mutation AA"]:
                raise Exception(
                    f"TSV data error for record with no "
                    f"GENOMIC_MUTATION_ID. "
                    f"The record with LEGACY_MUTATION_ID "
                    f"{x.get('LEGACY_MUTATION_ID')} "
                    f"has more than one value for Mutation AA. "
                    f"Values found are: "
                    f"{agg['Mutation AA']} and {mutation_aa}."
                )

        # add Mutation CDS to the aggregated dict
        mutation_cds = x.get("Mutation CDS")
        if "Mutation CDS" not in agg:
            agg["Mutation CDS"] = mutation_cds
        else:
            # throw exception if the mutation_cds for this row
            # does not match the mutation_aa previously found
            # for this mutation ID
            if mutation_cds != agg["Mutation CDS"]:
                raise Exception(
                    f"TSV data error for record with no "
                    f"GENOMIC_MUTATION_ID. "
                    f"The record with LEGACY_MUTATION_ID "
                    f"{x.get('LEGACY_MUTATION_ID')} "
                    f"has more than one value for Mutation CDS. "
                    f"Values found are: "
                    f"{agg['Mutation CDS']} and {mutation_cds}."
                )

    def aggregate(self, agg, x, is_tsv_no_g_m_id=False):  # pragma: no mccabe
        # add gene name to the aggregated dict
        gene_name = x.get("Gene name")
        if "Gene name" not in agg:
            agg["Gene name"] = gene_name
        else:
            # throw exception if the gene name for this row
            # does not match the gene name previously found
            # for this mutation ID
            if gene_name != agg["Gene name"]:
                raise Exception(
                    f"TSV data error. Mutation ID {x.get('MUTATION_ID')} "
                    f"contains more than one value for Gene name. Values "
                    f"found are: {agg['Gene name']} and {gene_name}."
                )

        # add LEGACY_MUTATION_ID to the aggregated dict
        l_m_id = x.get("LEGACY_MUTATION_ID")
        if "LEGACY_MUTATION_ID" not in agg:
            agg["LEGACY_MUTATION_ID"] = l_m_id
        else:
            # throw exception if the l_m_id for this row
            # does not match the l_m_id previously found
            # for this mutation ID
            if l_m_id != agg["LEGACY_MUTATION_ID"]:
                raise Exception(
                    f"TSV data error. Mutation ID {x.get('MUTATION_ID')} "
                    f"contains more than one value for LEGACY_MUTATION_ID. "
                    f"Values found are: {agg['LEGACY_MUTATION_ID']} "
                    f"and {l_m_id}."
                )

        if is_tsv_no_g_m_id:
            self.handle_tsv_no_g_m_id(agg, x)

        # update the counts for the tissue sites and resistance mutations
        agg["CNT"] += 1
        if x.get("Primary site") in agg["TISSUES"]:
            agg["TISSUES"][x.get("Primary site")] += 1
        else:
            agg["TISSUES"][x.get("Primary site")] = 1
        if x.get("Resistance Mutation") in agg["RESISTANCE_MUTATION"]:
            agg["RESISTANCE_MUTATION"][x.get("Resistance Mutation")] += 1
        else:
            agg["RESISTANCE_MUTATION"][x.get("Resistance Mutation")] = 1
        return agg

    def process_tissue_freqs(self, cosmic_dict):
        for ck, cv in cosmic_dict.items():
            for k, v in cv["TISSUES"].items():
                cosmic_dict[ck]["TISSUES_FREQ"][k] = float(v) / cv["CNT"]
        return cosmic_dict

    def process_vcf_info(self, v):
        if v.get("#CHROM") == "#CHROM":
            return
        # add values from INFO column to the dictionary
        if "CDS" in v["INFO"]:
            v["CDS"] = [x for x in v["INFO"].split(";") if x[:3] == "CDS"][
                0
            ].split("=", 1)[1]
        else:
            v["CDS"] = "None"

        if "AA" in v["INFO"]:
            v["AA"] = [x for x in v["INFO"].split(";") if x[:2] == "AA"][
                0
            ].split("=", 1)[1]
        else:
            v["AA"] = "None"

        if "LEGACY_ID" in v["INFO"]:
            v["LEGACY_ID"] = [
                x for x in v["INFO"].split(";") if x[:9] == "LEGACY_ID"
            ][0].split("=", 1)[1]
        else:
            v["LEGACY_ID"] = "None"

        if "GENE" in v["INFO"]:
            v["GENE"] = [x for x in v["INFO"].split(";") if x[:4] == "GENE"][
                0
            ].split("=", 1)[1]
        else:
            v["Gene"] = "None"


COSMIC_TSV_COLUMNS = [
    "Gene name",
    "Accession Number",
    "Gene CDS length",
    "HGNC ID",
    "Sample name",
    "ID_sample",
    "ID_tumour",
    "Primary site",
    "Site subtype 1",
    "Site subtype 2",
    "Site subtype 3",
    "Primary histology",
    "Histology subtype 1",
    "Histology subtype 2",
    "Histology subtype 3",
    "Genome-wide screen",
    "GENOMIC_MUTATION_ID",
    "LEGACY_MUTATION_ID",
    "MUTATION_ID",
    "Mutation CDS",
    "Mutation AA",
    "Mutation Description",
    "Mutation zygosity",
    "LOH",
    "GRCh",
    "Mutation genome position",
    "Mutation strand",
    "SNP",
    "Resistance Mutation",
    "FATHMM prediction",
    "FATHMM score",
    "Mutation somatic status",
    "Pubmed_PMID",
    "ID_STUDY",
    "Sample Type",
    "Tumour origin",
    "Age",
    "HGVSP",
    "HGVSC",
    "HGVSG",
]
