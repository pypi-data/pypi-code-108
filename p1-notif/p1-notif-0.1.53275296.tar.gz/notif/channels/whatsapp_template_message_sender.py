from .abstract_channel import AbstractChannel


class WhatsappTemplateMessageSender(AbstractChannel):

    def __init__(self, phone_number, template_id, wa_params, name):
        self.set_phone_number(phone_number)
        self.set_template_id(template_id)
        self.set_wa_params(wa_params)
        self.set_name(name)

    def set_phone_number(self, phone_number):
        self.phone_number = phone_number
    
    def set_template_id(self, template_id):
        self.template_id = template_id

    def set_wa_params(self, wa_params):
        self.wa_params = wa_params
    
    def set_name(self, name):
        self.name = name

    def notif_type(self):
        return 'SEND_TEMPLATE_MESSAGE'

    def json(self):
        return {
            'phone_number': self.phone_number,
            'template_id': self.template_id,
            'wa_params': self.wa_params,
            'name': self.name
        }

    def attachments(self):
        return []
