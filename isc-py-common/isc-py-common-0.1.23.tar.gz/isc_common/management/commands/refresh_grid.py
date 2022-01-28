import logging

from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # record = {'id': 135, 'code': '2020 / 07 / 1', 'name': None, 'date': datetime.datetime(2020, 7, 17, 11, 53, 8), 'description': None, 'parent_id': None, 'demand_id': None, 'demand__code': None, 'demand__date': None, 'item_id': None, 'parent_item_id': None, 'item__STMP_1_id': None, 'item__STMP_1__value_str': None, 'item__STMP_2_id': None, 'item__STMP_2__value_str': None, 'status_id': 7, 'status__code': 'in_production', 'status__name': 'Сформированы заказы на производство', 'qty': '', 'qty_made': 0, 'value_made': 100, 'value_sum': 100, 'isFolder': True, 'priority': '', 'editing': True, 'deliting': True}
        # WebSocket.row_refresh_grid(settings.GRID_CONSTANTS.refresh_production_launch_grid_row, record)

        record = {
            "id": 137,
            "code": "Тест 04/1",
            "date": "2020-07-17T11:53:08.000",
            "parent_id": 135,
            "demand_id": 85,
            "demand__code": "Тест 04",
            "demand__date": "2020-06-30T00:00:00.000",
            "item_id": 3542260,
            "parent_item_id": 3542258,
            "item__STMP_1_id": 1260666,
            "item__STMP_1__value_str": "Кузов- фургон",
            "item__STMP_2_id": 1978836,
            "item__STMP_2__value_str": "ТЕСТ 2",
            "status_id": 4,
            "status__code": "in_production",
            "status__name": "Сформированы заказы на производство",
            "qty": "2",
            "qty_made": 0,
            "value_sum": "418.0000",
            "isFolder": False,
            "priority": 0,
            "editing": True,
            "deliting": True,
        }
        Launches_viewManager.refreshRows(ids=record.get('id'))
