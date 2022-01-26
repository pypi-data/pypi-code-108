from edc_action_item.site_action_items import site_action_items
from edc_ltfu.action_items import LtfuAction as BaseLossToFollowupAction
from edc_ltfu.utils import get_ltfu_model_name
from edc_offstudy.action_items import EndOfStudyAction as BaseEndOfStudyAction
from edc_protocol_violation.action_items import (
    ProtocolDeviationViolationAction as BaseProtocolDeviationViolationAction,
)


class EndOfStudyAction(BaseEndOfStudyAction):

    reference_model = "mocca_prn.endofstudy"
    admin_site_name = "mocca_prn_admin"


class LossToFollowupAction(BaseLossToFollowupAction):

    reference_model = get_ltfu_model_name()
    admin_site_name = "mocca_prn_admin"


class ProtocolDeviationViolationAction(BaseProtocolDeviationViolationAction):
    reference_model = "mocca_prn.protocoldeviationviolation"
    admin_site_name = "mocca_prn_admin"


site_action_items.register(EndOfStudyAction)
site_action_items.register(LossToFollowupAction)
site_action_items.register(ProtocolDeviationViolationAction)
