'''Wrapper for importing CSV and Text files into MySQL and Postgress.

Only the MySQL implementation is working.  The MSSQL ODBC implementation
is giving me a lot of shit with the connection and I gave up for now to
get it working.
'''

import os
import datetime
import logging
import sys
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import platform
from pathlib import Path
import pyodbc
import beetools
import csvwrpr
import displayfx
import fixdate

_PROJ_DESC = __doc__.split('\n')[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem


class SQLDbWrpr:
    '''This module creates a wrapper for the MySql database.'''

    def __init__(
        self,
        p_parent_logger_name=None,
        p_host_name='localhost',
        p_user_name='',
        p_password='',
        p_recreate_db=False,
        p_db_name='',
        p_db_structure={},
        p_batch_size=10000,
        p_bar_len=50,
        p_msg_width=50,
        p_verbose=False,
    ):
        '''Create database with supplied structure and return a connector to the database

        Parameters
        - p_parent_logger_name - Name of parent logger
        - p_host_name = Host to connect to
        - p_user_name = User name for connection
        - p_password = paswword of user
        - ReCreate = Recresate the database or connecto to existing database
        - db_name =
        - table_details: Details of the tables to be created
        - batch_size:    Bulk data will be managed by batch_size to commit
        - p_bar_len:     Length for the progress bar
        - p_msg_width:   Width of message before progress bar
        '''
        self.logger_name = '{}.{}'.format(p_parent_logger_name, _PROJ_NAME)
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info('Start')
        # self.ver = _PROJ_VERSION
        self.success = False
        self.bar_len = p_bar_len
        self.batch_size = p_batch_size
        self.char_fields = {}
        self.conn = None
        self.cur = None
        self.db_name = p_db_name
        self.db_structure = p_db_structure
        self.delimiter = ','
        self.fkey_ref_act = {
            'C': 'CASCADE',
            'R': 'RESTRICT',
            'D': 'SET DEFAULT',
            'N': 'SET NULL',
        }
        self.host_PROJ_NAME = p_host_name
        self.idx_type = {'U': 'UNIQUE', 'F': 'FULLTEXT', 'S': 'SPATIAL'}
        self.msg_width = p_msg_width
        self.non_char_fields = {}
        self._password = p_password
        self.re_create_db = p_recreate_db
        self.silent = p_verbose
        self.sort_order = {'A': 'ASC', 'D': 'DESC'}
        self.table_load_order = []
        self.user_PROJ_NAME = p_user_name
        self.get_db_field_types()

    # end __int__

    def close(self):
        '''Close the connention'''
        if self.conn:
            self.conn.close()

    # end close

    def create_db(self):
        '''Create the database according to self.db_structure.'''
        self.cur.execute("SHOW DATABASES")
        db_res = [x[0].lower() for x in self.cur.fetchall()]
        if self.db_name.lower() in db_res:
            try:
                self.cur.execute('DROP DATABASE {}'.format(self.db_name))
                self.conn.commit()
            except mysql.connector.Error as err:
                self._print_err_msg(err, 'Could not drop the database')
                self.close()
                sys.exit()
        try:
            self.cur.execute(
                'CREATE DATABASE {} DEFAULT CHARACTER SET "utf8"'.format(self.db_name)
            )
            self.conn.commit()
            self.cur.execute('USE {}'.format(self.db_name))
            self.conn.commit()
        except mysql.connector.Error as err:
            self._print_err_msg(err, 'Could not create the database')
            self.close()
            sys.exit()
        return True

    # end create_db

    def create_tables(self):
        '''Create db tables from MySQL.table_details dict'''

        def build_db(p_db_sql_str_set):
            '''Description'''
            for sql_set in p_db_sql_str_set:
                try:
                    self.cur.execute(sql_set[1])
                    print('Created table = {}'.format(sql_set[0]))
                except mysql.connector.Error as err:
                    print(
                        'Failed creating table = {}: {}\nForced termination of program'.format(
                            sql_set[0], err
                        )
                    )
                    print('{}'.format(sql_set[1]))
                    sys.exit()
            pass

        # end build_db

        def generate_db_sql(
            p_table_set_up_str,
            p_primary_key_str,
            p_idx_set_up_list,
            p_constraint_set_up_list,
        ):
            '''Description'''
            table_set_up_str = p_table_set_up_str
            table_set_up_str += p_primary_key_str
            for idx_str in p_idx_set_up_list:
                table_set_up_str += idx_str
            for constraint_str in p_constraint_set_up_list:
                table_set_up_str += constraint_str[2]
            table_set_up_str = '{})'.format(table_set_up_str[:-2])
            return table_set_up_str

        # end generate_db_sql

        def build_constraints(p_table_PROJ_NAME):
            '''Description'''
            constraint_list = []
            fkey_nr_list = []
            for field_PROJ_NAME in self.db_structure[p_table_PROJ_NAME]:
                fkey = get_foreign_key(p_table_PROJ_NAME, field_PROJ_NAME)
                if fkey['Present']:
                    fkey_nr_list.append(fkey['ForeignKeyNr'])
                    # fkey_PROJ_NAME = 'fk_{}_{}'.format( fkey[ 'FKeyTable' ], fkey[ 'RefTable' ])
                    fkey_str = 'CONSTRAINT fk_{}_{} FOREIGN KEY ({}) REFERENCES {} ({}) ON DELETE {} ON UPDATE {}, '.format(
                        fkey['FKeyTable'],
                        fkey['RefTable'],
                        '.'.join(fkey['FKeyFlds']),
                        fkey['RefTable'],
                        '.'.join(fkey['RefFields']),
                        self.fkey_ref_act[fkey['OnDelete']],
                        self.fkey_ref_act[fkey['OnUpdate']],
                    )
                    constraint_list.append(
                        [fkey['FKeyTable'], fkey['RefTable'], fkey_str]
                    )
                    pass
            return constraint_list

        # def build_constraints

        def build_all_indexes(p_table_PROJ_NAME):
            '''Description'''

            def build_primary_key_idx(p_table_PROJ_NAME):
                '''Description'''
                idx_PROJ_NAME_list = []
                idx_str_list = []
                pkey = get_primary_key(p_table_PROJ_NAME)
                idx_PROJ_NAME = '{}_UNIQUE'.format('_'.join(pkey['Flds']))
                idx_PROJ_NAME_list.append(idx_PROJ_NAME)
                idx_str = 'UNIQUE INDEX pk_{} ({}) VISIBLE, '.format(
                    idx_PROJ_NAME, ','.join(pkey['Flds'])
                )
                idx_str_list.append(idx_str)
                return idx_str_list, idx_PROJ_NAME_list

            # end build_primary_key_idx

            def build_unique_key_idx(
                p_table_PROJ_NAME, p_dx_PROJ_NAME_list, p_idx_str_list
            ):
                '''Description'''
                idx_list = {}
                idx_PROJ_NAME_list = p_dx_PROJ_NAME_list
                idx_str_list = p_idx_str_list
                for field_PROJ_NAME in self.db_structure[p_table_PROJ_NAME]:
                    field_param_st_ref = self.db_structure[p_table_PROJ_NAME][
                        field_PROJ_NAME
                    ]['Params']
                    if field_param_st_ref['Index']:
                        if field_param_st_ref['Index'][0] not in idx_list:
                            idx_list[field_param_st_ref['Index'][0]] = [
                                [field_PROJ_NAME] + field_param_st_ref['Index'][1:]
                            ]
                        else:
                            idx_list[field_param_st_ref['Index'][0]].append(
                                [field_PROJ_NAME] + field_param_st_ref['Index'][1:]
                            )
                for idx_instance in idx_list:
                    idx_instance_order = sorted(
                        idx_list[idx_instance], key=lambda x: x[1]
                    )
                    idx_PROJ_NAME = ''
                    for field_det in idx_instance_order:
                        idx_PROJ_NAME += '{}_'.format(field_det[0])
                    if field_det[3] == 'U':
                        idx_PROJ_NAME = 'unq_{}'.format(idx_PROJ_NAME[:-1])
                    else:
                        idx_PROJ_NAME = 'idx_{}'.format(idx_PROJ_NAME[:-1])
                    if idx_PROJ_NAME not in idx_PROJ_NAME_list:
                        idx_PROJ_NAME_list.append(idx_PROJ_NAME)
                        if field_det[3] == 'U':
                            idx_str = '{} INDEX {} ('.format(
                                self.idx_type[field_det[3]], idx_PROJ_NAME
                            )
                        else:
                            idx_str = 'INDEX {} ('.format(idx_PROJ_NAME)
                        for field_det in idx_instance_order:
                            idx_str += '{} {}, '.format(
                                field_det[0], self.sort_order[field_det[2]]
                            )
                        idx_str = idx_str[:-2] + ') VISIBLE, '
                        idx_str_list.append(idx_str)
                return idx_str_list, idx_PROJ_NAME_list

            # end build_unique_key_idx

            idx_PROJ_NAME_list = []
            idx_list = []
            idx_list, idx_PROJ_NAME_list = build_unique_key_idx(
                p_table_PROJ_NAME, idx_PROJ_NAME_list, idx_list
            )
            return idx_list

        # def build_all_indexes

        def build_primary_key_sql_str(p_table_PROJ_NAME):
            '''Description'''
            primary_key_det = get_primary_key(p_table_PROJ_NAME)
            sql_str = 'PRIMARY KEY ({}), '.format(','.join(primary_key_det['Flds']))
            return sql_str

        # def build_primary_key_sql_str

        def build_table_sql_str(p_table_PROJ_NAME):
            '''Description'''
            sql_str = 'CREATE TABLE {} ('.format(p_table_PROJ_NAME)
            for field_PROJ_NAME in self.db_structure[p_table_PROJ_NAME]:
                field_type_st_ref = self.db_structure[p_table_PROJ_NAME][
                    field_PROJ_NAME
                ]['Type']
                field_param_st_ref = self.db_structure[p_table_PROJ_NAME][
                    field_PROJ_NAME
                ]['Params']
                field_comment_st_ref = self.db_structure[p_table_PROJ_NAME][
                    field_PROJ_NAME
                ]['Comment']
                sql_str += '{} {}'.format(field_PROJ_NAME, field_type_st_ref[0])
                if field_type_st_ref[0] == 'varchar' or field_type_st_ref[0] == 'char':
                    sql_str += ' ({})'.format(str(field_type_st_ref[1]))
                elif field_type_st_ref[0] == 'decimal':
                    sql_str += '({}, {})'.format(
                        str(field_type_st_ref[1]), str(field_type_st_ref[2])
                    )
                if field_param_st_ref['AI'] == 'Y':
                    sql_str += ' AUTO_INCREMENT'
                if field_param_st_ref['UN'] == 'Y' and field_param_st_ref['AI'] != 'Y':
                    sql_str += ' UNSIGNED'
                if field_param_st_ref['NN'] == 'Y':
                    sql_str += ' NOT NULL'
                if field_param_st_ref['ZF'] == 'Y':
                    sql_str += ' ZEROFILL'
                if field_param_st_ref['DEF']:
                    if (
                        field_type_st_ref[0] == 'varchar'
                        or field_type_st_ref[0] == 'char'
                    ):
                        sql_str += ' DEFAULT "{}"'.format(field_param_st_ref['DEF'])
                    else:
                        sql_str += ' DEFAULT {}'.format(field_param_st_ref['DEF'])
                if field_comment_st_ref:
                    sql_str += ' COMMENT "{}"'.format(field_comment_st_ref)
                sql_str += ', '
            return sql_str

        # end build_table_sql_str

        def get_foreign_key(p_table_PROJ_NAME, p_field_PROJ_NAME):
            '''Description'''
            fkey = {
                'Present': False,
                'FKeyFlds': [],
                'RefFields': [],
                'FKeyTable': '',
                'RefTable': '',
                'ForeignKeyNr': False,
                'OnDelete': 'N',
                'OnUpdate': 'N',
            }
            fkey_source = self.db_structure[p_table_PROJ_NAME][p_field_PROJ_NAME][
                'Params'
            ]['FKey']
            if fkey_source:
                table_det = self.db_structure[p_table_PROJ_NAME]
                fkey['ForeignKeyNr'] = fkey_source[0]
                fkey['FKeyTable'] = p_table_PROJ_NAME
                fkey['RefTable'] = fkey_source[2]
                ref_field_pair_list = []
                for field in table_det:
                    if table_det[field]['Params']['FKey']:
                        if (
                            table_det[field]['Params']['FKey'][0]
                            == fkey['ForeignKeyNr']
                        ):
                            ref_field_pair_list.append(
                                [
                                    field,
                                    table_det[field]['Params']['FKey'][3],
                                    table_det[field]['Params']['FKey'][1],
                                ]
                            )
                ref_field_pair_list = sorted(ref_field_pair_list, key=lambda x: x[2])
                fkey['FKeyFlds'], fkey['RefFields'], t_order = zip(*ref_field_pair_list)
                fkey['OnDelete'] = fkey_source[4]
                fkey['OnUpdate'] = fkey_source[5]
                fkey['Present'] = True
            return fkey

        # end get_foreign_key

        def get_primary_key(p_table_PROJ_NAME):
            '''Description'''
            pkey = {'Present': False, 'Flds': (), 'SortPairList': [], 'SortPairStr': []}
            for field_PROJ_NAME in self.db_structure[p_table_PROJ_NAME]:
                pkey_field_det = self.db_structure[p_table_PROJ_NAME][field_PROJ_NAME]
                if pkey_field_det['Params']['PrimaryKey'][0] == 'Y':
                    pkey['Flds'] += (field_PROJ_NAME,)
                    pkey['SortPairList'].append(
                        (
                            field_PROJ_NAME,
                            self.sort_order[pkey_field_det['Params']['PrimaryKey'][1]],
                        )
                    )
                    pkey['SortPairStr'].append(
                        (
                            '{} {}'.format(
                                field_PROJ_NAME,
                                self.sort_order[
                                    pkey_field_det['Params']['PrimaryKey'][1]
                                ],
                            )
                        )
                    )
                    pkey['Present'] = True
            return pkey

        # end get_primary_key

        def order_table_build_list(p_db_sql_str_set, p_constraint_set_up_list):
            '''Description'''
            db_sql_str_set = p_db_sql_str_set
            ordered = False
            while not ordered:
                ordered = True
                for constraint in p_constraint_set_up_list:
                    fkey_pos_found = False
                    i = 0
                    fkey_pos = -1
                    while not fkey_pos_found:
                        if db_sql_str_set[i][0] == constraint[1]:
                            fkey_pos_found = True
                            fkey_pos = i
                        else:
                            i += 1
                    table_pos_found = False
                    i = 0
                    tbl_pos = -1
                    while not table_pos_found:
                        if db_sql_str_set[i][0] == constraint[0]:
                            table_pos_found = True
                            tbl_pos = i
                        else:
                            i += 1
                    if tbl_pos < fkey_pos:
                        db_sql_str_set.insert(fkey_pos + 1, db_sql_str_set[tbl_pos])
                        del db_sql_str_set[tbl_pos]
                        ordered = False
            self.table_load_order = [x[0] for x in db_sql_str_set]
            return db_sql_str_set

        # end order_table_build_list

        def structure_validation():
            '''Description'''

            def check_pkey_fkey_overlap(p_remove_fkey_pkey__overlap=True):
                '''Description'''

                def partial_overlap(p_fkey, p_pkey):
                    '''Description'''
                    is_overlap = False
                    for field_PROJ_NAME in p_fkey['FKeyFlds']:
                        if field_PROJ_NAME in p_pkey['Flds']:
                            is_overlap = True
                    return is_overlap

                # end partial_overlap

                def remove_fkey(p_fkey):
                    '''Description'''
                    for field_PROJ_NAME in self.db_structure[p_fkey['FKeyTable']]:
                        if self.db_structure[p_fkey['FKeyTable']][field_PROJ_NAME][
                            'Params'
                        ]['FKey']:
                            if (
                                self.db_structure[p_fkey['FKeyTable']][field_PROJ_NAME][
                                    'Params'
                                ]['FKey'][0]
                                == p_fkey['ForeignKeyNr']
                            ):
                                self.db_structure[p_fkey['FKeyTable']][field_PROJ_NAME][
                                    'Params'
                                ]['FKey'] = []
                    pass

                # end remove_fkey

                for table_PROJ_NAME in self.db_structure:
                    pkey = get_primary_key(table_PROJ_NAME)
                    source_table = self.db_structure[table_PROJ_NAME]
                    for field_PROJ_NAME in source_table:
                        fkey = get_foreign_key(table_PROJ_NAME, field_PROJ_NAME)
                        if fkey['Present']:
                            if pkey['Flds'] != fkey['FKeyFlds'] and partial_overlap(
                                fkey, pkey
                            ):
                                log_str = 'The foreign key {}.{} and the primary key in {}.{} overlaps.'.format(
                                    fkey['FKeyTable'],
                                    fkey['FKeyFlds'],
                                    table_PROJ_NAME,
                                    pkey['Flds'],
                                )
                                self.logger.warning(log_str)
                                if p_remove_fkey_pkey__overlap:
                                    remove_fkey(fkey)
                                    log_str = 'Current settings forced removed the foreign key "{}.{}"'.format(
                                        fkey['FKeyTable'], fkey['FKeyFlds']
                                    )
                                    self.logger.warning(log_str)
                                else:
                                    log_str = 'This may cause a problem adding record to either {} or {}'.format(
                                        fkey['FKeyTable'], table_PROJ_NAME
                                    )
                                    self.logger.warning(log_str)
                        pass
                    pass

            # end check_pkey_ukey_overlap
            check_pkey_fkey_overlap()
            pass

        # end structure_validation()

        success = True
        structure_validation()
        table_set_up_list = ''
        idx_set_up_list = []
        constraint_set_up_list = []
        db_sql_str_set = []
        for table_PROJ_NAME in self.db_structure:
            table_set_up_list = build_table_sql_str(table_PROJ_NAME)
            primary_key_str = build_primary_key_sql_str(table_PROJ_NAME)
            idx_set_up_list = build_all_indexes(table_PROJ_NAME)
            tblconstraint_list = build_constraints(table_PROJ_NAME)
            db_sql_str_set.append(
                [
                    table_PROJ_NAME,
                    generate_db_sql(
                        table_set_up_list,
                        primary_key_str,
                        idx_set_up_list,
                        tblconstraint_list,
                    ),
                ]
            )
            if tblconstraint_list:
                constraint_set_up_list += tblconstraint_list
            pass
        db_sql_str_set = order_table_build_list(db_sql_str_set, constraint_set_up_list)
        build_db(db_sql_str_set)
        return success

    # end create_tables

    def create_users(self, p_admin_user, p_new_users):
        c_user_PROJ_NAME = 0
        self.cur.execute("SELECT User, Host FROM mysql.user".format())
        curr_users = self.cur.fetchall()
        for user in p_new_users:
            if not user[c_user_PROJ_NAME] in curr_users:
                try:
                    self.cur.execute(
                        "CREATE USER IF NOT EXISTS '{}'@'{}' IDENTIFIED BY '{}'".format(
                            user[0], self.host_PROJ_NAME, user[1]
                        )
                    )
                except mysql.connector.Error as err:
                    self._print_err_msg(err, 'Could not create user')
                    self.close()
                    sys.exit()
            self.conn.commit()
        self.success = True

    # end create_users

    def delete_users(self, p_admin_user, p_del_users):
        c_user_PROJ_NAME = 0
        # c_password = 1
        c_host = 2
        self.cur.execute("SELECT User FROM mysql.user")
        curr_users = [x[0] for x in self.cur.fetchall()]
        for user in p_del_users:
            if user[c_user_PROJ_NAME] in curr_users:
                try:
                    self.cur.execute(
                        "DROP USER '{}'@'{}'".format(
                            user[c_user_PROJ_NAME], user[c_host]
                        )
                    )
                except mysql.connector.Error as err:
                    self._print_err_msg(err, 'Could not delete user')
                    self.close()
                    sys.exit()
        self.success = True

    # end delete_users

    def _err_broken_rec(self, p_sql_str, p_csv_db_slice):
        '''Write broken record to logger'''
        # self.logger.critical( p_err )
        for row in p_csv_db_slice:
            try:
                self.cur.execute(p_sql_str, row)
            except Exception:
                self.logger.warning(
                    '{}\n{}\nForced program termination'.format(p_sql_str, row)
                )
                sys.exit()
            else:
                self.conn.commit()
            pass
        pass

    # end _err_broken_rec( err )

    def export_to_csv(
        self,
        p_csv_path,
        p_table_PROJ_NAME,
        p_delimeter='|',
        p_strip_chars='',
        p__vol_size=0,
        p_sql_query='',
    ):
        '''Export a table to a csv file

        Parameters
        - p_csv_path          - Path name of the file to be exported
        - p_table_PROJ_NAME = ''   - Table name to export
        - p_delimeter = '|'  - Field delimiter to use
        - p_strip_chars = ''  - characters to strip from text
        - p__vol_size = 0      - Create a multiple volume export. p__vol_size is
                             the number of records per file.  0 wil create
                             only one volume.
        '''

        def multi_volume_export(p_csv_path, p__vol_size):
            '''Create multiple volumes in path with p__vol_size records

            Parameters
            - p_csv_path          - Path name of the file to be exported
            - p__vol_size = 0      - Create a multiple volume export. p__vol_size is
                                 the number of records per file.  0 wil create
                                 only one volume.
            '''
            file_PROJ_NAME_list = []
            header = p_delimeter.join(self.db_structure[p_table_PROJ_NAME])
            prim_key_sql_str = 'SELECT '
            all_sql_str = (
                'SELECT '
                + header.replace(p_delimeter, ',')
                + ' FROM '
                + p_table_PROJ_NAME
                + ' WHERE '
            )
            for i, field in enumerate(self.db_structure[p_table_PROJ_NAME]):
                if (
                    self.db_structure[p_table_PROJ_NAME][field]['Params']['PrimaryKey'][
                        0
                    ]
                    == 'Y'
                ):
                    prim_key_sql_str += field + ', '
                    all_sql_str += field + ' = %s and '
            prim_key_sql_str = prim_key_sql_str[:-2] + ' FROM ' + p_table_PROJ_NAME
            all_sql_str = all_sql_str[:-5]
            print('Collecting {} table records'.format(p_table_PROJ_NAME))
            self.cur.execute(prim_key_sql_str)
            prim_key_res = self.cur.fetchall()
            vol_cntr = 1
            # curr_vol_size = p__vol_size
            list_len = len(prim_key_res)
            msg = beetools.msg_display(
                'Export records table = {} ({})'.format(p_table_PROJ_NAME, list_len),
                p_len=self.msg_width,
            )
            rec_cntr = 0
            pfx = displayfx.DisplayFx(
                _PROJ_NAME, list_len, p_msg=msg, p_bar_len=self.bar_len
            )
            csv_file = None
            for i, pkeys_rec in enumerate(prim_key_res):
                if rec_cntr == 0:
                    if rec_cntr == 0 and vol_cntr > 1:
                        csv_file.close()
                        # if list_len - ((vol_cntr - 1) * p__vol_size) < p__vol_size:
                        # curr_vol_size = list_len - ((vol_cntr - 1) * p__vol_size)
                    if vol_cntr == 1:
                        csv_vol_path = p_csv_path
                    else:
                        csv_vol_path = (
                            p_csv_path[:-4]
                            + '{:0>2}'.format(vol_cntr)
                            + p_csv_path[-4:]
                        )
                    file_PROJ_NAME_list.append(os.path.split(csv_vol_path))
                    csv_file = open(csv_vol_path, 'w+')
                    csv_file.write(header + '\n')
                self.cur.execute(all_sql_str, pkeys_rec)
                row_res = self.cur.fetchall()[0]
                csv_row = ''
                for j, field in enumerate(row_res):
                    if field is None:
                        field = 'NULL'
                    if j in self.char_fields[p_table_PROJ_NAME]:
                        csv_row += '"' + str(field) + '"' + p_delimeter
                    else:
                        csv_row += str(field) + p_delimeter
                for char in p_strip_chars:
                    csv_row.replace(char, '')
                csv_file.write(csv_row[:-1] + '\n')
                if rec_cntr == p__vol_size:
                    rec_cntr = 0
                    vol_cntr += 1
                else:
                    rec_cntr += 1
                pfx.update(i)
            csv_file.close()
            return file_PROJ_NAME_list

        # end multi_volume_export

        def single_volume_export(p_csv_path, p_sql_query):
            '''Create single volume in path with p__vol_size records

            Parameters
            - p_csv_path          - Path name of the file to be exported
            '''
            header = ''
            file_PROJ_NAME_list = []
            file_PROJ_NAME_list.append(os.path.split(p_csv_path))
            if not p_sql_query:
                header = p_delimeter.join(self.db_structure[p_table_PROJ_NAME])
                sql_str = (
                    'SELECT '
                    + header.replace(p_delimeter, ',')
                    + ' FROM '
                    + p_table_PROJ_NAME
                )
            else:
                header = p_delimeter.join(p_sql_query[0])
                sql_str = p_sql_query[1]
            csv_file = open(p_csv_path, 'w+')
            csv_file.write(header + '\n')
            print('Collecting {} table records'.format(p_table_PROJ_NAME))
            self.cur.execute(sql_str)
            table_res = self.cur.fetchall()
            # cntr = 0
            list_len = len(table_res)
            msg = beetools.msg_display(
                'Export records table = {} ({})'.format(p_table_PROJ_NAME, list_len),
                p_len=self.msg_width,
            )
            dfx = displayfx.DisplayFx(
                _PROJ_NAME, list_len, p_msg=msg, p_bar_len=self.bar_len
            )
            for i, row in enumerate(table_res):
                csv_row = ''
                for j, field in enumerate(row):
                    # if not field:
                    if field is None:
                        field = 'NULL'
                    if j in self.char_fields[p_table_PROJ_NAME]:
                        csv_row += '"' + str(field) + '"' + p_delimeter
                    else:
                        csv_row += str(field) + p_delimeter
                for char in p_strip_chars:
                    csv_row.replace(char, '')
                csv_file.write(csv_row[:-1] + '\n')
                dfx.update(i)
            csv_file.close()
            return file_PROJ_NAME_list

        # end single_volume_export

        try:
            self.cur.execute('SELECT COUNT(*) FROM ' + p_table_PROJ_NAME)
        except mysql.connector.Error as err:
            print('Err mesg: {}'.format(err.msg))
            print(err.msg)
        else:
            count_rec_res = self.cur.fetchall()[0][0]
            if p__vol_size > 0 and count_rec_res > p__vol_size and not p_sql_query:
                file_PROJ_NAME_list = multi_volume_export(p_csv_path, p__vol_size)
            else:
                file_PROJ_NAME_list = single_volume_export(p_csv_path, p_sql_query)
            # success = True
        return file_PROJ_NAME_list

    # end export_to_csv

    def get_db_field_types(self):
        '''Description'''
        for p_table_PROJ_NAME in self.db_structure:
            self.char_fields[p_table_PROJ_NAME] = []
            self.non_char_fields[p_table_PROJ_NAME] = []
            for field in self.db_structure[p_table_PROJ_NAME]:
                if (
                    self.db_structure[p_table_PROJ_NAME][field]['Type'][0] == 'char'
                    or self.db_structure[p_table_PROJ_NAME][field]['Type'][0]
                    == 'varchar'
                ):
                    self.char_fields[p_table_PROJ_NAME].append(field)
                else:
                    self.non_char_fields[p_table_PROJ_NAME].append(field)

    # end get_db_field_types

    def grant_rights(self, p_admin_user, p_user_rights):
        c_user_PROJ_NAME = 0
        # c_password = 1
        c_host = 1
        c_db = 2
        c_table = 3
        c_rights = 4
        # success = True
        for right in p_user_rights:
            try:
                sql_str = "GRANT {} ON {}.{} TO '{}'@'{}'".format(
                    ','.join(right[c_rights:]),
                    right[c_db],
                    right[c_table],
                    right[c_user_PROJ_NAME],
                    right[c_host],
                )
                self.cur.execute(sql_str)
                self.conn.commit()
                sql_str = "GRANT {} ON {}.{} TO '{}'@'{}' WITH GRANT OPTION".format(
                    ','.join(right[c_rights:]),
                    right[c_db],
                    right[c_table],
                    right[c_user_PROJ_NAME],
                    right[c_host],
                )
                self.cur.execute(sql_str)
                self.conn.commit()
            except mysql.connector.Error as err:
                self._print_err_msg(err)
                self.close()
                sys.exit()
        self.success = True

    # end grant_rights

    def import_csv(
        self,
        p_table_PROJ_NAME,
        p_csv_file_name='',
        p_key='',
        p_header='',
        p_del_head=False,
        p_csv_db='',
        p_csv_corr_str_file_name='',
        p_vol_type='Multi',
        p_verbose=False,
        p_replace=False,
    ):
        '''Import a csv file into a database table.

        Parameters
        - p_table_PROJ_NAME
          Table name to import the csv data into
        - p_csv_file_name = ''
          Csv file name.  Empty if structure contained in p_csv_db
        - p_key = ''
          Key used to insert in table
        - p_header = ''
          - Header of csv files
        - p_del_head = ''
          - Delete the header
        - p_csv_db = ''
          - Contains the csv table in a structure and makes p_csv_file_name obsolete.
        - p_csv_corr_str_file_name = ''
          - String that contains any strings that should be replace in the csv
            file brfore parsing
        - p_vol_type = 'Multi'
          - Multi - Read multiple volume
          - Single - Read single file
        - p_verbose = False
          - Determine if there are any output to screen
        - debug = False
          - Switch debug on
        - p_replace = False
          - False - INSERT into database
          - True - REPLACE into database
        '''

        def import_volume(p_csv_db, p_header, p_verbose):
            '''Description'''

            def convert_str_to_none(p_non_char_fields_idx, p_csv_db):
                '''Description'''
                rows_to_del = []
                csv_db = p_csv_db
                list_len = len(csv_db)
                msg = beetools.msg_display(
                    'Convert empty strings to None ({})'.format(list_len),
                    p_len=self.msg_width,
                )
                dfx = displayfx.DisplayFx(
                    _PROJ_NAME,
                    list_len,
                    p_msg=msg,
                    p_verbose=p_verbose,
                    p_bar_len=self.bar_len,
                )
                for row_idx, row in enumerate(csv_db):
                    found_none = False
                    t_tow = list(csv_db[row_idx])
                    for field in p_non_char_fields_idx:
                        if t_tow[field] == '':
                            t_tow[field] = None
                            found_none = True
                    if found_none:
                        csv_db.append(tuple(t_tow))
                        rows_to_del.append(row_idx)
                    dfx.update(row_idx)
                list_len = len(rows_to_del)
                msg = beetools.msg_display(
                    'Cleanup ({})'.format(list_len), p_len=self.msg_width
                )
                dfx = displayfx.DisplayFx(
                    _PROJ_NAME,
                    list_len,
                    p_msg=msg,
                    p_verbose=p_verbose,
                    p_bar_len=self.bar_len,
                )
                for i, row_idx in enumerate(sorted(rows_to_del, reverse=True)):
                    del csv_db[row_idx]
                    dfx.update(i)
                return csv_db

            # end convert_str_to_none

            def find_non_char_field_idx(p_csv_db):
                '''Find the indexs of the fealds to could potentially contain mepty strings.'''
                non_char_fields_idx = []
                for header_field_PROJ_NAME in self.non_char_fields[p_table_PROJ_NAME]:
                    for row_idx, data_field_PROJ_NAME in enumerate(p_csv_db[0]):
                        if header_field_PROJ_NAME == data_field_PROJ_NAME:
                            non_char_fields_idx.append(row_idx)
                            break
                return non_char_fields_idx

            # end find_non_char_field_idx

            def fix_dates(p_csv_db, p_table_PROJ_NAME, p_header):
                '''Ensure date and datetime fileds in the database is valid.'''
                c_field_idx = 0
                c_field_type = 1
                csv_db = p_csv_db
                idx = []
                # date_time_idx = []
                for i, field in enumerate(p_header):
                    if field in self.db_structure[p_table_PROJ_NAME]:
                        if (
                            self.db_structure[p_table_PROJ_NAME][field]['Type'][0]
                            == 'date'
                        ):
                            idx.append([i, 'date'])
                        elif (
                            self.db_structure[p_table_PROJ_NAME][field]['Type'][0]
                            == 'datetime'
                        ):
                            idx.append([i, 'datetime'])
                if idx:
                    for i, row in enumerate(csv_db[1:]):
                        for field_det in idx:
                            if row[field_det[c_field_idx]] is not None:
                                if field_det[c_field_type] == 'date' and not isinstance(
                                    row[field_det[c_field_idx]], datetime.date
                                ):
                                    fixed_date = fixdate.FixDate(
                                        self.logger_name,
                                        row[field_det[c_field_idx]],
                                        p_out_format='%Y/%m/%d',
                                    ).date_str
                                    if isinstance(csv_db[i + 1], tuple):
                                        csv_db[i + 1] = (
                                            csv_db[i + 1][: field_det[c_field_idx]]
                                            + (fixed_date,)
                                            + csv_db[i + 1][
                                                field_det[c_field_idx] + 1 :
                                            ]
                                        )
                                    if isinstance(csv_db[i + 1], list):
                                        csv_db[i + 1] = (
                                            csv_db[i + 1][: field_det[c_field_idx]]
                                            + [fixed_date]
                                            + csv_db[i + 1][
                                                field_det[c_field_idx] + 1 :
                                            ]
                                        )
                                    pass
                                    # elif field_det[ c_field_type ] == 'datetime' and isinstance( row[ field_det[ c_field_idx ]], datetime.datetime ):
                                    #     date, time = row[ field_det[ c_field_idx ]].split( ' ' )
                                    #     date, time = row[ field_det[ c_field_idx ]].split( ' ' )
                                    # fixed_date = fixdate.FixDate( self.logger_name, date, p_out_format = '%Y/%m/%d').date_str
                                    #     if isinstance( csv_db[ i + 1 ], tuple ):
                                    #         csv_db[ i + 1 ] = csv_db[ i + 1 ][ :field_det[ c_field_idx ]] + ( '{} {}'.format( fixed_date, time ), ) \
                                    #                                            + csv_db[ i + 1 ][ field_det[ c_field_idx ] + 1:]
                                    #     if isinstance( csv_db[ i + 1 ], list ):
                                    #         csv_db[ i + 1 ] = csv_db[ i + 1 ][ :field_det[ c_field_idx ]] + [ '{} {}'.format( fixed_date, time ) ] \
                                    #                                            + csv_db[ i + 1 ][ field_det[ c_field_idx ] + 1:]
                                    pass
                    pass
                return csv_db

            # end fix_dates

            def write_to_table(p_csv_db):
                '''Write the data to a table'''
                i = 1
                j = 0  # In case batch size is more than all records
                list_len = len(p_csv_db)
                msg = beetools.msg_display(
                    'Populate table = {} ({})'.format(p_table_PROJ_NAME, list_len),
                    p_len=self.msg_width,
                )
                dfx = displayfx.DisplayFx(
                    _PROJ_NAME,
                    list_len,
                    p_msg=msg,
                    p_verbose=p_verbose,
                    p_bar_len=self.bar_len,
                )
                # sql_str = 'REPLACE'
                if p_replace:
                    sql_str = 'REPLACE'
                else:
                    sql_str = 'INSERT'
                sql_str = '{} INTO {} ({}) VALUES ({})'.format(
                    sql_str,
                    p_table_PROJ_NAME,
                    ','.join([str(x) for x in header]),
                    ','.join(['%s' for x in range(len(header))]),
                )
                for j in range(self.batch_size, list_len, self.batch_size):
                    try:
                        self.cur.executemany(sql_str, p_csv_db[i : j + 1])
                    except Error as err:
                        self.logger.error(err)
                        self.conn.rollback()
                        self._err_broken_rec(sql_str, p_csv_db[i : j + 1])
                    finally:
                        self.conn.commit()
                        i = j + 1
                        dfx.update(j)
                # New needs to be tested. Writing the records 1 by 1?
                self.logger.debug('{}'.format(p_csv_db[j + 1 : len(p_csv_db)]))
                self.cur.executemany(sql_str, p_csv_db[j + 1 : len(p_csv_db)])
                self.conn.commit()
                if j < list_len:
                    dfx.update(list_len)
                pass

            # end write_to_table

            csv_db = p_csv_db
            if p_header:
                header = p_header
            else:
                header = csv_db[0]
            csv_db = fix_dates(csv_db, p_table_PROJ_NAME, header)
            if self.non_char_fields[p_table_PROJ_NAME]:
                csv_db = convert_str_to_none(
                    find_non_char_field_idx(p_csv_db), p_csv_db
                )
            write_to_table(csv_db)
            pass

        # end import_volume

        def import_single_volume(p_csv_db, p_header, p_verbose):
            '''Description'''
            success = False
            # if not p_csv_db:
            #     if os.path.isfile(p_csv_file_name):
            #         csv_file_data = csvwrpr.CsvWrpr(
            #             self.logger_name,
            #             p_csv_file_name=p_csv_file_name,
            #             p_key1=p_key,
            #             p_header=p_header,
            #             p_del_head=p_del_head,
            #             p_struc_type=(),
            #             p_csv_corr_str_file_name=p_csv_corr_str_file_name,
            #             p_replace_header=replace_header,
            #             p_verbose=p_verbose,
            #             p_bar_len=self.bar_len,
            #             p_msg_width=self.msg_width,
            #         )
            #         csv_db = csv_file_data.csv_db
            if p_csv_db:
                import_volume(p_csv_db, p_header, p_verbose)
                success = True
            return success

        # end import_single_volume

        def import_multi_volume(p_verbose, p_header):
            '''Description'''
            vol_cntr = 1
            success = False
            vol_csv_file_name = p_csv_file_name
            while os.path.isfile(vol_csv_file_name):
                csv_file_data = csvwrpr.CsvWrpr(
                    _PROJ_NAME,
                    vol_csv_file_name,
                    p_key1=p_key,
                    p_header=p_header,
                    p_del_head=p_del_head,
                    p_struc_type=(),
                    p_csv_corr_str_file_name=p_csv_corr_str_file_name,
                    p_replace_header=replace_header,
                    p_verbose=p_verbose,
                    p_msg_width=self.msg_width,
                    p_bar_len=self.bar_len,
                    p_match_nr_of_fields=True,
                )
                csv_db = csv_file_data.csv_db
                if csv_db:
                    import_volume(csv_db, p_header, p_verbose)
                    success = True
                vol_cntr += 1
                vol_csv_file_name = (
                    p_csv_file_name[:-4]
                    + '{:0>2}'.format(vol_cntr)
                    + p_csv_file_name[-4:]
                )
            if not success:
                log_str = 'No data to import from {}'.format(vol_csv_file_name)
                self.logger.warning(log_str)
            return success

        # end import_multi_volume

        if p_header:
            replace_header = True
        else:
            replace_header = False
        if p_vol_type == 'Single' or p_csv_db:
            success = import_single_volume(p_csv_db, p_header, p_verbose)
        elif p_vol_type == 'Multi':
            success = import_multi_volume(p_verbose, p_header)
        return success

    # end import_csv

    def import_and_split_csv(
        self,
        p_split_struct,
        p_data,
        p_header='',
        p_insert_header=False,
        p_verbose=False,
        p_debug=False,
    ):
        '''Import a csv file into a database table.

        Parameters
        - p_split_struct - { 'Seq01' : { 'TableName' : Desttable_PROJ_NAME1, 'Key' : TableKey, 'Replace' : False, 'Flds': [[ OrgField1, DestField1, [ Command, Parm1, Parm2, Parm3 ]],
                                                                                                                      [ OrgField2, DestField2, [ Command, Parm1, Parm2, Parm3 ]],
                                                                                                                      [ ...                                             ]]},
                            'Seq02' : { 'TableName' : Desttable_PROJ_NAME2, 'Key' : TableKey, 'Replace' : False, 'Flds': [[ OrgField1, DestField1, [ Command, Parm1, Parm2, Parm3 ]],
                                                                                                                      [ OrgField2, DestField3, [ Command, Parm1, Parm2, Parm3 ]],
                                                                                                                      [ ...                                             ]]},
                          ...                                                                                                                        }
          - SeqNN:               Any iterate sequence to indicate the various tables the csv file should be split into ( seq01, seq02, seq03, ...)
          - table_PROJ_NAME (str):     Mandatory key word (in the python dict structure) to indicate the table name in the database
          - Desttable_PROJ_NAME (str): The name of the table in the database to populate
          - Key (str):           Mandatory key word (in the python dict structure) to indicate the primary key field of the table
          - TableKey (str):      Destination table primary key
          - Replace (boolean):   Either use REPLACE or INSERT SQL statement to add records to the table.  INSERT will cause
                                 a failure when the record to be added is a duplicate.
          - Fields (str):        Mandatory key word (in the python dict structure) to list the fields in the table
          - OrgFieldN (str):     Field name from the csv file top copy to the database table
          - DestFieldN (str):    Destination filed where OrgFieldN will be copied into
          - Command (int):       0 = Copy OrgFieldN to DestFieldN as is
                                     Parm1 = Truncate OrgFieldN at Parm1 if it is a string and insert into DestFieldN.  0 for no truncation.  Non 'str' will not be truncated
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                     Parm3 = Insert a default value if the original field matched the list.
                                           = [ list, Def ]
                                 1 = Insert fixed value into DestFieldN
                                     Parm1 = The fixed value to insert into DestFieldN
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                 2 = Split OrgFieldN by ',' and insert the n'th occurrence defined in Parm1 into DestFieldN
                                     Parm1 = The n'th occurrence from split of OrgFieldN to insert into DestFieldN
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                 3 = Combine the "year" value in OrgFieldN with "01/01" and insert into DestFieldN
                                     Parm1 = Date
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                 4 = Value of OrgFieldN will be looked up in a dict and inserted into DestFieldN
                                     Parm1 = Lookup table in form of dict
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                 5 = Copy sub string from OrgFieldN into DestFieldN
                                     Parm1 = List with start and end value to copy from OrgFieldN
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
                                 6 = Insert auto number into DestFieldN
                                     Parm1 = Start with the value and add 1 with each iteration
                                     Parm2 = True if you do not want to add the row if the result is empty, else False
        - p_data
        - p_header = ''
        '''
        if isinstance(p_data, list):
            csv_file_data = p_data.copy()
        elif isinstance(p_data, str):
            csv_file_data = csvwrpr.CsvWrpr(
                self.logger_name,
                p_data,
                '',
                p_struc_type=(),
                p_header=p_header,
                p_verbose=p_verbose,
                p_bar_len=self.bar_len,
                p_msg_width=self.msg_width,
            ).csv_db
        else:
            csv_file_data = ()
            print('Incorect data structure')
        if p_insert_header and p_header:
            header = [tuple(p_header)]
            csv_file_data = header + csv_file_data
        for seq in p_split_struct:
            table = p_split_struct[seq]['TableName']
            new_header = ()
            field_list = []
            field_config = []
            for field in p_split_struct[seq]['Flds']:
                field_config = []
                t_str = (field[1],)
                new_header = new_header + t_str
                if field[0] != 'None':
                    field_config.append(csv_file_data[0].index(field[0]))
                else:
                    field_config.append(-1)
                field_config = field_config + field[2]
                field_list.append(field_config)
            newcsv_db = [new_header]
            table_len = len(csv_file_data[1:])
            if isinstance(p_data, list):
                msg = beetools.msg_display(
                    'Split data to {} ({})'.format(table, table_len),
                    p_len=self.msg_width,
                )
            elif isinstance(p_data, str):
                msg = beetools.msg_display(
                    'Split {} to {} ({})'.format(
                        os.path.split(p_data)[1], table, table_len
                    ),
                    p_len=self.msg_width,
                )
            c_field_nr = 0
            c_cmd_opy = 0
            c_cmd_insert = 1
            c_cmd_split = 2
            c_cmd_date = 3
            c_cmd_look_up = 4
            c_cmd_copy_sub = 5
            c_cmd_auto_inc = 6
            c_no_trunc = 0
            c_cmd = 1
            c_parm1 = 2
            c_parm2 = 3
            c_parm3 = 4
            c_parm3_rep_str = 0
            c_parm3_def_str = 1
            dfx = displayfx.DisplayFx(
                _PROJ_NAME,
                len(csv_file_data[1:]),
                p_msg=msg,
                p_verbose=False,
                p_bar_len=self.bar_len,
            )
            for i, row in enumerate(csv_file_data[1:]):
                new_row = ()
                add_row = True
                for field_det in field_list:
                    t_str = ''
                    if field_det[c_cmd] == c_cmd_opy:  # Copy / duplicate
                        if field_det[c_parm1] == c_no_trunc or isinstance(
                            row[field_det[c_field_nr]], str
                        ):
                            t_str = row[field_det[c_field_nr]]
                        else:
                            t_str = row[field_det[c_field_nr]][0 : field_det[c_parm1]]
                        if len(field_det) > 4:
                            if t_str in field_det[c_parm3][c_parm3_rep_str]:
                                t_str = field_det[c_parm3][c_parm3_def_str]
                    elif field_det[c_cmd] == c_cmd_insert:  # Insert fixed value
                        t_str = field_det[c_parm1]
                    elif (
                        field_det[c_cmd] == c_cmd_split
                    ):  # Insert fixed value from split field
                        if row[field_det[c_field_nr]].count(',') >= field_det[c_parm1]:
                            t_str = row[field_det[c_field_nr]].split(',')[
                                field_det[c_parm1]
                            ]
                        else:
                            t_str = ''
                    elif field_det[c_cmd] == c_cmd_date:  # Insert special value
                        if field_det[c_parm1] == 'Date':
                            t_str = row[field_det[c_field_nr]] + '/01/01'
                        else:
                            print('my_sql_db: 143 - Unknown value -', field_list[1])
                    elif (
                        field_det[c_cmd] == c_cmd_look_up
                    ):  # Replace with look up value
                        if row[field_det[c_field_nr]] in field_det[c_parm1]:
                            t_str = field_det[c_parm1][row[field_det[0]]]
                    elif (
                        field_det[c_cmd] == c_cmd_copy_sub
                    ):  # Replace with substring from original field
                        t_str = row[field_det[c_field_nr]][
                            field_det[c_parm1][0] : field_det[c_parm1][1]
                        ]
                    elif field_det[c_cmd] == c_cmd_auto_inc:  # Insert auto number
                        t_str = field_det[c_parm1]
                        field_det[c_parm1] += 1
                    if isinstance(t_str, str):
                        t_str = t_str.strip()
                    new_row = new_row + (t_str,)
                    if field_det[c_parm2] and not t_str:
                        add_row = add_row and False
                        break
                if add_row:
                    newcsv_db.append(new_row)
                dfx.update(i)
            self.import_csv(
                p_table_PROJ_NAME=table,
                p_csv_db=newcsv_db,
                p_header=new_header,
                p_verbose=p_verbose,
                p_replace=p_split_struct[seq]['Replace'],
            )

    # end import_and_split_csv

    def _print_err_msg(self, p_err, p_msg=''):
        msg = p_msg
        if p_msg:
            msg = '{}\n'.format(p_msg)
        print(
            beetools.msg_error(
                '{}Err No:\t\t{}\nSQL State:\t{}\nErr Msg:\t{}\nSystem terminated...'.format(
                    msg, p_err.errno, p_err.sqlstate, p_err.msg
                )
            )
        )
        pass

    # end printErrMsg


# end SQLDbWrpr


class MySQL(SQLDbWrpr):
    '''This module creates a wrapper for the MySql database.'''

    def __init__(
        self,
        p_parent_logger_name,
        p_host_name='localhost',
        p_user_name='',
        p_password='',
        p_user_rights=False,
        p_recreate_db=False,
        p_db_name=None,
        p_db_structure={},
        p_batch_size=10000,
        p_bar_len=50,
        p_msg_width=50,
        p_verbose=False,
        p_admin_userName=False,
        p_admin_user_password=False,
    ):
        '''Description'''
        super().__init__(
            p_parent_logger_name,
            p_host_name=p_host_name,
            p_user_name=p_user_name,
            p_password=p_password,
            p_db_name=p_db_name,
            p_recreate_db=p_recreate_db,
            p_db_structure=p_db_structure,
            p_batch_size=p_batch_size,
            p_bar_len=p_bar_len,
            p_msg_width=p_msg_width,
            p_verbose=p_verbose,
        )
        try:
            self.conn = mysql.connector.connect(
                host=self.host_PROJ_NAME,
                user=self.user_PROJ_NAME,
                password=self._password,
                database=None,
                auth_plugin='mysql_native_password',
            )
            self.cur = self.conn.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(
                    beetools.msg_error(
                        "User '{}'@'{}' does not exist\nAtempt to create it...".format(
                            self.user_PROJ_NAME, self.host_PROJ_NAME
                        )
                    )
                )
                if p_admin_userName and p_admin_user_password and p_user_rights:
                    try:
                        self.conn = mysql.connector.connect(
                            host=self.host_PROJ_NAME,
                            user=p_admin_userName,
                            password=p_admin_user_password,
                            database=None,
                            auth_plugin='mysql_native_password',
                        )
                    except mysql.connector.Error as err:
                        self._print_err_msg(
                            err,
                            'Admin user name and/or password not supplied or incorrect',
                        )
                    if self.conn.is_connected():
                        self.cur = self.conn.cursor()
                        self.create_users(
                            [p_admin_userName, p_admin_user_password],
                            [[p_user_name, p_password]],
                        )
                        self.grant_rights(
                            [p_admin_userName, p_admin_user_password], [p_user_rights]
                        )
                    else:
                        print(
                            beetools.msg_error('Could not connect\nSystem terminated')
                        )
                        sys.exit()
                else:
                    self._print_err_msg(
                        err,
                        'User name and/or password and/or user access rights not supplied or incorrect',
                    )
                    sys.exit()
            self.close()
        if not self.conn.is_connected():
            self.conn = mysql.connector.connect(
                host=self.host_PROJ_NAME,
                user=self.user_PROJ_NAME,
                password=self._password,
                database=None,
                auth_plugin='mysql_native_password',
            )
            self.cur = self.conn.cursor()
        if self.re_create_db:
            if self.create_db():
                self.create_tables()
        elif self.db_name:
            self.conn.cmd_init_db(self.db_name)
            self.conn.commit()
        self.success = True
        pass

    # end __int__


# end MySQL


class MSSQL(SQLDbWrpr):
    '''This module creates a wrapper for the MySql database.'''

    def __init__(
        self,
        p_parent_logger_name,
        p_host_name='localhost',
        p_user_name='',
        p_password='',
        p_recreate_db=False,
        p_db_name=None,
        p_db_structure={},
        p_batch_size=10000,
        p_bar_len=50,
        p_msg_width=50,
        p_verbose=False,
    ):
        '''Description'''
        super().__init__(
            p_parent_logger_name,
            p_host_name=p_host_name,
            p_user_name=p_user_name,
            p_password=p_password,
            p_db_name=p_db_name,
            p_recreate_db=p_recreate_db,
            p_db_structure=p_db_structure,
            p_batch_size=p_batch_size,
            p_bar_len=p_bar_len,
            p_msg_width=p_msg_width,
            p_verbose=p_verbose,
        )
        try:
            self.host_PROJ_NAME = '156.38.224.15,1433'
            self.user_PROJ_NAME = 'chessaco_chessanew'
            self._password = '@Jv&F77%'
            self.db_name = 'chessaco_analytics'
            self.driver = '{ODBC Driver 17 for SQL Server}'
            # driver = pyodbc.drivers()
            # con_str_1 = 'DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format( self.driver, self.host_PROJ_NAME, self.db_name, self.user_PROJ_NAME, self._password )
            con_str_2 = (
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                + self.host_PROJ_NAME
                + ';DATABASE='
                + self.db_name
                + ';UID='
                + self.user_PROJ_NAME
                + ';PWD='
                + self._password
            )
            self.conn = pyodbc.connect(con_str_2)
            pass
        except Error as err:
            self.logger.error(err)
        self.success = self.conn.is_connected()
        if self.conn.is_connected():
            self.cur = self.conn.cursor()
            if self.re_create_db:
                self.create_db()
                self.success = self.create_tables()


# end MSSQL


def do_tests(p_app_path='', p_cls=True):
    '''Test the class methods.  Also called by the PackageIt PIP app to
    test the module during PIP installation.

    Parameters
    - baseFolder    : Base folder for source code
    - cls = True    : Clear the screen at start-up
    '''

    def basic_test():
        '''Basic and mandatory scenario tests for certification of the class'''

        def t_init(
            p_db_host_PROJ_NAME,
            p_db_user,
            p_db_name,
            p_user_rigthts,
            p_db_structure,
            p_admin_user,
        ):
            success = True
            print('\nTest initialization, creation and population of database...')
            for db_vendor in ['MySQL']:
                if db_vendor == 'MySQL':
                    my_sql_db = MySQL(
                        _PROJ_NAME,
                        p_host_name=p_db_host_PROJ_NAME,
                        p_user_name=p_db_user[0],
                        p_password=p_db_user[1],
                        p_user_rights=p_user_rigthts,
                        p_recreate_db=True,
                        p_db_name=p_db_name,
                        p_db_structure=p_db_structure,
                        p_batch_size=1,
                        p_admin_userName=p_admin_user[0],
                        p_admin_user_password=p_admin_user[1],
                    )
                # elif db_vendor == 'MSSQL':
                #   msSQLDb = MSSQL( _PROJ_NAME, p_host_name = db_host_PROJ_NAME, p_user_name = db_uid, p_password = db_pwd, p_recreate_db = True, p_db_name = DbName,
                # p_db_structure = db_structure, p_batch_size = 1 )
                success = my_sql_db.success and success
                if not beetools.is_struct_the_same(
                    my_sql_db.db_structure, t_db_structure
                ):
                    success = False and success

                my_sql_db.import_csv('Country', country_path)
                my_sql_db.import_csv('Member', member_path)
                success = my_sql_db.success and success
                if success:
                    my_sql_db.cur.execute(
                        'SELECT {} FROM Member'.format(
                            ','.join(my_sql_db.db_structure['Member'])
                        )
                    )
                    table_res = my_sql_db.cur.fetchall()
                    if not beetools.is_struct_the_same(table_res, t_member_db01):
                        success = False and success
                my_sql_db.close()

                my_sql_db = MySQL(
                    _PROJ_NAME,
                    p_host_name=p_db_host_PROJ_NAME,
                    p_user_name=p_db_user[0],
                    p_password=p_db_user[1],
                    p_db_name=p_db_name,
                    p_db_structure=p_db_structure,
                    p_batch_size=1,
                )
                success = my_sql_db.success and success
                if success:
                    my_sql_db.cur.execute(
                        'SELECT {} FROM Member'.format(
                            ','.join(my_sql_db.db_structure['Member'])
                        )
                    )
                    table_res = my_sql_db.cur.fetchall()
                    if not beetools.is_struct_the_same(table_res, t_member_db01):
                        success = False and success
                my_sql_db.close()
            return success

        # end t_init

        def timport_csv(p_mysql_db_wrpr):
            '''Basic and mandatory scenario tests for certification of the class'''
            success = True
            print('\nTest import of Csv files...')
            tablest_o_load = {
                'Country': [country_path, t_country_db01],
                'Member': [member_path, t_member_db01],
                'MemberOrg': [member_org_path, t_member_org_db01],
                'Organization': [organization_path, t_organization_db01],
                'Rating': [rating_path, t_rating_db01],
            }
            for table_PROJ_NAME in p_mysql_db_wrpr.table_load_order:
                if table_PROJ_NAME in tablest_o_load:
                    p_mysql_db_wrpr.import_csv(
                        table_PROJ_NAME, tablest_o_load[table_PROJ_NAME][0]
                    )
                    success = p_mysql_db_wrpr.success and success
                    p_mysql_db_wrpr.cur.execute(
                        'SELECT {} FROM {}'.format(
                            ','.join(my_sql_db.db_structure[table_PROJ_NAME]),
                            table_PROJ_NAME,
                        )
                    )
                    table_res = p_mysql_db_wrpr.cur.fetchall()
                    if beetools.is_struct_the_same(
                        table_res, tablest_o_load[table_PROJ_NAME][1]
                    ):
                        success = True and success
            return success

        # end timport_csv

        def t_export_db(p_mysql_db_wrpr):
            '''Basic and mandatory scenario tests for certification of the class'''
            success = True
            print('\nTest export of tables to Csv files...')
            tables_to_export = {
                'Member': [member_export_path, t_member_db01],
                'MemberOrg': [member_org_export_path, t_member_org_db01],
                'Organization': [organization_export_path, t_organization_db01],
            }

            for table_PROJ_NAME in p_mysql_db_wrpr.table_load_order:
                if table_PROJ_NAME in tables_to_export:
                    vol_csv_file_name = tables_to_export[table_PROJ_NAME][0]
                    vol_cntr = 1
                    while os.path.isfile(vol_csv_file_name):
                        os.remove(vol_csv_file_name)
                        vol_cntr += 1
                        vol_csv_file_name = (
                            member_export_path[:-4]
                            + '{:0>2}'.format(vol_cntr)
                            + member_export_path[-4:]
                        )
                    p_mysql_db_wrpr.export_to_csv(
                        tables_to_export[table_PROJ_NAME][0], table_PROJ_NAME
                    )
                    success = p_mysql_db_wrpr.success and success
                    p_mysql_db_wrpr.cur.execute(
                        'TRUNCATE TABLE {}'.format(table_PROJ_NAME)
                    )
                    p_mysql_db_wrpr.conn.commit()
                    p_mysql_db_wrpr.import_csv(
                        table_PROJ_NAME, tables_to_export[table_PROJ_NAME][0]
                    )
                    p_mysql_db_wrpr.cur.execute(
                        'SELECT {} FROM {}'.format(
                            ','.join(my_sql_db.db_structure[table_PROJ_NAME]),
                            table_PROJ_NAME,
                        )
                    )
                    table_res = p_mysql_db_wrpr.cur.fetchall()
                    if not beetools.is_struct_the_same(
                        table_res, tables_to_export[table_PROJ_NAME][1]
                    ):
                        success = False and success
            return success

        # end t_export_db

        def tsql_query(p_mysql_db_wrpr):
            '''Basic and mandatory scenario tests for certification of the class'''
            success = True
            print('\nTest SQL query feature...')
            sql_query = [
                ['Surname', 'Name', 'OrgName'],
                '''SELECT Member.Surname, Member.Name, Organization.OrgName
                                                              FROM Member
                                                                JOIN MemberOrg ON Member.Surname = MemberOrg.Surname AND Member.Name = MemberOrg.Name
                                                                JOIN Organization ON MemberOrg.OrgId = Organization.OrgId
                                                                  WHERE Organization.OrgName = "St Louis Chess Club"''',
            ]
            my_sql_db.export_to_csv(export_join_path, 'Member', p_sql_query=sql_query)
            csv_file_join_data = csvwrpr.CsvWrpr(
                _PROJ_NAME,
                p_csv_file_name=export_join_path,
                p_key1='Surname',
                p_header=sql_query[0],
                p_del_head=True,
                p_struc_type=[],
            )
            if not beetools.is_struct_the_same(
                csv_file_join_data.csv_db, t_join_member_member_org_db
            ):
                success = False
            return success

        # end tsql_query

        def t_multi_volume(p_mysql_db_wrpr):
            '''Basic and mandatory scenario tests for certification of the class'''
            success = True
            print('\nTest multi volume import of Csv files...')
            vol_csv_file_name = member_export_path
            vol_cntr = 1
            while os.path.isfile(vol_csv_file_name):
                os.remove(vol_csv_file_name)
                vol_cntr += 1
                vol_csv_file_name = (
                    member_export_path[:-4]
                    + '{:0>2}'.format(vol_cntr)
                    + member_export_path[-4:]
                )
            p_mysql_db_wrpr.export_to_csv(member_export_path, 'Member')
            p_mysql_db_wrpr.cur.execute('TRUNCATE TABLE Member')
            p_mysql_db_wrpr.conn.commit()
            p_mysql_db_wrpr.import_csv('Member', member_export_path)
            p_mysql_db_wrpr.cur.execute(
                'SELECT Surname, Name, SosSec, Country, PassportNr, Race, RegDateTime, Picture, ActiveStatus, BirthYear, DOB FROM Member'
            )
            t_vol_test01 = p_mysql_db_wrpr.cur.fetchall()
            if not beetools.is_struct_the_same(t_vol_test01, t_member_db01):
                success = False

            # multi_vol_csv_path = os.path.join(test_data_folder, 'MultiVolCsv1.csv')
            if os.path.isfile(member_export_path):
                os.remove(member_export_path)
            file_PROJ_NAME_list = p_mysql_db_wrpr.export_to_csv(
                member_export_path, 'Member', p__vol_size=1
            )
            p_mysql_db_wrpr.cur.execute('TRUNCATE TABLE Member')
            p_mysql_db_wrpr.conn.commit()
            p_mysql_db_wrpr.import_csv('Member', member_export_path, p_vol_type='Multi')
            p_mysql_db_wrpr.cur.execute(
                'SELECT Surname, Name, ActiveStatus FROM Member ORDER BY Surname'
            )
            t_multi_vol_test01 = p_mysql_db_wrpr.cur.fetchall()
            if (
                not beetools.is_struct_the_same(t_multi_vol_test01, t_member_db02)
                and not file_PROJ_NAME_list
            ):
                success = False
            return success

        # end p_mysql_db_wrpr

        def t_split_file01(p_mysql_db_wrpr):
            '''Basic and mandatory scenario tests for certification of the class'''
            success = True
            print('\nTest split file structure feature...')
            look_up_tbl = {'Asian': 1, 'Black': 2, 'White': 5}
            tablest_o_load = {
                'Country': [country_path, t_country_db01],
                'Rating': [rating_path, t_rating_db01],
            }
            my_sql_db = MySQL(
                _PROJ_NAME,
                p_host_name=db_host_PROJ_NAME,
                p_user_name=db_user[0],
                p_password=db_user[1],
                p_recreate_db=True,
                p_db_name=db_name,
                p_db_structure=db_structure,
                p_batch_size=1,
            )
            for table_PROJ_NAME in p_mysql_db_wrpr.table_load_order:
                if table_PROJ_NAME in tablest_o_load:
                    p_mysql_db_wrpr.import_csv(
                        table_PROJ_NAME, tablest_o_load[table_PROJ_NAME][0]
                    )
                    success = p_mysql_db_wrpr.success and success
                    p_mysql_db_wrpr.cur.execute(
                        'SELECT {} FROM {}'.format(
                            ','.join(my_sql_db.db_structure[table_PROJ_NAME]),
                            table_PROJ_NAME,
                        )
                    )
                    table_res = p_mysql_db_wrpr.cur.fetchall()
                    if beetools.is_struct_the_same(
                        table_res, tablest_o_load[table_PROJ_NAME][1]
                    ):
                        success = True and success

            split_struct = {
                'Seq01': {
                    'TableName': 'Member',
                    'Key': 'Surname',
                    'Replace': False,
                    'Flds': [
                        ['SurnameName', 'Surname', [2, 0, True]],
                        ['SurnameName', 'Name', [2, 1, True]],
                        [
                            'IDNr',
                            'SosSec',
                            [
                                0,
                                0,
                                True,
                                [
                                    [],
                                ],
                            ],
                        ],
                        ['Country', 'Country', [0, 0, True, [['', None], 'CHN']]],
                        ['None', 'PassportNr', [6, 100, True]],
                        ['Race', 'Race', [4, look_up_tbl, True]],
                        ['Picture', 'Picture', [1, None, False]],
                        ['ActiveStatus', 'ActiveStatus', [1, 1, True]],
                        [
                            'BirthYear',
                            'BirthYear',
                            [
                                0,
                                0,
                                True,
                                [
                                    [],
                                ],
                            ],
                        ],
                        ['BirthYear', 'DOB', [3, 'Date', True]],
                    ],
                },
                'Seq02': {
                    'TableName': 'Organization',
                    'Key': 'OrgId',
                    'Replace': True,
                    'Flds': [
                        ['OrgId', 'OrgId', [0, 0, True]],
                        ['OrgName', 'OrgName', [5, [0, 8], True]],
                        ['RegFee', 'RegFee', [0, 0, True]],
                        ['OpenTrading', 'OpenTrading', [0, 0, True]],
                    ],
                },
                'Seq03': {
                    'TableName': 'MemberOrg',
                    'Key': 'Surname',
                    'Replace': False,
                    'Flds': [
                        ['SurnameName', 'Surname', [2, 0, True]],
                        ['SurnameName', 'Name', [2, 1, True]],
                        ['OrgId', 'OrgId', [0, 0, True]],
                    ],
                },
            }
            my_sql_db.import_and_split_csv(
                split_struct,
                split_test_csv_path,
                p_header=[
                    'SurnameName',
                    'IDNr',
                    'Country',
                    'PassportNr',
                    'Race',
                    'Picture',
                    'ActiveStatus',
                    'OrgId',
                    'OrgName',
                    'RegFee',
                    'OpenTrading',
                ],
                p_verbose=True,
            )
            my_sql_db.cur.execute(
                'SELECT {} FROM Member'.format(
                    ','.join(p_mysql_db_wrpr.db_structure['Member'])
                )
            )
            t_member_split_res = my_sql_db.cur.fetchall()
            if not beetools.is_struct_the_same(t_member_split_res, t_member_db03):
                success = False
            my_sql_db.cur.execute(
                'SELECT {} FROM Organization'.format(
                    ','.join(p_mysql_db_wrpr.db_structure['Organization'])
                )
            )
            t_org_split_res = my_sql_db.cur.fetchall()
            if not beetools.is_struct_the_same(t_org_split_res, t_organization_db02):
                success = False
            my_sql_db.cur.execute(
                'SELECT {} FROM MemberOrg'.format(
                    ','.join(p_mysql_db_wrpr.db_structure['MemberOrg'])
                )
            )
            t_member_org_split_res = my_sql_db.cur.fetchall()
            if not beetools.is_struct_the_same(
                t_member_org_split_res, t_member_org_db02
            ):
                success = False
            my_sql_db.close()
            return success

        # end t_split_file01

        def t_incomplete_records():
            '''Read file with incomplete records'''
            success = True
            print('\nTest import of incomplete records...')
            tablest_o_load = {
                'Country': [country_path, t_country_db01],
                'Member': [incomplete_records_path, t_ember_db04],
            }

            my_sql_db = MySQL(
                _PROJ_NAME,
                p_host_name=db_host_PROJ_NAME,
                p_user_name=db_user[0],
                p_password=db_user[1],
                p_recreate_db=True,
                p_db_name=db_name,
                p_db_structure=db_structure,
                p_batch_size=1,
            )
            for table_PROJ_NAME in my_sql_db.table_load_order:
                if table_PROJ_NAME in tablest_o_load:
                    my_sql_db.import_csv(
                        table_PROJ_NAME, tablest_o_load[table_PROJ_NAME][0]
                    )
                    success = my_sql_db.success and success
                    my_sql_db.cur.execute(
                        'SELECT {} FROM {}'.format(
                            ','.join(my_sql_db.db_structure[table_PROJ_NAME]),
                            table_PROJ_NAME,
                        )
                    )
                    table_res = my_sql_db.cur.fetchall()
                    if not beetools.is_struct_the_same(
                        table_res, tablest_o_load[table_PROJ_NAME][1]
                    ):
                        success = False and success
            my_sql_db.close()
            return success

        # end t_incomplete_records

        def t_user_creation(
            p_db_host_PROJ_NAME,
            p_db_user,
            p_db_name,
            p_user_rights,
            p_db_structure,
            p_admin_user,
            p_new_users,
            p_new_user_rights,
        ):
            success = True
            print('\nTest initialization, creation and population of database...')
            for db_vendor in ['MySQL']:
                if db_vendor == 'MySQL':
                    my_sql_db = MySQL(
                        _PROJ_NAME,
                        p_host_name=p_db_host_PROJ_NAME,
                        p_user_name=p_db_user[0],
                        p_password=p_db_user[1],
                        p_user_rights=p_user_rights,
                        p_admin_userName=p_admin_user[0],
                        p_admin_user_password=p_admin_user[1],
                    )
                    my_sql_db.create_users(p_admin_user, p_new_users)
                    my_sql_db.grant_rights(p_admin_user, p_new_user_rights)
                    my_sql_db.delete_users(p_admin_user, p_new_users)
            return success

        # end t_user_creation

        success = True
        system_PROJ_NAME = platform.node()
        if system_PROJ_NAME in ['ip-172-31-18-250']:
            db_host_PROJ_NAME = 'ccstldb.c9dax5ifrbth.us-east-1.rds.amazonaws.com'
            db_name = 'urs_v2_dev2'
            db_user = ['urs_devuser', '31u!Rg1UEmv9Iw$x']
        else:
            admin_user = ['root', 'En0l@Gay']
            db_host_PROJ_NAME = 'localhost'
            db_name = 'SQLDbWrpr'
            db_user = ['rtinstall', 'Rt1nst@ll']
            db_user_rights = [db_user[0], db_host_PROJ_NAME, '*', '*', 'ALL']
            new_users = [
                ['Testing01', '1re$UtseT', 'localhost'],
                ['Testing02', '2re$UtseT', 'localhost'],
            ]
            new_user_rights = [
                [new_users[0][0], new_users[0][2], '*', '*', 'ALL'],
                [new_users[1][0], new_users[1][2], '*', '*', 'SELECT', 'INSERT'],
            ]
        test_data_folder = Path(__file__).absolute().parents[3] / _PROJ_NAME / 'Data'
        country_path = os.path.join(test_data_folder, 'Country.csv')
        # country_export_path = os.path.join(test_data_folder, 'CountryExport.csv')
        export_join_path = os.path.join(test_data_folder, 'JoinExport.csv')
        incomplete_records_path = os.path.join(
            test_data_folder, 'IncompleteRecords.csv'
        )
        member_export_path = os.path.join(test_data_folder, 'MemberExport.csv')
        member_org_export_path = os.path.join(test_data_folder, 'MemberOrgExport.csv')
        member_org_path = os.path.join(test_data_folder, 'MemberOrg.csv')
        member_path = os.path.join(test_data_folder, 'Member.csv')
        organization_export_path = os.path.join(
            test_data_folder, 'OrganizationExport.csv'
        )
        organization_path = os.path.join(test_data_folder, 'Organization.csv')
        # rating_export_path = os.path.join(test_data_folder, 'RatingExport.csv')
        # rating_export_path = os.path.join( test_data_folder, 'RatingExport.csv' )
        rating_path = os.path.join(test_data_folder, 'Rating.csv')
        split_test_csv_path = os.path.join(test_data_folder, 'SplitFile01.csv')
        db_structure = {
            'Rating': {
                'Date': {
                    'Type': ['date'],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [1, 1, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rate of publication',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [1, 2, 'Member', 'Name', 'C', 'C'],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name from Member',
                },
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [1, 1, 'Member', 'Surname', 'C', 'C'],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname from Member',
                },
                'Rating': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rating of member',
                },
                'OrgMemberId': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [1, 2, 'A', 'U'],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rating of member',
                },
            },
            'Member': {
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname of member',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name of the member',
                },
                'SosSec': {
                    'Type': ['varchar', 10],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [1, 1, 'D', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Sosial security nr filled with zeros',
                },
                'Country': {
                    'Type': ['char', 3],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [1, 1, 'Country', 'Code', 'R', 'C'],
                        'Index': [2, 2, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Country passport',
                },
                'PassportNr': {
                    'Type': ['char', 15],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [2, 1, 'D', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Passport number',
                },
                'Race': {
                    'Type': ['tinyint'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '1',
                    },
                    'Possible Values': '1=White,2=Balck',
                    'Comment': 'Race of member',
                },
                'RegDateTime': {
                    'Type': ['datetime'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [3, 1, 'D', 'U'],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Registration date',
                },
                'Picture': {
                    'Type': ['blob'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': 'Y',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Photo of member',
                },
                'ActiveStatus': {
                    'Type': ['boolean'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Active | Inactive',
                },
                'BirthYear': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Birth year of member',
                },
                'DOB': {
                    'Type': ['date'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Date of Birth',
                },
            },
            'Country': {
                'Code': {
                    'Type': ['char', 3],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': '3 digit country code',
                },
                'Description': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name of country',
                },
            },
            'Organization': {
                'OrgId': {
                    'Type': ['bigint'],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [1, 1, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': 'Y',
                        'G': 'Y',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Organization id auto generated',
                },
                'OrgName': {
                    'Type': ['varchar', 20],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [2, 1, 'A', ''],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Organization name',
                },
                'RegFee': {
                    'Type': ['decimal', 5, 2],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Registration fee',
                },
                'OpenTrading': {
                    'Type': ['time'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Opening time for trading',
                },
            },
            'MemberOrg': {
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname from Member',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name from Member',
                },
                'OrgId': {
                    'Type': [
                        'bigint',
                    ],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'OrgId from Organizarion',
                },
            },
        }
        t_db_structure = {
            'Rating': {
                'Date': {
                    'Type': ['date'],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [1, 1, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rate of publication',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name from Member',
                },
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname from Member',
                },
                'Rating': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rating of member',
                },
                'OrgMemberId': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [1, 2, 'A', 'U'],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Rating of member',
                },
            },
            'Member': {
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname of member',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name of the member',
                },
                'SosSec': {
                    'Type': ['varchar', 10],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [1, 1, 'D', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Sosial security nr filled with zeros',
                },
                'Country': {
                    'Type': ['char', 3],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [1, 1, 'Country', 'Code', 'R', 'C'],
                        'Index': [2, 2, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Country passport',
                },
                'PassportNr': {
                    'Type': ['char', 15],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [2, 1, 'D', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Passport number',
                },
                'Race': {
                    'Type': ['tinyint'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '1',
                    },
                    'Possible Values': '1=White,2=Balck',
                    'Comment': 'Race of member',
                },
                'RegDateTime': {
                    'Type': ['datetime'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [3, 1, 'D', 'U'],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Registration date',
                },
                'Picture': {
                    'Type': ['blob'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': 'Y',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Photo of member',
                },
                'ActiveStatus': {
                    'Type': ['boolean'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Active | Inactive',
                },
                'BirthYear': {
                    'Type': ['int'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Birth year of member',
                },
                'DOB': {
                    'Type': ['date'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Date of Birth',
                },
            },
            'Country': {
                'Code': {
                    'Type': ['char', 3],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': '3 digit country code',
                },
                'Description': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name of country',
                },
            },
            'Organization': {
                'OrgId': {
                    'Type': ['bigint'],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [1, 1, 'A', 'U'],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': 'Y',
                        'G': 'Y',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Organization id auto generated',
                },
                'OrgName': {
                    'Type': ['varchar', 20],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [2, 1, 'A', ''],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Organization name',
                },
                'RegFee': {
                    'Type': ['decimal', 5, 2],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Registration fee',
                },
                'OpenTrading': {
                    'Type': ['time'],
                    'Params': {
                        'PrimaryKey': ['', ''],
                        'FKey': [],
                        'Index': [],
                        'NN': '',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Opening time for trading',
                },
            },
            'MemberOrg': {
                'Surname': {
                    'Type': ['varchar', 45],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Surname from Member',
                },
                'Name': {
                    'Type': ['varchar', 30],
                    'Params': {
                        'PrimaryKey': ['Y', 'A'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': '',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'Name from Member',
                },
                'OrgId': {
                    'Type': ['bigint'],
                    'Params': {
                        'PrimaryKey': ['Y', 'D'],
                        'FKey': [],
                        'Index': [],
                        'NN': 'Y',
                        'B': '',
                        'UN': 'Y',
                        'ZF': '',
                        'AI': '',
                        'G': '',
                        'DEF': '',
                    },
                    'Possible Values': '',
                    'Comment': 'OrgId from Organizarion',
                },
            },
        }
        t_join_member_member_org_db = [
            ['Ding', 'Liren', 'St Louis Chess Club'],
            ['Nakamura', 'Hikaru', 'St Louis Chess Club'],
        ]
        t_member_db01 = [
            (
                'Carlsen',
                'Magnus',
                'A123456781',
                'NOR',
                'AB12CD34',
                5,
                datetime.datetime(year=2020, month=3, day=26, hour=7, minute=0),
                None,
                1,
                1990,
                datetime.date(1990, 11, 30),
            ),
            (
                'Ding',
                'Liren',
                'B123456791',
                'CHN',
                'CD56EF78',
                1,
                datetime.datetime(year=2020, month=4, day=16, hour=8, minute=10),
                None,
                1,
                2000,
                datetime.date(1992, 10, 24),
            ),
            (
                'Nakamura',
                'Hikaru',
                'C123456793',
                'USA',
                'EF90GH12',
                5,
                datetime.datetime(
                    year=2020, month=4, day=30, hour=9, minute=20, second=10
                ),
                None,
                0,
                1980,
                datetime.date(2002, 11, 30),
            ),
        ]
        t_member_db02 = [
            ('Carlsen', 'Magnus', 1),
            ('Ding', 'Liren', 1),
            ('Nakamura', 'Hikaru', 0),
        ]
        t_member_db03 = [
            (
                'Carlsen',
                'Magnus',
                'A123456781',
                'NOR',
                '100',
                5,
                None,
                None,
                1,
                1990,
                datetime.date(year=1990, month=1, day=1),
            ),
            (
                'Ding',
                'Liren',
                'B123456791',
                'CHN',
                '101',
                1,
                None,
                None,
                1,
                2000,
                datetime.date(year=2000, month=1, day=1),
            ),
            (
                'Nakamura',
                'Hikaru',
                'C123456793',
                'USA',
                '102',
                5,
                None,
                None,
                1,
                1980,
                datetime.date(year=1980, month=1, day=1),
            ),
        ]
        t_ember_db04 = [
            (
                'Carlsen',
                'Magnus',
                'A123456781',
                'NOR',
                'AB12CD34',
                5,
                datetime.datetime(year=2020, month=3, day=26, hour=7, minute=0),
                None,
                1,
                1990,
                None,
            ),
            (
                'Ding',
                'Liren',
                'B123456791',
                'CHN',
                'CD56EF78',
                1,
                datetime.datetime(year=2020, month=4, day=16, hour=8, minute=10),
                None,
                1,
                2000,
                None,
            ),
            (
                'Nakamura',
                'Hikaru',
                'C123456793',
                'USA',
                'EF90GH12',
                5,
                datetime.datetime(
                    year=2020, month=4, day=30, hour=9, minute=20, second=10
                ),
                None,
                0,
                1980,
                None,
            ),
        ]
        t_member_org_db01 = [
            ('Carlsen', 'Magnus', 6),
            ('Ding', 'Liren', 3),
            ('Nakamura', 'Hikaru', 3),
        ]
        t_member_org_db02 = [
            ('Carlsen', 'Magnus', 6),
            # ( 'Ding'   ,  'Liren',  3 ),
            ('Nakamura', 'Hikaru', 3),
        ]
        t_country_db01 = [
            ('CHN', 'China'),
            ('NOR', 'Norway'),
            ('USA', 'United States of America'),
        ]
        t_organization_db01 = [
            (2, 'Boondocs Chess Club', 150.00, datetime.timedelta(seconds=68400)),
            (3, 'St Louis Chess Club', 100.00, datetime.timedelta(seconds=32400)),
            (6, 'Ice Cold Chess Club', 20.00, datetime.timedelta(seconds=28800)),
        ]
        t_organization_db02 = [
            (3, 'St Louis', 100.00, datetime.timedelta(seconds=32400)),
            (6, 'Ice Cold', 20.00, datetime.timedelta(seconds=28800)),
        ]
        t_rating_db01 = [
            (datetime.date(2020, 2, 29), 'Hikaru', 'Nakamura', 2750, 123456),
            (datetime.date(2020, 2, 29), 'Liren', 'Ding', 2800, 234567),
            (datetime.date(2020, 2, 29), 'Magnus', 'Carlsen', 2850, 456789),
            (datetime.date(2020, 3, 31), 'Hikaru', 'Nakamura', 2760, 123456),
            (datetime.date(2020, 3, 31), 'Liren', 'Ding', 2830, 234567),
            (datetime.date(2020, 3, 31), 'Magnus', 'Carlsen', 2845, 456789),
        ]
        # del_users = [[x[0], x[2]] for x in new_users]

        success = (
            t_init(
                db_host_PROJ_NAME,
                db_user,
                db_name,
                db_user_rights,
                db_structure,
                admin_user,
            )
            and success
        )
        success = (
            t_user_creation(
                db_host_PROJ_NAME,
                db_user,
                db_name,
                db_user_rights,
                db_structure,
                admin_user,
                new_users,
                new_user_rights,
            )
            and success
        )
        my_sql_db = MySQL(
            _PROJ_NAME,
            p_host_name=db_host_PROJ_NAME,
            p_user_name=db_user[0],
            p_password=db_user[1],
            p_recreate_db=True,
            p_db_name=db_name,
            p_db_structure=db_structure,
            p_batch_size=1,
        )
        success = my_sql_db.success and success
        if not beetools.is_struct_the_same(my_sql_db.db_structure, t_db_structure):
            success = False and success
        success = timport_csv(my_sql_db) and success
        success = t_export_db(my_sql_db) and success
        success = tsql_query(my_sql_db) and success
        success = t_multi_volume(my_sql_db) and success
        my_sql_db.close()
        my_sql_db = MySQL(
            _PROJ_NAME,
            p_host_name=db_host_PROJ_NAME,
            p_user_name=db_user[0],
            p_password=db_user[1],
            p_recreate_db=True,
            p_db_name=db_name,
            p_db_structure=db_structure,
            p_batch_size=1,
        )
        success = t_split_file01(my_sql_db) and success
        my_sql_db.close()
        success = t_incomplete_records() and success
        return success

    # end basic_test

    success = True
    b_tls = beetools.Archiver(
        _PROJ_DESC,
        _PROJ_PATH,
        p_app_ini_file_name=None,
        p_cls=True,
        # p_logger = False,
        p_arc_excl_dir=None,
        p_arc_extern_dir=None,
        p_arc_incl_ext=None,
    )
    logger = logging.getLogger(_PROJ_NAME)
    logger.setLevel(beetools.DEF_LOG_LEV)
    file_handle = logging.FileHandler(beetools.LOG_FILE_NAME, mode='w')
    file_handle.setLevel(beetools.DEF_LOG_LEV_FILE)
    console_handle = logging.StreamHandler()
    console_handle.setLevel(beetools.DEF_LOG_LEV_CON)
    file_format = logging.Formatter(
        beetools.LOG_FILE_FORMAT, datefmt=beetools.LOG_DATE_FORMAT
    )
    console_format = logging.Formatter(beetools.LOG_CONSOLE_FORMAT)
    file_handle.setFormatter(file_format)
    console_handle.setFormatter(console_format)
    logger.addHandler(file_handle)
    logger.addHandler(console_handle)

    b_tls.print_header(p_cls=p_cls)
    success = basic_test()
    beetools.result_rep(success, 'Done')
    b_tls.print_footer()
    if success:
        return b_tls.arc_pth
    return False


# end do_tests

if __name__ == '__main__':
    do_tests(p_app_path=_PROJ_PATH)
# end __main__
