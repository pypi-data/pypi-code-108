'''Fix a date and present it in specified format

Attempts to correct dates and convert to standard format
'''


import datetime
import logging
from pathlib import Path
import sys
import beetools

_VERSION = '1.13.4'
_path = Path(sys.argv[0])
_name = _path.stem


class FixDate:
    '''Attempts to correct dates and convert to standard format'''

    def __init__(
        self,
        p_parent_logger_name,
        p_in_date_str,
        p_out_format='%Y%m%d',
        p_in_format='YMD',
        p_set_day_to_one=True,
    ):
        '''Description'''
        self.logger_name = '{}.{}'.format(p_parent_logger_name, _name)
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info('Start')
        self.version = _VERSION
        self.success = False
        self.success = False
        self.comp_pos_day = False
        self.comp_pos_month = False
        self.comp_pos_year = False
        self.date = None
        self.day = None
        self.even_day_months = [4, 6, 9, 11]
        self.in_date_str = p_in_date_str
        self.in_format = p_in_format
        self.leap_day_months = [2]
        self.month = None
        self.month_dict = {
            'JAN': 1,
            'FEB': 2,
            'MAR': 3,
            'APR': 4,
            'MAY': 5,
            'JUN': 6,
            'JUL': 7,
            'AUG': 8,
            'SEP': 9,
            'OCT': 10,
            'NOV': 11,
            'DEC': 12,
        }
        self.seperators = '/-.'
        self.set_day_to_one = p_set_day_to_one
        self.un_even_day_months = [0, 1, 3, 5, 7, 8, 10, 12]
        self.year = None
        self._get_comp_pos()
        if self._get_components():
            if self._fix_type_errors():
                self._fix_century()
                try:
                    self.date = datetime.date(self.year, self.month, self.day)
                    self.date_str = self.date.strftime(p_out_format)
                    self.success = True
                except ValueError:
                    if self.year > 0 and self.month > 0 and self.day > 0:
                        self._check_day_and_month_swap()
                        try:
                            self.date = datetime.date(self.year, self.month, self.day)
                            self.date_str = self.date.strftime(p_out_format)
                            self.success = True
                        except ValueError:
                            if self.set_day_to_one:
                                self._set_day_to_one()
                                try:
                                    self.date = datetime.date(
                                        self.year, self.month, self.day
                                    )
                                    self.date_str = self.date.strftime(p_out_format)
                                    self.success = True
                                except ValueError:
                                    print(
                                        'Scenario not forseen.  Forced system exit:\nYear: {}, Month: {}, Day: {}'.format(
                                            self.year, self.month, self.day
                                        )
                                    )
                                    self.success = False
                                    sys.exit()
        if not self.success:
            self.day = None
            self.month = None
            self.year = None
            self.date = None
            self.date_str = ''
        pass

    # end __init__

    def _check_day_and_month_swap(self):
        '''Description'''
        if self.month < 1 or self.month > 12:
            if self.day >= 1 or self.day <= 12:
                if (
                    (
                        self.day in self.un_even_day_months
                        and self.month >= 1
                        and self.month <= 31
                    )
                    or (
                        self.day in self.even_day_months
                        and self.month >= 1
                        and self.month <= 30
                    )
                    or (
                        self.day in self.leap_day_months
                        and self.month >= 1
                        and self.month <= 28
                    )
                ):
                    t_month = self.month
                    self.month = self.day
                    self.day = t_month
                else:
                    self.month = None
            else:
                self.month = None
        pass

    # end _check_day_and_month_swap

    def _fix_century(self):
        '''Description'''
        if len(str(self.year)) < 4:
            # d_fmt = int( datetime.datetime.now().strftime( '%y' ))
            if (
                self.year > int(datetime.datetime.now().strftime('%y'))
                and self.month > 0
                and self.day > 0
            ):
                self.year = self.year + 1900
            else:
                self.year = self.year + 2000
        pass

    # end _fix_century

    def _fix_type_errors(self):
        '''Description'''
        try:
            self.year = int(self.year)
            try:
                self.month = int(self.month)
                try:
                    self.day = int(self.day)
                    success = True
                except ValueError:
                    success = False
            except ValueError:
                success = False
        except ValueError:
            success = False
        return success

    # end _fix_type_errors

    def _get_components(self):
        '''Description'''

        def insert_seperators():
            '''Description'''
            if len(self.in_date_str) == 6:
                self.in_date_str = self.in_date_str[:2] + '/' + self.in_date_str[2:]
                self.in_date_str = self.in_date_str[:5] + '/' + self.in_date_str[5:]
            elif len(self.in_date_str) == 8:
                if self.comp_pos_year == 0:
                    self.in_date_str = self.in_date_str[:4] + '/' + self.in_date_str[4:]
                    self.in_date_str = self.in_date_str[:7] + '/' + self.in_date_str[7:]
                elif self.comp_pos_year == 2:
                    self.in_date_str = self.in_date_str[:2] + '/' + self.in_date_str[2:]
                    self.in_date_str = self.in_date_str[:5] + '/' + self.in_date_str[5:]
                elif self.comp_pos_year == 1:
                    self.in_date_str = self.in_date_str[:2] + '/' + self.in_date_str[2:]
                    self.in_date_str = self.in_date_str[:7] + '/' + self.in_date_str[7:]
            pass

        # end insert_seperators

        def swap_year_and_day():
            '''Description'''
            tmp = self.comp_pos_day
            self.comp_pos_day = self.comp_pos_year
            self.comp_pos_year = tmp
            pass

        # end swap_year_and_day

        self.in_date_str = self.in_date_str.strip()
        success = False
        components = False
        if self.in_date_str.isnumeric():
            insert_seperators()
        if self.in_date_str:
            for sep in self.seperators:
                self.in_date_str = self.in_date_str.replace(sep, '/')
            components = self.in_date_str.split('/')
            if len(components) == 3:
                success = True
                if components[self.comp_pos_month].upper() in self.month_dict:
                    if self.in_format == 'YMD':
                        self.in_format = 'DMY'
                        swap_year_and_day()
                    components[self.comp_pos_month] = self.month_dict[
                        components[self.comp_pos_month].upper()
                    ]
                    success = True
                if len(components[self.comp_pos_day]) == 4:
                    swap_year_and_day()
            if success:
                self.day = components[self.comp_pos_day]
                self.month = components[self.comp_pos_month]
                self.year = components[self.comp_pos_year]
        return success

    # end _get_components

    def _get_comp_pos(self):
        '''Description'''
        self.comp_pos_day = self.in_format.upper().find('D')
        self.comp_pos_month = self.in_format.upper().find('M')
        self.comp_pos_year = self.in_format.upper().find('Y')
        pass

    # end _get_comp_pos

    def _is_leap_year(self):
        '''Description'''
        if self.year % 4 == 0 and self.year % 100 != 0:
            if self.year % 400 == 0:
                return True
        elif self.year % 4 != 0:
            return False

    # end _is_leap_year

    def _set_day_to_one(self):
        '''Description'''
        if self.day < 1:
            self.day = 1
        elif self.month in self.un_even_day_months and self.day > 31:
            self.day = 31
        elif self.month in self.even_day_months and self.day > 30:
            self.day = 30
        elif self.month in self.leap_day_months:
            if self._is_leap_year():
                if self.day > 29:
                    self.day = 28
            else:
                if self.day > 28:
                    self.day = 28
        pass

    # end _set_day_to_one


# end FixDate


def do_tests(p_app_path='', p_cls=True):
    '''Test the class methods.  Also called by the PackageIt PIP app to
    test the module during PIP installation.

    Parameters
    - baseFolder    : Base folder for source code
    - cls = True    : Clear the screen at start-up
    '''

    def basic_test(p_app_path=p_app_path):
        '''Basic and mandatory scenario tests for certification of the class'''
        success = True
        # Below must be implimented.  Abandoned due to time pressure
        # date = FixDate( _name, '21MAY17', p_in_format = 'DMY' )
        # if date.date != datetime.date( 2021, 5, 17 ):
        #     success = success and False
        date = FixDate(_name, '  .  .  ', p_in_format='DMY')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '.  .', p_in_format='DMY')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '11.10.03', p_in_format='DMY')
        if date.date != datetime.date(2003, 10, 11):
            success = success and False
        date = FixDate(_name, '11.10.68', p_in_format='DMY')
        if date.date != datetime.date(1968, 10, 11):
            success = success and False
        date = FixDate(_name, '68.10.11', p_in_format='YMD')
        if date.date != datetime.date(1968, 10, 11):
            success = success and False
        date = FixDate(_name, '10.11.68', p_in_format='MDY')
        if date.date != datetime.date(1968, 10, 11):
            success = success and False
        date = FixDate(_name, '073 339 5214')
        if date.date_str is not None and date.date is not None:
            success = success and False
        date = FixDate(_name, '19681011')
        if date.date != datetime.date(1968, 10, 11):
            success = success and False
        date = FixDate(_name, '1968/10/11')
        if date.date != datetime.date(1968, 10, 11):
            success = success and False
        date = FixDate(_name, '4/9/1996')
        if date.date != datetime.date(1996, 9, 4):
            success = success and False
        date = FixDate(_name, '2001/9/8')
        if date.date != datetime.date(2001, 9, 8):
            success = success and False
        date = FixDate(_name, '5/10/1976')
        if date.date != datetime.date(1976, 10, 5):
            success = success and False
        date = FixDate(_name, '2000/4/21')
        if date.date != datetime.date(2000, 4, 21):
            success = success and False
        date = FixDate(_name, '1968/10/1')
        if date.date != datetime.date(1968, 10, 1):
            success = success and False
        date = FixDate(_name, '20-Oct-1968')
        if date.date != datetime.date(1968, 10, 20):
            success = success and False
        date = FixDate(_name, '20-Oct-68')
        if date.date != datetime.date(1968, 10, 20):
            success = success and False
        date = FixDate(_name, '20/10/1968')
        if date.date != datetime.date(1968, 10, 20):
            success = success and False
        date = FixDate(_name, '00/00/00')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '00-00-00')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '2017-01-0I')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '2017-02-30')
        if date.date != datetime.date(2017, 2, 28):
            success = success and False
        date = FixDate(_name, '')
        if date.date is not None:
            success = success and False
        date = FixDate(_name, '2017-20-10')
        if date.date != datetime.date(2017, 10, 20):
            success = success and False
        date = FixDate(_name, '2017.20.10')
        if date.date != datetime.date(2017, 10, 20):
            success = success and False
        date = FixDate(_name, '20.10.2017')
        if date.date != datetime.date(2017, 10, 20):
            success = success and False
        date = FixDate(_name, '10.20.2017')
        if date.date != datetime.date(2017, 10, 20):
            success = success and False
        date = FixDate(_name, '1900/00/00')
        if date.date is not None:
            success = success and False
        beetools.result_rep(success, 'Done')
        return success

    # end basic_test

    success = True
    b_tls = beetools.Archiver(
        _name, _VERSION, __doc__[0], p_app_path=p_app_path, p_cls=p_cls
    )
    logger = logging.getLogger(_name)
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
        return b_tls.archive_path
    return False


# end do_tests

if __name__ == '__main__':
    do_tests(p_app_path=_path)
# end __main__
