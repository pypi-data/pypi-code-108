# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
try:
    from yangsuite.apps import YSAppConfig
except:
    from django.apps import AppConfig as YSAppConfig


class YSFileManagerConfig(YSAppConfig):
    # Python module name (mandatory)
    name = 'ysfilemanager'

    # Prefix under which to include this module's URLs
    url_prefix = 'filemanager'

    # Human-readable label
    verbose_name = (
        "Provides quick, low-overhead parsing of YANG"
        ' (<a href="https://tools.ietf.org/html/rfc6020">RFC 6020</a>,'
        ' <a href="https://tools.ietf.org/html/rfc7950">RFC 7950</a>) models'
        " and identification of their interdependencies."
        " Manages YANG file repositories and sets of YANG files within these"
        " repositories."
        " Provides UI and APIs for file upload to YANG Suite."
    )

    # Menu items {'menu': [(text, relative_url), ...], ...}
    menus = {
        'Setup': [
            ('YANG files and repositories', 'repository/manage/'),
            ('YANG module sets', 'yangsets/manage/'),
        ],
    }

    help_pages = [
        ('Constructing and populating a YANG module repository',
         'create_repository.html'),
        ('Uploading YANG files from the local filesystem',
         'upload_schemas.html'),
        ('Downloading YANG files from a device via NETCONF',
         'download_schemas.html'),
        ('Copying YANG files from a server via SCP',
         'scp_schemas.html'),
        ('Importing YANG files from a Git repository',
         'git_schemas.html'),
        ('Defining a YANG module set',
         'define_yangset.html'),
    ]
