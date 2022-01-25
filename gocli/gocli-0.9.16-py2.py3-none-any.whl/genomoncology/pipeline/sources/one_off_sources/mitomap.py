from cytoolz.curried import curry, assoc

from genomoncology.parse import DocType, __TYPE__, __CHILD__
from ..base import LazyFileSource

import sqlite3
from tempfile import NamedTemporaryFile

from gosdk import logger

import re
import json

TAG_RE = re.compile(r"<[^>]+>")


@curry
class MitomapFileSource(LazyFileSource):
    def __init__(self, dump_file_name, keep_db=False, **meta):
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(
                self.meta, __TYPE__, DocType.MITOMAP_RECORD.value
            )

        self.dump_file = open(dump_file_name, "r")
        self.table_names = [
            "mitomap.genbank",
            "mitomap.gbcontrol",
            "mitomap.genbank_count",
            "mitomap.genbank_haplogroup",
            "mitomap.mitotip",
            "mitomap.helix",
            "mitomap.apogee",
        ]
        self.table_indexed_fields = {
            "mitomap.genbank": ["tpos", "qnt"],
            "mitomap.gbcontrol": ["tpos", "qnt"],
            "mitomap.genbank_count": ["haplogroup", "alt", "pos"],
            "mitomap.genbank_haplogroup": ["haplogroup"],
            "mitomap.mitotip": ["pos", "ref", "alt"],
            "mitomap.helix": ["position", "refna", "regna"],
            "mitomap.apogee": ["position", "refna", "regna"],
        }
        self.lines = self.dump_file.readlines()
        self.table_line_boundaries = {}
        self.table_fields = {}
        # map of pos-ref-alt to set of haplogroups
        self.pra_map = {}
        # maps to gather counts during genbank table load
        self.var_haplo_cnt_map = {}
        self.haplo_cnt_map = {}
        self.fl_count_map = {}
        # set to get total fl count
        self.genbank_id_set = set()
        self.db = sqlite3.connect(":memory:")
        self.temp_file = NamedTemporaryFile(delete=(not keep_db))
        if keep_db:
            logger.get_logger().debug(
                "Mitomap database can be found at: {0}".format(
                    self.temp_file.name
                )
            )
        self.db = sqlite3.connect(self.temp_file.name)
        self.cursor = self.db.cursor()
        self.create_tables_in_db()

    # METHODS TO GET INFO ON TABLE START/END LINES
    def line_num_end_of_input(self, line_number, lines):
        for the_line in lines:
            if the_line.startswith("\\."):
                return line_number
            line_number += 1

    def get_table_line_boundaries(self, lines, starting_num, table_name):
        end_of_input = self.line_num_end_of_input(starting_num, lines)
        self.table_line_boundaries[table_name] = (starting_num, end_of_input)
        return end_of_input

    # METHODS TO CREATE SQL STATEMENTS
    def format_fields_with_data_types(self, fields):
        structured_fields = []
        for i in range(len(fields)):
            structured_fields.append(fields[i].strip() + " TEXT")
        return ",".join(structured_fields)

    def create_question_mark_string(self, length_of_fields):
        question_marks = ["?"] * length_of_fields
        return "{}".format(",".join(question_marks))

    def create_index_for_table(self, table_name, indexed_fields):
        return "CREATE INDEX index_{0} ON {0} ({1});".format(
            table_name, ",".join(indexed_fields)
        )

    def create_table_statement(self, table_name, fields):
        structured_fields = self.format_fields_with_data_types(fields)
        return "CREATE TABLE {0}({1});".format(table_name, structured_fields)

    def insert_into_table_statement(self, table_name, fields):
        return "INSERT INTO {0}({1}) VALUES({2});".format(
            table_name,
            ",".join(fields),
            self.create_question_mark_string(len(fields)),
        )

    def select_data_statement(self, table_name, selected_fields):
        return "SELECT {0} FROM {1};".format(
            ",".join(selected_fields), table_name
        )

    def select_cr_count(self, tpos, qnt):
        return (
            "SELECT count(*) FROM gbcontrol WHERE tpos='{0}' AND "
            "qnt='{1}';".format(tpos, qnt)
        )

    def select_total_count(self, table_name):
        return "SELECT count(DISTINCT genbank_id) FROM {0}".format(table_name)

    def select_variant_haplogroup_count(self, haplogroup, qnt, tpos):
        return (
            "SELECT cnt FROM genbank_count WHERE haplogroup='{0}' "
            "and alt='{1}' and pos='{2}';".format(haplogroup, qnt, tpos)
        )

    def select_haplogroup_count(self, haplogroup):
        return (
            "SELECT count(genbank_id) FROM genbank_haplogroup WHERE "
            "haplogroup='{0}';".format(haplogroup)
        )

    def select_mitotip(self, tpos, tnt, qnt):
        return (
            "SELECT score FROM mitotip WHERE pos='{0}' "
            "AND ref='{1}' AND alt='{2}'".format(tpos, tnt, qnt)
        )

    def select_helix_info(self, tpos, tnt, qnt):
        return (
            "SELECT counts_hom, af_hom, gene FROM helix WHERE position='{0}' "
            "AND refna='{1}' AND regna='{2}'".format(tpos, tnt, qnt)
        )

    def select_apogee_info(self, tpos, tnt, qnt):
        return (
            "SELECT score, status FROM apogee WHERE position='{0}' "
            "AND refna='{1}' AND regna='{2}'".format(tpos, tnt, qnt)
        )

    # METHODS TO EXECUTE SQL STATEMENTS
    def create_table(self, table_name, fields):
        self.cursor.execute(self.create_table_statement(table_name, fields))
        self.db.commit()

    def insert_into_table(
        self, table_name, fields, all_values, indexed_fields
    ):
        self.cursor.executemany(
            self.insert_into_table_statement(table_name, fields), all_values
        )
        if indexed_fields is not None:
            self.cursor.execute(
                self.create_index_for_table(table_name, indexed_fields)
            )
        self.db.commit()

    def get_table_data(self, table_name, selected_fields):
        self.cursor.execute(
            self.select_data_statement(table_name, selected_fields)
        )
        return self.cursor.fetchall()

    def get_fl_count(self, tpos, qnt):
        return self.fl_count_map[(tpos, qnt)]

    def get_cr_count(self, tpos, qnt):
        self.cursor.execute(self.select_cr_count(tpos, qnt))
        return self.cursor.fetchone()[0]

    def get_total_fl_count(self):
        return len(self.genbank_id_set)

    def get_total_count(self, table_name):
        self.cursor.execute(self.select_total_count(table_name))
        return self.cursor.fetchone()[0]

    def get_variant_haplogroup_count(self, haplogroup, qnt, tpos):
        self.cursor.execute(
            self.select_variant_haplogroup_count(haplogroup, qnt, tpos)
        )
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return 0  # return 0 if not present

    def get_haplogroup_count(self, haplogroup):
        self.cursor.execute(self.select_haplogroup_count(haplogroup))
        return self.cursor.fetchone()[0]

    def get_mitotip(self, tpos, tnt, qnt):
        self.cursor.execute(self.select_mitotip(tpos, tnt, qnt))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0]
        return None  # return None if no score

    def get_helix_info(self, tpos, tnt, qnt):
        self.cursor.execute(self.select_helix_info(tpos, tnt, qnt))
        result = self.cursor.fetchone()
        if result is not None:
            return result[0], 195983, result[1], result[2]
        return None, None, None, None  # return None if no helix info

    def get_apogee(self, tpos, tnt, qnt):
        apogee_list = []
        self.cursor.execute(self.select_apogee_info(tpos, tnt, qnt))
        results = self.cursor.fetchall()
        for result in results:
            info = {"score": result[0], "consensus": result[1]}
            apogee_list.append(json.dumps(info))
        return apogee_list

    # METHODS TO CREATE AND POPULATE THE TABLES
    def parse_and_set_genbank_data(self, the_lines):
        data = []
        for line in the_lines:
            line = line.replace("\n", "")
            record = line.split("\t")
            # get the pos, ref, and alt to see if duplicate hgvs
            gb_fields = self.table_fields["mitomap.genbank"]
            pos = record[gb_fields.index("tpos")]
            ref = record[gb_fields.index("tnt")]
            alt = record[gb_fields.index("qnt")]
            # get haplogroup
            haplogroup = record[gb_fields.index("haplogroup")]
            pra_key = (pos, ref, alt)
            if pra_key not in self.pra_map.keys():
                self.pra_map[pra_key] = {"haplogroup_set": set([haplogroup])}
                # add the first occurrence to the genbank table
                data.append(tuple(record))
            else:
                self.pra_map[pra_key]["haplogroup_set"].add(haplogroup)

            # calculate fl_count
            fl_key = (pos, alt)
            if fl_key not in self.fl_count_map.keys():
                self.fl_count_map[fl_key] = 1
            else:
                self.fl_count_map[fl_key] = self.fl_count_map[fl_key] + 1

            # add genbank id to set to use to calculate total fl count
            genbank_id = record[gb_fields.index("genbank_id")]
            self.genbank_id_set.add(genbank_id)

        return data

    def set_table_data(self, the_lines):
        data = []
        for line in the_lines:
            line = line.replace("\n", "")
            record = line.split("\t")
            data.append(tuple(record))
        return data

    def create_and_populate_table(
        self, table_name, the_lines, fields, indexed_fields
    ):
        if table_name == "mitomap.genbank":
            data = self.parse_and_set_genbank_data(the_lines)
        else:
            data = self.set_table_data(the_lines)
        # remove mitomap. from the name when actually creating the db table
        table_name = table_name.replace("mitomap.", "")
        self.create_table(table_name, fields)
        self.insert_into_table(table_name, fields, data, indexed_fields)

    def create_tables_in_db(self):
        line_num = 0
        while line_num < len(self.lines):
            line = self.lines[line_num]
            if line.startswith("COPY") and line.split()[1] in self.table_names:
                table_name = line.split()[1]
                field_names = re.search(r"\((.*?)\)", line).group(1)
                self.table_fields[table_name] = list(
                    map(str.strip, field_names.split(","))
                )
                # get the line boundaries
                table_end_line = self.get_table_line_boundaries(
                    self.lines[line_num + 1 :], line_num + 1, table_name
                )
                # create and populate the table
                self.create_and_populate_table(
                    table_name,
                    self.lines[line_num + 1 : table_end_line],
                    self.table_fields[table_name],
                    self.table_indexed_fields[table_name],
                )
                line_num = table_end_line + 1
            line_num += 1

    def get_insertion(self, tnt, qnt):
        return qnt.replace(tnt, "", 1)

    def get_hgvs_g(self, tpos, tnt, qnt, ntchange):
        if ntchange == "insertion":
            insertion = self.get_insertion(tnt, qnt)
            return "NC_012920.1:g.{0}_{1}ins{2}".format(
                tpos, int(tpos) + 1, insertion
            )
        if ntchange == "deletion":
            return "NC_012920.1:g.{0}del{1}".format(tpos, tnt)
        return "NC_012920.1:g.{0}{1}>{2}".format(tpos, tnt, qnt)

    def get_csra(self, tpos, tnt, qnt):
        return f"chrMT|{tpos}|{tnt}|{qnt}|GRCh37"

    def get_freq(self, numer, denom):
        return 0 if denom == 0 else numer / denom

    def remove_html_tags(self, text):
        text_array = [
            non_tag_text.strip()
            for non_tag_text in TAG_RE.split(text)
            if non_tag_text.strip()
        ]
        return " ".join(text_array)

    def __iter__(self):  # pragma: no mccabe
        yield self.create_header()

        selected_fields = [
            "genbank_id",
            "tpos",
            "tnt",
            "qnt",
            "ntchange",
            "mmutid",
            "disease",
            "cal_aachange",
            "conservation",
            "haplogroup",
            "calc_locus",
        ]
        records = self.get_table_data("genbank", selected_fields)
        fl_total_count = self.get_total_fl_count()
        cr_total_count = self.get_total_count("gbcontrol")

        for rec in records:
            # get fields for each record
            tpos = rec[selected_fields.index("tpos")]
            tnt = rec[selected_fields.index("tnt")]
            qnt = rec[selected_fields.index("qnt")]
            ntchange = rec[selected_fields.index("ntchange")]
            hgvs_g = self.get_hgvs_g(tpos, tnt, qnt, ntchange)
            csra = self.get_csra(tpos, tnt, qnt)
            disease = rec[selected_fields.index("disease")]
            aa_change = self.remove_html_tags(
                rec[selected_fields.index("cal_aachange")]
            )
            conservation = rec[selected_fields.index("conservation")]
            loci = rec[selected_fields.index("calc_locus")]
            # get haplogroups for this pos-ref-alt
            pra_key = (tpos, tnt, qnt)
            haplo_set = self.pra_map[pra_key]["haplogroup_set"]
            haplogroups = list(haplo_set)

            # get calculated fields
            fl_count = self.get_fl_count(tpos, qnt)
            cr_count = self.get_cr_count(tpos, qnt)
            fl_frequency = self.get_freq(fl_count, fl_total_count)
            cr_frequency = self.get_freq(cr_count, cr_total_count)
            mitoTIP = self.get_mitotip(tpos, tnt, qnt)
            h_count, h_total_count, h_frequency, h_gene = self.get_helix_info(
                tpos, tnt, qnt
            )
            apogee_list = self.get_apogee(tpos, tnt, qnt)

            var_haplo_counts = []
            haplo_counts = []
            for haplo in haplogroups:
                var_haplo_counts.append(
                    self.var_haplo_cnt_map.setdefault(
                        (haplo, qnt, tpos),
                        self.get_variant_haplogroup_count(haplo, qnt, tpos),
                    )
                )
                haplo_counts.append(
                    self.haplo_cnt_map.setdefault(
                        haplo, self.get_haplogroup_count(haplo)
                    )
                )

            yield {
                "hgvs_g": hgvs_g,
                "csra": csra,
                "disease": disease,
                "aa_change": aa_change,
                "conservation": conservation,
                "haplogroups": haplogroups,
                "loci": loci,
                "fl_count": fl_count,
                "cr_count": cr_count,
                "fl_frequency": fl_frequency,
                "cr_frequency": cr_frequency,
                "variant_haplogroup_counts": var_haplo_counts,
                "haplogroup_counts": haplo_counts,
                "mitoTIP": mitoTIP,
                "helix_count": h_count,
                "helix_total_count": h_total_count,
                "helix_frequency": h_frequency,
                "gene": h_gene,
                "apogee": apogee_list,
                "__type__": DocType.MITOMAP_RECORD.value,
            }

        self.cursor.close()
        self.db.close()

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "meta": self.meta,
            "fields": [
                "hgvs_g",
                "csra",
                "disease",
                "aa_change",
                "conservation",
                "haplogroups",
                "loci",
                "fl_count",
                "cr_count",
                "fl_frequency",
                "cr_frequency",
                "variant_haplogroup_counts",
                "haplogroup_counts",
                "mitoTIP",
                "helix_count",
                "helix_total_count",
                "helix_frequency",
                "gene",
                "apogee",
            ],
        }
