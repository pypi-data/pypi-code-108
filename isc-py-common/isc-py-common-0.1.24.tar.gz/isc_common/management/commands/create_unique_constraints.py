import logging

from django.core.management import BaseCommand

from code_generator.core.writer import qutes_str, int_2_bin_str, reverse_str, fill_ch

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Создание уникальных ограничителей с учетом null столбцов"

    # constraints = [
    #     UniqueConstraint(fields=['STMP_2', 'props'], condition=Q(STMP_1=None) | Q(version=None), name='Item_unique_1'),
    #     UniqueConstraint(fields=['STMP_1', 'props'], condition=Q(STMP_2=None) | Q(version=None), name='Item_unique_2'),
    #     UniqueConstraint(fields=['STMP_2', 'version', 'props'], condition=Q(STMP_1=None), name='Item_unique_3'),
    #     UniqueConstraint(fields=['STMP_1', 'version', 'props'], condition=Q(STMP_2=None), name='Item_unique_4'),
    #     UniqueConstraint(fields=['STMP_1', 'STMP_2', 'props'], condition=Q(version=None), name='Item_unique_5'),
    #     UniqueConstraint(fields=['STMP_1', 'STMP_2', 'version', 'props'], name='Item_unique_6'),
    # ]

    def add_arguments(self, parser):
        parser.add_argument('--table', type=str)
        parser.add_argument('--columns', type=str)

    def handle(self, *args, **options):
        table = options.get('table')
        columns = options.get('columns')

        _columns = columns.split(',')
        not_null_column = []
        null_column = []
        constraints = []

        for column in _columns:
            _column = column.split('=')
            if len(_column) > 1 and _column[1] == 'null':
                null_column.append(_column[0].strip())
            else:
                not_null_column.append(qutes_str(_column[0].strip()))

        for i in range(0, 2 ** len(null_column)):
            condition = []
            b = reverse_str(int_2_bin_str(i, len(null_column)))
            idx = 0
            cl_null_column = []
            cl_not_null_column = sorted(not_null_column.copy())
            for _b in b:
                if _b == '1':
                    cl_not_null_column.append(qutes_str(null_column[idx]))
                else:
                    cl_null_column.append(null_column[idx])
                idx += 1

            for _null_column in cl_null_column:
                condition.append(f'Q({_null_column}=None)')

            not_null_column_str = ', '.join(sorted(cl_not_null_column))
            condition_str = ' & '.join(sorted(condition))
            if not condition_str:
                uconstraint = fill_ch(f'''UniqueConstraint(fields=[{not_null_column_str}], name='{table}_unique_constraint_{i}'),\n''', 4, ' ')
            else:
                uconstraint = fill_ch(f'''UniqueConstraint(fields=[{not_null_column_str}], condition={condition_str}, name='{table}_unique_constraint_{i}'),\n''', 4, ' ')
            constraints.append(uconstraint)
        res = f'''constraints = [\n{''.join(constraints)}]'''
        print(res)
