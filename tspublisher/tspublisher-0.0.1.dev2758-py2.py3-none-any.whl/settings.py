from __future__ import absolute_import, division, print_function, unicode_literals

import os
import platform

GIT_DIRECTORY = os.path.expanduser("~/git")
PROCEDURE_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-procedures")
CHANNELS_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-channels")
CHANNELS_ASSET_DIRECTORY = os.path.expanduser("~/git/content-channels/assets")
TRANSLATIONS_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-translations")

STUDIO_GIT_PATH = 'studio-git.touchsurgery.com'
PROCEDURE_REPOSITORY = '{0}:/srv/git/procedure-repo'.format(STUDIO_GIT_PATH)
CHANNELS_REPOSITORY = '{0}:/srv/git/channel-repo'.format(STUDIO_GIT_PATH)
TRANSLATIONS_REPOSITORY = '{0}:/srv/git/translation-repo'.format(STUDIO_GIT_PATH)

TEMPLATE_DIRECTORY = os.path.join(os.path.dirname(__file__), "template_files")

SSH_DIRECTORY_PATH = os.path.expanduser('~/.ssh')
SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
RSA_PUBLIC_KEY_PATH = os.path.expanduser('~/.ssh/touchsurgery_publisher_rsa.pub')
RSA_PRIVATE_KEY_PATH = os.path.expanduser('~/.ssh/touchsurgery_publisher_rsa')

if platform.system() == "Windows":
    BASE_DATA_DIR = "Z:\\"
else:
    BASE_DATA_DIR = os.path.join("/Volumes", "content")

PRODUCTION_INFO_DIR = os.path.join(BASE_DATA_DIR, "productionInfo")
PRODUCTION_INFO_BACKUP_DIR = os.path.expanduser("~/git/production-info")
CHANNELS_INFO_DIR = CHANNELS_CHECKOUT_DIRECTORY

CONTENT_DB_DIR = os.path.join(BASE_DATA_DIR, "assetdb", ".db", "contentdb.sqlite3")

ORIGINAL_CONTENT_ROOT = "Z:/assetdb"
ORIGINAL_CONTENT_ROOT_OLD = "C:/TouchSurgery/assetdb"

if platform.system() == "Windows":
    REPLACEMENT_CONTENT_ROOT = "Z:/assetdb"
else:
    REPLACEMENT_CONTENT_ROOT = "/Volumes/content/assetdb"

CG_APP5_ROOT = os.path.join(BASE_DATA_DIR, "delivery", "app5")
VBS_ROOT = os.path.join(BASE_DATA_DIR, "delivery", "vbs")

LOCALE_DIRECTORIES = {
    'en': 'en',
    'es': 'es',
    'pt': 'pt',
    'ru': 'ru',
    'zh-hans': 'hans',
    'zh-hant': 'hant',
    'ja': 'ja'
}

CHANNEL_TYPES = ['touchsurgery', 'institution', 'company']
DEFAULT_SCALE = "scale='768:1024'"  # fix frame-popping in app5. 680:1024 previously
ASSET_NAME_PREFIX = 'channel-'
REPORT_SCRIPT = os.path.join(os.path.dirname(__file__), "studio-report", "src", "main.js")
REPORT_FOLDER = os.path.join(os.path.dirname(__file__), "studio-report")
REPORT_ENDPOINT = 'https://www.touchsurgery.com/pdf-templating/new'
