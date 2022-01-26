import json
from typing import List, TypeVar

import pandas as pd

from magnumapi.cadata.CableDefinition import CableDefinition
from magnumapi.cadata.ConductorDefinition import ConductorDefinition
from magnumapi.cadata.FilamentDefinition import FilamentDefinition
from magnumapi.cadata.InsulationDefinition import InsulationDefinition
from magnumapi.cadata.QuenchDefinition import QuenchDefinition
from magnumapi.cadata.RemFitDefinition import RemFitDefinition
from magnumapi.cadata.StrandDefinition import StrandDefinition
from magnumapi.cadata.TransientDefinition import TransientDefinition
import magnumapi.tool_adapters.roxie.RoxieAPI as RoxieAPI
import magnumapi.commons.json_file as json_file
import magnumapi.commons.text_file as text_file
from magnumapi.commons.DirectoryManager import DirectoryManager

T = TypeVar('T')


class CableDatabase:
    """ Class providing an interface to read, write, and access cable database definitions.

    """
    keyword_to_class = {'INSUL': InsulationDefinition,
                        'REMFIT': RemFitDefinition,
                        'FILAMENT': FilamentDefinition,
                        'STRAND': StrandDefinition,
                        'TRANSIENT': TransientDefinition,
                        'QUENCH': QuenchDefinition,
                        'CABLE': CableDefinition,
                        'CONDUCTOR': ConductorDefinition}

    def __init__(self,
                 insul_defs: List[InsulationDefinition],
                 remfit_defs: List[RemFitDefinition],
                 filament_defs: List[FilamentDefinition],
                 strand_defs: List[StrandDefinition],
                 transient_defs: List[TransientDefinition],
                 quench_defs: List[QuenchDefinition],
                 cable_defs: List[CableDefinition],
                 conductor_defs: List[ConductorDefinition]) -> None:

        self.insul_defs = insul_defs
        self.remfit_defs = remfit_defs
        self.filament_defs = filament_defs
        self.strand_defs = strand_defs
        self.transient_defs = transient_defs
        self.quench_defs = quench_defs
        self.cable_defs = cable_defs
        self.conductor_defs = conductor_defs

    @classmethod
    def initialize_definitions(cls, cadata_file_path: str, keyword: str) -> List[T]:
        """ Method initializing a list of definitions of a given type from a given cadata file. Method reads a cadata
        file and returns a dictionary, which is converted into a list of dictionaries. The list of dictionaries is
        converted into a list of definitions.

        :param cadata_file_path: a path to a cadata file
        :param keyword: a cadata table name
        :return: a list of cadata definitions for a given table name
        """
        ClassDefinition = cls.keyword_to_class[keyword.upper()]
        try:
            df = RoxieAPI.read_bottom_header_table(cadata_file_path, keyword=keyword)
            df = df.drop(columns=['No'])
            df = df.rename(columns=ClassDefinition.get_roxie_to_magnum_dct())
            df_dicts = df.to_dict('records')
            defs = []
            for df_dict in df_dicts:
                defs.append(ClassDefinition(**df_dict))

            return defs
        except IndexError:
            return [ClassDefinition(name='', comment='')]

    def get_insul_definition(self, condname: str) -> InsulationDefinition:
        """ Method returning an insulation definition for a given conductor name

        :param condname: conductor name
        :return: insulation definition if match, otherwise a KeyError is thrown
        """
        insul_name = self.get_conductor_definition(condname).insulation

        return _find_matching_definition(self.insul_defs, insul_name, 'insulation')

    def get_remfit_definition(self, condname: str) -> RemFitDefinition:
        """ Method returning a remfit definition for a given conductor name

        :param condname: conductor name
        :return: remfit definition if match, otherwise a KeyError is thrown
        """
        remfit_name = self.get_filament_definition(condname).fit_perp

        return _find_matching_definition(self.remfit_defs, remfit_name, 'rem_fit')

    def get_filament_definition(self, condname: str) -> FilamentDefinition:
        """ Method returning a filament definition for a given conductor name

        :param condname: conductor name
        :return: filament definition if match, otherwise a KeyError is thrown
        """
        filament_name = self.get_conductor_definition(condname).filament

        return _find_matching_definition(self.filament_defs, filament_name, 'filament')

    def get_strand_definition(self, condname: str) -> StrandDefinition:
        """ Method returning a strand definition for a given conductor name

        :param condname: conductor name
        :return: strand definition if match, otherwise a KeyError is thrown
        """
        strand_name = self.get_conductor_definition(condname).strand

        return _find_matching_definition(self.strand_defs, strand_name, 'strand')

    def get_transient_definition(self, condname: str) -> TransientDefinition:
        """ Method returning a transient definition for a given conductor name. If there is no transient definition for
        a given condname, then an empty transient definition is returned.

        :param condname: conductor name
        :return: transient definition if match, otherwise a KeyError is thrown
        """
        trans_name = self.get_conductor_definition(condname).transient

        if trans_name == 'NONE':
            return TransientDefinition(name='', comment='')

        return _find_matching_definition(self.transient_defs, trans_name, 'transient')

    def get_quench_definition(self, condname: str) -> QuenchDefinition:
        """ Method returning a quench definition for a given conductor name. If there is no quench definition for
        a given condname, then an empty quench definition is returned.

        :param condname: conductor name
        :return: quench definition if match, otherwise a KeyError is thrown
        """
        quench_name = self.get_conductor_definition(condname).quench_mat

        if quench_name == 'NONE':
            return QuenchDefinition(name='', comment='')

        return _find_matching_definition(self.quench_defs, quench_name, 'quench')

    def get_cable_definition(self, condname: str) -> CableDefinition:
        """ Method returning an insulation definition for a given conductor name

        :param condname: conductor name
        :return: insulation definition if match, otherwise a KeyError is thrown
        """
        geometry_name = self.get_conductor_definition(condname).cable_geom

        return _find_matching_definition(self.cable_defs, geometry_name, 'cable')

    def get_conductor_definition(self, condname: str) -> ConductorDefinition:
        """ Method returning an insulation definition for a given conductor name

        :param condname: conductor name
        :return: insulation definition if match, otherwise a KeyError is thrown
        """
        return _find_matching_definition(self.conductor_defs, condname, 'conductor')

    @classmethod
    def read_json(cls, json_file_path: str) -> "CableDatabase":
        """ Method reading a json file and returning an initialized CableDatabase instance. Some definitions are
        optional. In this case, the

        :param json_file_path: a path
        :return: a CableDatabase instance with initialized lists of definitions
        """
        data = json_file.read(json_file_path)

        # Optional definitions
        if 'remfit' in data:
            remfit_defs = [RemFitDefinition(**remfit_def) for remfit_def in data['remfit']]
        else:
            remfit_defs = [RemFitDefinition(name='', comment='')]

        if 'transient' in data:
            transient_defs = [TransientDefinition(**transient_def) for transient_def in data['transient']]
        else:
            transient_defs = [TransientDefinition(name='', comment='')]

        if 'quench' in data:
            quench_defs = [QuenchDefinition(**quench_def) for quench_def in data['quench']]
        else:
            quench_defs = [QuenchDefinition(name='', comment='')]

        # Mandatory definitions
        insul_defs = [InsulationDefinition(**insulation_def) for insulation_def in data['insulation']]
        filament_defs = [FilamentDefinition(**filament_def) for filament_def in data['filament']]
        strand_defs = [StrandDefinition(**strand_def) for strand_def in data['strand']]
        cable_defs = [CableDefinition(**cable_def) for cable_def in data['cable']]
        conductor_defs = [ConductorDefinition(**conductor_def) for conductor_def in data['conductor']]

        return CableDatabase(insul_defs=insul_defs,
                             remfit_defs=remfit_defs,
                             filament_defs=filament_defs,
                             strand_defs=strand_defs,
                             transient_defs=transient_defs,
                             quench_defs=quench_defs,
                             cable_defs=cable_defs,
                             conductor_defs=conductor_defs)

    def write_json(self, json_output_path: str) -> None:
        """ Method writing a CableDatabase instance into a json file.

        :param json_output_path: a path to an output json file
        """
        json_cadata = {"insulation": self._get_insulation_definitions_as_list_of_dict(),
                       "remfit": self._get_remfit_definitions_as_list_of_dict(),
                       "filament": self._get_filament_definitions_as_list_of_dict(),
                       "strand": self._get_strand_definitions_as_list_of_dict(),
                       "transient": self._get_transient_definitions_as_list_of_dict(),
                       "quench": self._get_quench_definitions_as_list_of_dict(),
                       "cable": self._get_cable_definitions_as_list_of_dict(),
                       "conductor": self._get_conductor_definitions_as_list_of_dict()}

        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(json_cadata, f, ensure_ascii=False, indent=4)

    def _get_conductor_definitions_as_list_of_dict(self):
        """ Method returning a list of conductor definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with conductor definitions sorted with ROXIE order
        """
        return [ConductorDefinition.reorder_dct(conductor_def.__dict__) for conductor_def in self.conductor_defs]

    def _get_cable_definitions_as_list_of_dict(self):
        """ Method returning a list of cable definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with cable definitions sorted with ROXIE order
        """
        return [CableDefinition.reorder_dct(cable_def.__dict__) for cable_def in self.cable_defs]

    def _get_quench_definitions_as_list_of_dict(self):
        """ Method returning a list of quench definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with quench definitions sorted with ROXIE order
        """
        return [QuenchDefinition.reorder_dct(quench_def.__dict__) for quench_def in self.quench_defs]

    def _get_transient_definitions_as_list_of_dict(self):
        """ Method returning a list of transient definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with transient definitions sorted with ROXIE order
        """
        return [TransientDefinition.reorder_dct(transient_def.__dict__) for transient_def in self.transient_defs]

    def _get_strand_definitions_as_list_of_dict(self):
        """ Method returning a list of strand definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with strand definitions sorted with ROXIE order
        """
        return [StrandDefinition.reorder_dct(strand_def.__dict__) for strand_def in self.strand_defs]

    def _get_filament_definitions_as_list_of_dict(self):
        """ Method returning a list of filament definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with filament definitions sorted with ROXIE order
        """
        return [FilamentDefinition.reorder_dct(filament_def.__dict__) for filament_def in self.filament_defs]

    def _get_remfit_definitions_as_list_of_dict(self):
        """ Method returning a list of remfit definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with remfit definitions sorted with ROXIE order
        """
        return [RemFitDefinition.reorder_dct(remfit_def.__dict__) for remfit_def in self.remfit_defs]

    def _get_insulation_definitions_as_list_of_dict(self):
        """ Method returning a list of insulation definitions as a list of dictionaries sorted with ROXIE order.

        :return: a list of dictionaries with insulation definitions sorted with ROXIE order
        """
        return [InsulationDefinition.reorder_dct(insul_def.__dict__) for insul_def in self.insul_defs]

    @classmethod
    def read_cadata(cls, cadata_file_path: str) -> "CableDatabase":
        """ Method reading a cadata file and returns an initialized CableDatabase instance with a list of definitions.

        :param cadata_file_path: a path to a cadata file
        :return: a CableDatabase instance with initialized lists of definitions
        """
        DirectoryManager.check_if_file_exists(cadata_file_path)

        return CableDatabase(insul_defs=cls.initialize_definitions(cadata_file_path, keyword='INSUL'),
                             remfit_defs=cls.initialize_definitions(cadata_file_path, keyword='REMFIT'),
                             filament_defs=cls.initialize_definitions(cadata_file_path, keyword='FILAMENT'),
                             strand_defs=cls.initialize_definitions(cadata_file_path, keyword='STRAND'),
                             transient_defs=cls.initialize_definitions(cadata_file_path, keyword='TRANSIENT'),
                             quench_defs=cls.initialize_definitions(cadata_file_path, keyword='QUENCH'),
                             cable_defs=cls.initialize_definitions(cadata_file_path, keyword='CABLE'),
                             conductor_defs=cls.initialize_definitions(cadata_file_path, keyword='CONDUCTOR'))

    def write_cadata(self, cadata_output_path: str) -> None:
        """ Method writing a CableDatabase instance into a cadata file.

        :param cadata_output_path: a path to an output cadata file
        """
        output = ['VERSION 11',
                  self._convert_definition_df_to_bottom_header_str(self.get_insul_df(), 'INSUL'),
                  self._convert_definition_df_to_bottom_header_str(self.get_remfit_df(), 'REMFIT'),
                  self._convert_definition_df_to_bottom_header_str(self.get_filament_df(), 'FILAMENT'),
                  self._convert_definition_df_to_bottom_header_str(self.get_strand_df(), 'STRAND'),
                  self._convert_definition_df_to_bottom_header_str(self.get_transient_df(), 'TRANSIENT'),
                  self._convert_definition_df_to_bottom_header_str(self.get_quench_df(), 'QUENCH'),
                  self._convert_definition_df_to_bottom_header_str(self.get_cable_df(), 'CABLE'),
                  self._convert_definition_df_to_bottom_header_str(self.get_conductor_df(), 'CONDUCTOR')
                  ]

        # Write to a text file
        text_file.writelines(cadata_output_path, output, endline='\n\n')

    @classmethod
    def _convert_definition_df_to_bottom_header_str(cls, df: pd.DataFrame, keyword: str) -> str:
        """ Method converting a definition dataframe to a string representation as a bottom header table for ROXIE.

        :param df: input dataframe with definitions
        :param keyword: name of a table
        :return: a string formatted as a bottom header table of ROXIE
        """
        # Get the definition class
        ClassDefinition = cls.keyword_to_class[keyword.upper()]
        # Convert to a dataframe
        df = df.rename(columns=ClassDefinition.get_magnum_to_roxie_dct())
        # Take only those columns that are needed for ROXIE
        df = df[ClassDefinition.get_roxie_to_magnum_dct().keys()]
        # Add apostrophes around comment column
        df['Comment'] = '\'' + df['Comment'] + '\''
        # Add No column (1-based)
        columns = df.columns
        df['No'] = df.index + 1
        df = df[['No'] + list(columns)]
        df = df.astype({'No': 'int32'})
        # Convert a dataframe to a bottom header table
        return RoxieAPI.convert_bottom_header_table_to_str(df, keyword=keyword)

    def get_insul_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with insulation definitions.

        :return: a dataframe table with insulation definitions.
        """
        insulation_definitions = self._get_insulation_definitions_as_list_of_dict()
        return pd.DataFrame(insulation_definitions)

    def get_remfit_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with remfit definitions.

        :return: a dataframe table with remfit definitions.
        """
        remfit_definitions = self._get_remfit_definitions_as_list_of_dict()
        return pd.DataFrame(remfit_definitions)

    def get_filament_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with filament definitions.

        :return: a dataframe table with filament definitions.
        """
        filament_definitions = self._get_filament_definitions_as_list_of_dict()
        return pd.DataFrame(filament_definitions)

    def get_strand_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with strand definitions.

        :return: a dataframe table with strand definitions.
        """
        strand_definitions = self._get_strand_definitions_as_list_of_dict()
        return pd.DataFrame(strand_definitions)

    def get_transient_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with transient definitions.

        :return: a dataframe table with transient definitions.
        """
        transient_definitions = self._get_transient_definitions_as_list_of_dict()
        return pd.DataFrame(transient_definitions)

    def get_quench_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with quench definitions.

        :return: a dataframe table with quench definitions.
        """
        quench_definitions = self._get_quench_definitions_as_list_of_dict()
        return pd.DataFrame(quench_definitions)

    def get_cable_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with cable definitions.

        :return: a dataframe table with cable definitions.
        """
        cable_definitions = self._get_cable_definitions_as_list_of_dict()
        return pd.DataFrame(cable_definitions)

    def get_conductor_df(self) -> pd.DataFrame:
        """ Method returning a dataframe table with conductor definitions.

        :return: a dataframe table with conductor definitions.
        """
        conductor_definitions = self._get_conductor_definitions_as_list_of_dict()
        return pd.DataFrame(conductor_definitions)


def _find_matching_definition(defs: List[T], name_def: str, desc_def: str) -> T:
    """ Function finding a definition with a matching name in a list of input definitions. If there is a match, then
    the definition is returned, otherwise a KeyError is thrown.

    :param defs: list of input definitions over which a search is performed.
    :param name_def: name of a definition to find.
    :param desc_def: name of a key storing the definition name.
    :return: If there is a match, then the definition is returned, otherwise a KeyError is thrown.
    """
    matches = list(filter(lambda x: x.name == name_def, defs))

    if matches:
        return matches[0]
    else:
        raise KeyError('%s name %s not present in %s definitions.' % (desc_def.capitalize(), name_def, desc_def))
