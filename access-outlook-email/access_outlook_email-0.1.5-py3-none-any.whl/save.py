"""
Created on 30.04.2021
This script can save email attachments into one specific directory and rename the file.
@author: baier
"""

import os
from exchangelib import Message, FileAttachment, ItemAttachment


# Read & Save Attachments code
def save_attachment(exchange_folder_name: str, save_to_folder: str, account_var, suffix=0,
                    prename='', last_items=1) -> str:
    folder = account_var.inbox / exchange_folder_name
    for item in folder.all().order_by('-datetime_received')[:last_items]:
        for attachment in item.attachments:
            print('Number of Attachment found:', len(item.attachments))
            if isinstance(attachment, FileAttachment):
                local_path = os.path.join(save_to_folder, prename + attachment.name[suffix:])
                with open(local_path, 'wb') as f:
                    f.write(attachment.content)
                print('Saved attachment to', local_path)
                return local_path
            elif isinstance(attachment, ItemAttachment):
                if isinstance(attachment.item, Message):
                    print(attachment.item.subject, attachment.item.body)
