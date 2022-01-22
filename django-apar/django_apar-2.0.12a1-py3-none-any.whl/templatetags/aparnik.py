from django import template
from django.core.validators import URLValidator

from aparnik.settings import Setting

register = template.Library()


@register.simple_tag()
def site_name_persian():
    title = Setting.objects.get(key='PROJECT_NAME').get_value()
    return title


@register.simple_tag()
def project_description():
    description = Setting.objects.get(key='PROJECT_DESCRIPTION').get_value()
    return description


@register.simple_tag()
def logo():
    logo = Setting.objects.get(key='LOGO_PROJECT_ICON').get_value()
    return logo


@register.simple_tag(takes_context=True)
def applications_download_list(context):
    def get_script(is_iran, link):
        if not is_iran:
            return '''
            alert("دسترسی تنها از ایران مقدور است. لطفا وی پی ان خود را خاموش بفرمایید.");
            '''
        else:
            return '''window.open("''' + link + '''", "myWin", "scrollbars=yes,width=400,height=650");'''
    #
    # import geoip2.database
    # reader = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-Country.mmdb')
    # response = reader.country(context['request'].META.get('REMOTE_ADDR'))
    # is_iran = response.country.iso_code.upper() == 'IR'
    is_iran = True

    APPSTORE_LINK = [
        'ios',
        '''window.open("''' + Setting.objects.get(key='APPSTORE_LINK').get_value() + '''", "myWin",
                            "scrollbars=yes,width=400,height=650");self.close()''',
        Setting.objects.get(key='APPSTORE_LINK'),

    ]
    IOS_LINK = [
        'ios',
        get_script(is_iran, Setting.objects.get(key='IOS_LINK').get_value()),
        Setting.objects.get(key='IOS_LINK')
    ]
    GOOGLE_PLAY_LINK = [
        'googleplay',
        '''window.open("''' + Setting.objects.get(key='GOOGLE_PLAY_LINK').get_value() + '''", "myWin",
                    "scrollbars=yes,width=400,height=650");''',
        Setting.objects.get(key='GOOGLE_PLAY_LINK')
    ]
    ANDROID_LINK = [
        'android',
        '''window.open("''' + Setting.objects.get(key='ANDROID_LINK').get_value() + '''", "myWin",
                        "scrollbars=yes,width=400,height=650");''',
        Setting.objects.get(key='ANDROID_LINK')
    ]

    validator = URLValidator()

    apdl = []
    for value in [APPSTORE_LINK, IOS_LINK, GOOGLE_PLAY_LINK, ANDROID_LINK]:
        try:
            # check validation url if not valid raise it happen
            validator(value[2].get_value())
            if value[2].get_value() != '':
                apdl.append({
                    'class': value[0],
                    'js': value[1]
                })
        except:
            pass

    return apdl


@register.simple_tag()
def application_image():
    return Setting.objects.get(key='APPLICATION_IMAGE').get_value()


@register.simple_tag()
def application_identifier():
    return Setting.objects.get(key='IDENTIFIER').get_value()
