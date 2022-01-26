##
#
# File:    EditorConfig.py
# Author:  R. Sala
# Date:    03-Sep-2015
# Version: 0.001
# Updates:
#
# 2016-03-02    RPS: added EditorConfig.itemsAllowingUnicodeAccommodation list
# 2016-09-08    RPS: added "pdbx_nmr_software.ordinal" to autoIncrDecrList
# 2016-09-13    RPS: migrating config for "arrReadOnlyCtgries" and "arrCanDeleteLastRowCtgries" here from front end files for consistency.
#                    Added "em_vitrification" to "arrCanDeleteLastRowCtgries"
# 2016-09-22    RPS: added 'pdbx_SG_project' to "arrCanDeleteLastRowCtgries"
# 2016-10-25    EP:  added 'entity_src_nat', 'struct_ncs_dom', 'pdbx_nmr_refine'  to "arrAllowLastRowCDeletetgries"
#                    added to "itemsAllowingCifNullOption"
# 2016-11-30    EP:  Allow deletion of last row for "em_entity_assembly_molwt"
#                    and "em_single_particle_entity". Purge empty "em_sample_support"
# 2017-05-22    EP:  Add itemsAllowingOverrideRegex to list items in which a regular expression will give a
#                    warning but still allow for acceptance
# 2017-10-26    EP:  Treat em_author_list ordinal properly.
# 2018-07-10    EP:  Configure pdbx_serial_crystal categories to autopurge and delete last
##
"""
Contains settings pertinent to configuring the behaviour of the CIF Editor
"""
__docformat__ = "restructuredtext en"
__author__ = "Raul Sala"
__email__ = "rsala@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


class EditorConfig(object):

    # list of category.items for which ordinal value should be incremented/decremented automatically when adding/inserting or deleting a row
    autoIncrDecrList = [
        "audit_author.pdbx_ordinal",
        "citation_author.ordinal",
        "em_author_list.ordinal",
        "entity.id",
        "entity_poly.entity_id",
        "pdbx_audit_support.ordinal",
        "pdbx_nmr_software.ordinal",
        "pdbx_refine_tls_group.id",
        "pdbx_related_exp_data_set.ordinal",
        "reflns_shell.pdbx_ordinal",
        "software.pdbx_ordinal",
    ]

    # generating dictionary version of above autoIncrDecrList list where key is category name and value is item name
    autoIncrDecrDict = {}
    for cifitem in autoIncrDecrList:
        autoIncrDecrDict[cifitem.split(".")[0]] = cifitem.split(".")[1]

    # list of category.items for which auto increment/decrement behavior is NOT wanted
    autoIncrExclList = [
        "atom_sites.entry_id",
        "chem_comp.id",
        "citation.id",
        "citation_author.citation_id",
        "database_2.database_id",
        "entity_src_gen.pdbx_src_id",
        "entity_src_nat.pdbx_src_id",
        "pdbx_database_PDB_obs_spr.pdb_id",
        "pdbx_database_PDB_obs_spr.replace_pdb_id",
        "pdbx_database_proc.entry_id",
        "pdbx_database_related.db_id",
        "pdbx_entity_src_syn.pdbx_src_id",
        "pdbx_struct_sheet_hbond.sheet_id",
        "refine.pdbx_refine_id",
        "refine_ls_restr.pdbx_refine_id",
        "refine_ls_shell.pdbx_refine_id",
        "struct_asym.id",
        "struct_conf.id",
        "struct_conf_type.id",
        "struct_conn.id",
        "struct_conn_type.id",
        "struct_sheet.id",
        "struct_sheet_order.sheet_id",
        "struct_sheet_range.sheet_id",
    ]

    # list of categories for which rows in which all items have non-meaningful/null values are purged on exit from the Editor session
    purgeSkeletonRowList = [
        "database_PDB_caveat",
        "diffrn_radiation_wavelength",
        "em_sample_support",
        "em_focused_ion_beam",
        "entity_src_gen",
        "entity_src_nat",
        "pdbx_database_proc",
        "pdbx_database_related",
        "pdbx_distant_solvent_atoms",
        "pdbx_entity_src_syn",
        "pdbx_refine_tls_group",
        "pdbx_related_exp_data_set",
        "pdbx_struct_assembly_auth_evidence",
        "pdbx_struct_assembly_prop",
        "pdbx_serial_crystallography_measurement",
        "pdbx_serial_crystallography_sample_delivery",
        "pdbx_serial_crystallography_sample_delivery_injection",
        "pdbx_serial_crystallography_sample_delivery_fixed_target",
        "pdbx_serial_crystallography_data_reduction",
        "refine_ls_restr_ncs",
        "refine_ls_shell",
        "reflns_shell",
        "struct_biol",
        "struct_conn",
        "struct_mon_prot_cis",
        "struct_ncs_dom",
        "struct_ncs_dom_lim",
        "struct_ref_seq_dif",
        "pdbx_audit_support",
        "pdbx_reference_entity_sequence",
        "pdbx_reference_entity_poly",
    ]

    # list of categories for which we allow submitted values to take form of comma separated list
    itemsInCsvListForm = ["diffrn_source.pdbx_wavelength_list"]

    # dictionary defining which category.items serve as default sort column for given category when viewed in Editor
    sortColDict = {
        "audit_author": "pdbx_ordinal",
        "citation_author": "ordinal",
        "em_author_list": "ordinal",
        "entity": "id",
        "entity_poly": "entity_id",
        "pdbx_refine_tls_group": "id",
        "struct_ncs_ens": "id",
    }

    # list of category.items for which the user is allowed to supply a cif null (i.e. '?')
    itemsAllowingCifNullOption = [
        "pdbx_database_status.methods_development_category",
        "pdbx_nmr_exptl_sample_conditions.pressure_units",
        "refine.pdbx_method_to_determine_struct",
        "struct_conn.pdbx_value_order",
        "em_imaging_optics.phase_plate",
    ]

    bAccommodatingUnicode = False  # are we handling incoming non-ascii unicode inputs by converting to XML char references when persisting to CIF file

    # list of category.items for which we will convert unicode characters to ascii safe counterparts
    itemsAllowingUnicodeAccommodation = ["audit_author.name", "em_author_list.author", "citation.title", "citation_author.name", "struct.title"]

    # list of categories which will be treated as READ ONLY in the UI
    arrReadOnlyCtgries = [
        "pdbx_chem_comp_depositor_info",
        "pdbx_chem_comp_instance_depositor_info",
        "pdbx_chem_comp_upload_depositor_info",
        "pdbx_entity_src_gen_depositor_info",
        "pdbx_helical_symmetry_depositor_info",
        "pdbx_point_symmetry_depositor_info",
        "pdbx_struct_assembly_gen_depositor_info",
        "pdbx_struct_assembly_prop_depositor_info",
        "pdbx_struct_oper_list_depositor_info",
        "pdbx_struct_ref_seq_depositor_info",
        "pdbx_struct_ref_seq_dif_depositor_info",
        "struct_ref",
        "struct_ref_seq",
    ]

    # list of categories for which deletion of last remaining row will be allowed in the UI
    arrAllowLastRowDeleteCtgries = [
        "em_db_reference",
        "em_entity_assembly_molwt",
        "em_single_particle_entity",
        "em_vitrification",
        "entity_src_nat",
        "pdbx_database_related",
        "pdbx_SG_project",
        "pdbx_nmr_refine",
        "refine_ls_shell",
        "struct_conn",
        "struct_ncs_dom",
        "pdbx_related_exp_data_set",
        "pdbx_serial_crystallography_measurement",
        "pdbx_serial_crystallography_sample_delivery",
        "pdbx_serial_crystallography_sample_delivery_injection",
        "pdbx_serial_crystallography_sample_delivery_fixed_target",
        "pdbx_serial_crystallography_data_reduction",
        "pdbx_audit_support",
    ]

    # list of items that use a regular expression - for which biocurator could override..
    itemsAllowingOverrideRegex = ["audit_author.name", "citation_author.name"]
