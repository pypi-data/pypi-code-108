from nehushtan.mail.IMAPAgent import IMAPAgent
from tests.config import IMAP_CONFIG

status_name_array = (
    IMAPAgent.STATUS_NAME_MESSAGES,
    IMAPAgent.STATUS_NAME_RECENT,
    IMAPAgent.STATUS_NAME_UIDNEXT,
    IMAPAgent.STATUS_NAME_UIDVALIDITY,
    IMAPAgent.STATUS_NAME_UNSEEN,
)

imap_agent = IMAPAgent(IMAP_CONFIG['imap_server'], IMAP_CONFIG['imap_port'], True)
imap_agent.login(IMAP_CONFIG['username'], IMAP_CONFIG['password'])
boxes = imap_agent.list_mail_boxes()
for box in boxes:
    box_tuple = IMAPAgent.parse_box_string_to_tuple(box)
    # print(box,box_tuple)

    box_name = box_tuple[2]

    status = imap_agent.show_status(box_name, status_name_array)
    print('Box Status: ', status)

data = imap_agent.select_mailbox('INBOX')
print(f'Total Mails: {data}')

message_id_array = imap_agent.search_mails_for_message_id('ALL')
print(message_id_array)

for message_id in message_id_array:
    print(f"MESSAGE [{message_id}]")
    nem = imap_agent.fetch_mail_with_message_id_as_nem(message_id)
    print(f'\tOn {nem.read_field_date()}')
    print(f'\tFrom {nem.read_field_from()} To {nem.read_field_to()}')
    print(f'\tSubject {nem.read_field_subject()}')

imap_agent.logout()
