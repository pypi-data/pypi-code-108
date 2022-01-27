# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codex',
 'codex._vendor',
 'codex._vendor.haystack',
 'codex._vendor.haystack.backends',
 'codex._vendor.haystack.management',
 'codex._vendor.haystack.management.commands',
 'codex._vendor.haystack.templatetags',
 'codex._vendor.haystack.utils',
 'codex.librarian',
 'codex.librarian.covers',
 'codex.librarian.db',
 'codex.librarian.janitor',
 'codex.librarian.watchdog',
 'codex.migrations',
 'codex.serializers',
 'codex.settings',
 'codex.views',
 'tests']

package_data = \
{'': ['*'],
 'codex': ['static_root/*',
           'static_root/admin/css/*',
           'static_root/admin/css/vendor/select2/*',
           'static_root/admin/fonts/*',
           'static_root/admin/img/*',
           'static_root/admin/img/gis/*',
           'static_root/admin/js/*',
           'static_root/admin/js/admin/*',
           'static_root/admin/js/vendor/jquery/*',
           'static_root/admin/js/vendor/select2/*',
           'static_root/admin/js/vendor/select2/i18n/*',
           'static_root/admin/js/vendor/xregexp/*',
           'static_root/css/*',
           'static_root/fonts/*',
           'static_root/img/*',
           'static_root/js/*',
           'static_root/rest_framework/css/*',
           'static_root/rest_framework/docs/css/*',
           'static_root/rest_framework/docs/img/*',
           'static_root/rest_framework/docs/js/*',
           'static_root/rest_framework/fonts/*',
           'static_root/rest_framework/img/*',
           'static_root/rest_framework/js/*',
           'templates/*',
           'templates/admin/*',
           'templates/admin/codex/adminflag/*',
           'templates/admin/codex/failedimport/*',
           'templates/admin/codex/library/*',
           'templates/admin/codex/queuejob/*',
           'templates/search/indexes/codex/*'],
 'codex._vendor.haystack': ['templates/panels/*',
                            'templates/search_configuration/*']}

install_requires = \
['Pillow>=9.0,<10.0',
 'ansicolors>=1.1,<2.0',
 'comicbox>=0.2.2,<0.3.0',
 'django-cors-headers>=3.2,<4.0',
 'django-dark>=0.1,<0.2',
 'django>=4.0,<5.0',
 'djangorestframework>=3.11,<4.0',
 'fnvhash>=0.1,<0.2',
 'humanfriendly>=10.0,<11.0',
 'humanize>=3.12.0,<4.0.0',
 'hypercorn[h3]>=0.13.0,<0.14.0',
 'pycountry>=22.1,<23.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.24,<3.0',
 'simplejson>=3.17,<4.0',
 'stringcase>=1.2,<2.0',
 'tzlocal>=4.1,<5.0',
 'watchdog>=2.0,<3.0',
 'websocket_client>=1.2,<2.0',
 'whitenoise[brotli]>=5.2,<6.0',
 'xapian-bindings>=0.1.0,<0.2.0',
 'xapian-haystack>=3.0.1,<4.0.0']

entry_points = \
{'console_scripts': ['codex = codex.run:main']}

setup_kwargs = {
    'name': 'codex',
    'version': '0.8.0rc2',
    'description': 'A comic archive web server.',
    'long_description': '# Codex\n\nCodex is a comic archive browser and reader.\n\n## <a name="features">✨ Features</a>\n\n- Codex is a web server, not a desktop or mobile app.\n- Full text search of metadata and bookmarks.\n- Filter and sort on all comic metadata and unread status per user.\n- Browse a tree of publishers, imprints, series, volumes, or your\n  own folder hierarchy.\n- Read comics in a variety of aspect ratios that fit your screen.\n- Per user bookmarking. You get per browser bookmarks even before you make an account.\n- Watches the filesystem and automatically imports new or changed comics.\n\n## <a name="demonstration">👀 Demonstration</a>\n\nYou may browse a [live demo server](https://codex.sl8r.net/) to get a feel for Codex.\n\n## <a name="news">📰 News</a>\n\nCodex has a <a href="NEWS.md">NEWS file</a> to summarize changes that affect users.\n\n## <a name="installation">📦 Installation</a>\n\n### Install & Run with Docker\n\nRun the official [Docker Image](https://hub.docker.com/r/ajslater/codex). Instructions for running the docker image are on the Docker Hub README. This is the recommended way to run Codex.\n\nYou\'ll then want to read the [Administration](#administration) section of this document.\n\n### Install & Run as a Native Application\n\nYou can also run Codex as a natively installed python application with pip.\n\n#### Wheel Build Dependencies\n\nYou\'ll need to install these system dependencies before installing Codex.\n\n##### macOS\n\n```sh\nbrew install jpeg libffi libyaml libzip openssl python unrar xapian\n```\n\n##### Linux\n\n###### Debian based (e.g. Ubuntu)\n\n```sh\napt install build-essential libffi-dev libjpeg-dev libssl-dev libxapian30 libyaml-dev python3-pip python3-xapian zlib1g-dev\n```\n\n###### Alpine\n\n```sh\napk add bsd-compat-headers build-base jpeg-dev libffi-dev openssl-dev xapian-bindings-python3 xapian-core yaml-dev zlib-dev\n```\n\n##### Install unrar Runtime Dependency on Linux\n\nCodex requires unrar to read cbr formatted comic archives. Unrar is rarely packaged for Linux, but here are some instructions: [How to install unrar in Linux](https://www.unixtutorial.org/how-to-install-unrar-in-linux/)\n\n#### Install Codex with pip\n\nYou may now install Codex with pip\n\n```sh\npip3 install codex\n```\n\n#### Run Codex Natively\n\npip should install the codex binary on your path. Run\n\n```sh\ncodex\n```\n\nand then navigate to <http://localhost:9810/>\n\n## <a name="administration">👑 Administration</a>\n\n### Change the Admin password\n\nThe first thing you should do is log in as the admin user and change the admin password.\n\n#### Navigate to the Admin Panel\n\n- Click the hamburger menu ☰ to open the browser settings drawer.\n- Log in as the \'admin\' user. The default administator password is also \'admin\'.\n- Navigate to the Admin Panel by clicking on its link in the browser settings drawer after you have logged in.\n\n##### In the Admin Panel, Change the Password\n\n- Navigate to the AUTHENTICATION AND AUTHORIZATION Users panel.\n- Select the `admin` user.\n- Change the admin password using the small "this form" link in the password section.\n- You may also change the admin user\'s name or anything else.\n- You may grant other users admin privileges by making them staff.\n\n### Adding Comic Libraries\n\nThe second thing you will want to do is log in as an Administrator and add one or more comic libraries.\n\n#### From the Admin Panel, Add Comic Libraries\n\n- Navigate to the CODEX Libraries Panel in the Admin Panel\n- Add a Library with the "ADD LIBRARY +" button in the upper right.\n\n### Reset the admin password\n\nIf you forget all your superuser passwords, you may restore the original default admin account by running codex with the `CODEX_RESET_ADMIN` environment variable set.\n\n```sh\nCODEX_RESET_ADMIN=1 codex\n```\n\nor, if using Docker:\n\n```sh\ndocker run -e CODEX_RESET_ADMIN=1 -v <host path to config>/config:/config ajslater/codex\n```\n\n## <a name="configuration">⚙️ Configuration</a>\n\n### Config Dir\n\nThe default config directory is named `config/` directly under the working directory you run codex from. You may specify an alternate config directory with the environment variable `CODEX_CONFIG_DIR`.\n\nThe config directory contains a file named `hypercorn.toml` where you can specify ports and bind addresses. If no `hypercorn.toml` is present a default one is copied to that directory on startup.\n\nThe default values for the config options are:\n\n```toml\nbind = ["0.0.0.0:9810"]\nquick_bind = ["0.0.0.0:9810"]\nroot_path = "/codex"\nmax_db_ops = 100000\n\n```\n\nThe config directory also holds the main sqlite database, the Xapian search index, a Django cache and comic book cover thumbnails generated when comics are imported.\n\n### Environment Variables\n\n- `LOGLEVEL` will change how verbose codex\'s logging is. Valid values are `ERROR`, `WARNING`, `INFO`, `VERBOSE`, `DEBUG`. The default is `INFO`.\n- `TIMEZONE` or `TZ` will explicitly the timezone in long format (e.g. `"America/Los Angeles"`). This is mostly useful inside Docker because codex cannot automatically detect the host machine\'s timezone.\n- `CODEX_CONFIG_DIR` will set the path to codex config directory. Defaults to `$CWD/config`\n- `CODEX_RESET_ADMIN=1` will reset the admin user and its password to defaults when codex starts.\n- `CODEX_SKIP_INTEGRITY_CHECK` will skip the database integrity repair that runs when codex starts.\n\n### Reverse Proxy\n\n[nginx](https://nginx.org/) is often used as a TLS terminator and subpath proxy.\n\nHere\'s an example nginx config with a subpath named \'/codex\'.\n\n```nginx\n    # HTTP\n    proxy_set_header  Host              $http_host;\n    proxy_set_header  X-Forwarded-For   $proxy_add_x_forwarded_for;\n    proxy_set_header  X-Forwarded-Host  $server_name;\n    proxy_set_header  X-Forwarded-Port  $server_port;\n    proxy_set_header  X-Forwarded-Proto $scheme;\n    proxy_set_header  X-Real-IP         $remote_addr;\n    proxy_set_header  X-Scheme          $scheme;\n\n    # Websockets\n    proxy_http_version 1.1;\n    proxy_set_header Upgrade $http_upgrade;\n    proxy_set_header Connection "Upgrade"\n\n    # This example uses a docker container named \'codex\' at sub-path /codex\n    # Use a valid IP or resolvable host name for other configurations.\n    location /codex {\n        proxy_pass  http://codex:9810;\n    }\n```\n\nSpecify a reverse proxy sub path (if you have one) in `config/hypercorn.toml`\n\n```toml\nroot_path = "/codex"\n\n```\n\n#### Nginx Reverse Proxy 502 when container refreshes\n\nNginx requires a special trick to refresh dns when linked Docker containers\nrecreate. See this [nginx with dynamix upstreams](https://tenzer.dk/nginx-with-dynamic-upstreams/) article.\n\n## <a name="usage">📖 Usage</a>\n\n### Sessions & Accounts\n\nOnce your administrator has added some comic libraries, you may browse and read comics. Codex will remember your preferences, bookmarks and progress in the browser session. Sessions last 60 days at which point they are destroyed.\nTo preserve these settings across browsers and after sessions expire, you may register an account with a username and password.\nYou will have to contact your administrator to reset your password if you forget it.\n\n### 🔎 Search Help\n\n[Codex\'s metadata search engine has it\'s own help page.\n](https://github.com/ajslater/codex/blob/release/SEARCH.md)\n\n## <a name="troubleshooting">🩺 Troubleshooting</a>\n\n### Logs\n\nCodex collects its logs in the `config/logs` directory. Take a look to see what th e server is doing.\n\nYou can change how much codex logs by setting the `LOGLEVEL` environment variable. By default this level is `INFO`. To see more messages run codex like:\n\n```bash\nLOGLEVEL=VERBOSE codex\n```\n\nTo see a great deal of noisy messages from dependencies try:\n\n```bash\nLOGLEVEL=DEBUG codex\n```\n\n### Watching Filesystem Events with Docker\n\nCodex tries to watch for filesystem events to instantly update your comic libraries when they are changed on disk. But these native filesystem events are not translated between macOS & Windows Docker hosts and the Docker Linux container. If you find that your installation is not updating to filesystem changes instantly, you might try enabling polling for the affected libraries and decreasing the `poll_every` value in the Admin console to a frequency that suits you.\n\n### Emergency Database Repair\n\nIf the database becomes corrupt, Codex includes a facitlity to rebuild the database.\nPlace a file named `rebuild_db` in your Codex config directory like so:\n\n```sh\n  touch config/rebuild_db\n```\n\nShut down and restart Codex.\n\nThe next time Codex starts it will back up the existing database and try to rebuild it.\nThe database lives in the config directory as the file `config/db.sqlite3`.\nIf this procedure goes kablooey, you may recover the original database at `config/db.sqlite3.backup`.\n\n### Bulk Database Updates Fail\n\nCodex\'s bulk database updater has been tested to usually work batching 100,000 filesystem events at a time. With enough RAM Codex could probably batch much more. But if you find that updating large batches of comics are failing, consider setting a the `max_db_ops` value in `hypercorn.toml` to a lower value. 1000 will probably still be pretty fast, for instance.\n\n### Bug Reports\n\nIssues are best filed [here on github](https://github.com/ajslater/codex/issues).\nHowever I and other brave Codex testers may also sometimes be found on the [Mylar support channels](https://github.com/mylar3/mylar3#live-support--conversation). It would be polite to use the `#anything-other-than-mylar` Discord channel to ask for help with Codex.\n\n## <a name="out-of-scope">🚫 Out of Scope</a>\n\n- I have no intention of making this an eBook reader.\n- I think metadata editing would be better placed in a comic manager than a reader.\n\n## <a name="alternatives-to-codex">📚Alternatives</a>\n\n- [Komga](https://komga.org/) has light metadata editing.\n- [Kavita](https://www.kavitareader.com/) has light metadata filtering/editing and supports comics and eBooks.\n- [Ubooquity](https://vaemendis.net/ubooquity/) reads both comics and eBooks.\n- [Mylar](https://github.com/mylar3/mylar3) is the best comic book manager which also has a built in reader.\n- [Comictagger](https://github.com/comictagger/comictagger) seems to be the best comic metadata editor. It comes with a powerful command line and useful desktop GUI.\n\n## <a name="develop-codex">🛠 Develop</a>\n\nCodex is a Django Python webserver with a VueJS front end.\n\n`/codex/codex/` is the main django app which provides the webserver and database.\n\n`/codex/frontend/` is where the vuejs frontend lives.\n\n`/codex/dev-env-setup.sh` will install development dependencies.\n\n`/codex/dev-ttabs.sh` will run the three or four different servers recommended for development in terminal tabs.\n\n`/codex/dev-codex.sh` runs the main Django server. Set the `DEBUG` environment variable to activate debug mode: `DEBUG=1 ./run.sh`. This also lets you run the server without collecting static files for production and with a hot reloading frontend. I recommend setting `LOGLEVEL=VERBOSE` for development as well.\n\n### Links\n\n- [Docker Image](https://hub.docker.com/r/ajslater/codex)\n- [PyPi Package](https://pypi.org/project/codex/)\n- [GitHub Project](https://github.com/ajslater/codex/)\n\n## <a name="special-thanks">🙏🏻 Special Thanks</a>\n\n- Thanks to [Aurélien Mazurie](https://pypi.org/user/ajmazurie/) for allowing me to use the PyPi name \'codex\'.\n- Thanks to the good people of [#mylar](https://github.com/mylar3/mylar3#live-support--conversation) for continuous feedback and comic ecosystem education.\n\n## <a name="enjoy">😊 Enjoy</a>\n\n![These simple people have managed to tap into the spiritual forces that mystics and yogis spend literal lifetimes seeking. I feel... ...I feel...](strange.jpg)\n',
    'author': 'AJ Slater',
    'author_email': 'aj@slater.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ajslater/codex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
