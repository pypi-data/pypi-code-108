from django.contrib import admin

from .models import ReceiverEmailConfiguration, SenderEmailConfiguration, \
    EmailConfiguration


@admin.register(ReceiverEmailConfiguration)
class ReceiverEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('email_address',)


@admin.register(SenderEmailConfiguration)
class SenderEmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('sender_email_address',)


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ('Subject',
                    'Email_Content',
                    'Signature',
                    'Email_Us',
                    'FAQ_URL',
                    'Unsubscribe_Email_ID',
                    'Logs_Type',
                    'HTML_File',
                    )
