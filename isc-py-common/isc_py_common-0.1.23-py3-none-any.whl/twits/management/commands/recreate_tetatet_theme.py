import logging

from django.core.management import BaseCommand
from django.db import connections, connection, transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute('update twits_chat_user_user set common_id = 0')

            with connection.cursor() as cursor:
                cursor.execute('''select
                                        user_reciver_id
                                    from
                                        twits_chat_user_user
                                    group by
                                        user_reciver_id
                                    order by user_reciver_id''')
                user_recivers = cursor.fetchall()
                for user_reciver in user_recivers:
                    # print(user_reciver[0])
                    user_reciver_id = user_reciver[0]
                    cursor.execute("select id, user_sender_id from twits_chat_user_user  where user_reciver_id = %s order by user_sender_id", [user_reciver[0]])
                    user_senders = cursor.fetchall()

                    for user_sender in user_senders:
                        # print(f'   {user_sender}')

                        from twits.models.chat_user_user import Chat_user_userManager
                        common_id = Chat_user_userManager.get_next_common_id()
                        id = user_sender[0]
                        user_sender_id = user_sender[1]

                        cursor.execute("select id from twits_chat_user_user  where user_reciver_id = %s and user_sender_id=%s", [user_sender_id, user_reciver_id])
                        rev_user_senders = cursor.fetchall()

                        for rev_user_sender in rev_user_senders:
                            # print(f'       {rev_user_sender}')
                            rev_id = rev_user_sender[0]

                            cursor.execute("update twits_chat_user_user set common_id = %s where id = %s", [common_id, rev_id])
                        cursor.execute("update twits_chat_user_user set common_id = %s where id = %s", [common_id, id])

                cursor.execute("delete from twits_chat_user_user_theme where chat_user_user_id in (select id from twits_chat_user_user where common_id = 0)")
                cursor.execute("delete from twits_chat_user_user where common_id = 0")

        print('Recreate_tetatet_theme done.')
