import logging

from investing_algorithm_framework import OrderExecutor, Order, OrderStatus
from investing_algorithm_framework.core import OperationalException
from eltyer import Client, ClientException
from eltyer_investing_algorithm_framework.configuration import constants

logger = logging.getLogger(__name__)


class EltyerOrderExecutor(OrderExecutor):
    identifier = "ELTYER"

    def execute_limit_order(self, order: Order, algorithm_context,
                            **kwargs) -> bool:
        client: Client = algorithm_context.config[constants.ELTYER_CLIENT]
        try:

            try:
                eltyer_order = client.create_limit_order(
                    target_symbol=order.get_target_symbol(),
                    amount=order.get_amount_target_symbol(),
                    side=order.get_side(),
                    price=order.get_initial_price()
                )
                order.set_order_reference(eltyer_order.order_reference)
            except ClientException as e:
                logger.error(e)
                raise OperationalException(e)

            return True
        except ClientException as e:
            logger.exception(e)
            return False

    def execute_market_order(self, order: Order, algorithm_context,
                             **kwargs) -> bool:
        client: Client = algorithm_context.config[constants.ELTYER_CLIENT]

        try:
            eltyer_order = client.create_market_order(
                order.get_target_symbol(), order.get_amount_target_symbol()
            )
            order.order_reference = eltyer_order.id
            return True
        except ClientException as e:
            logger.exception(e)
            return False

    def get_order_status(self, order: Order, algorithm_context,
                         **kwargs) -> OrderStatus:
        client: Client = algorithm_context.config[constants.ELTYER_CLIENT]

        try:
            order = client.get_order(reference_id=order.get_order_reference())
            return OrderStatus.from_string(order.status)
        except ClientException as e:
            logger.error(e)
            raise OperationalException(
                "Could not get order status from eltyer"
            )
