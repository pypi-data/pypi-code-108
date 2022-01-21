from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False  # Needed because the index is added concurrently

    dependencies = [
        ('ingress', '0009_auto_20210315_1454'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='failedmessage',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True, db_index=True),
                )
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        CREATE INDEX CONCURRENTLY ingress_failedmessage_created_at_5de47ca9
                        ON ingress_failedmessage (created_at);
                    """,
                    reverse_sql="""
                        DROP INDEX ingress_failedmessage_created_at_5de47ca9;
                    """,
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="message",
                    name="created_at",
                    field=models.DateTimeField(auto_now_add=True, db_index=True),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        CREATE INDEX CONCURRENTLY ingress_message_collection_id_c83e46bd
                        ON ingress_message (collection_id);
                    """,
                    reverse_sql="""
                        DROP INDEX ingress_message_collection_id_c83e46bd;
                    """,
                ),
            ],
        ),
    ]
