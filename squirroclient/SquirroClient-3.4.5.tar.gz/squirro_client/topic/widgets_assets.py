import base64
import io
import json
import os
import tarfile
import uuid

import hjson


class WidgetsAndAssetsMixin(object):

    #
    # Dashboard Custom Widgets
    #

    def get_dashboard_widgets(self):
        """Return all dashboard widgets (for tenant).

        :returns: A list of custom dashboard widgets dictionaries.

        Example::

            >>> client.get_dashboard_widgets()
            [{u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
              u'title': u'Test',
              u'scope': u'custom',
              u'definition': [{u'background': u'#ffffff',
                               u'titleColor': u'#525252',
                               .....}]}]
        """
        url = "%(ep)s/v0/%(tenant)s/widgets" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_dashboard_widget(self, name, include_files=False):
        """Return a specific custom dashboard widget.

        :param name: Name of custom widget (in current tenant)
        :param include_files: Bool, Returns  all files with content of the
            asset if True. Default: False

        :returns: A dictionary of the named custom widget.

        Example::

            >>> client.get_dashboard_widget('map_us')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'title': u'Test',
             u'scope': u'custom',
             u'definition': [{u'background': u'#ffffff',
                             u'titleColor': u'#525252',
                             .....}]}]
        """
        url = "%(ep)s/v0/%(tenant)s/widgets/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": name,
        }

        params = {}
        if include_files:
            params["include_files"] = include_files

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_dashboard_widget(self, config):
        """Upload a new custom widget to squirro

        :param config: properties that require at least the `directory`
            to be specified where the custom widget code resides. The `title`
            property for use in the user interface is optional. All properties
            other than `directory` are passed on to the backend in the
            widget.ini file unless widget.ini already exists. The `name`
            and `hash` properties are reserved for internal use.

        Example::

            >>> client.new_dashboard_widget(
            >>>     config={u'directory': u'/home/us_map',
            >>>             u'base_widget': u'world_map',
            >>>             u'friendly_name': u'Map of the USA'})
        """
        if config is None or "directory" not in config:
            raise ValueError('Config needs to include directory: "%r"', config)
        directory = config["directory"].rstrip("/")
        name = os.path.basename(directory)

        if not name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                'The directory name "'
                + name
                + '" in config '
                + "needs to be alphanumeric or can contain - or _"
                + ". Please rename the directory."
            )

        data = "[widget]\n"
        for key, value in config.items():
            if key == "directory":
                continue
            elif key in ["name", "hash"]:
                raise ValueError('Reserved "' + key + '" property in config')
            data += key + "=" + value + "\n"

        data += "hash = " + str(uuid.uuid1()) + "\n"
        widget_config = io.BytesIO(data.encode())  # io.StringIO(data)

        try:
            with io.BytesIO() as binary_data:
                with tarfile.open(fileobj=binary_data, mode="w|gz") as tar:
                    tar.add(
                        directory,
                        arcname=name,
                        recursive=True,
                        # Ignore `widget.ini` files as config has
                        # precedence
                        filter=(
                            lambda ti: ti
                            if os.path.basename(ti.name) != "widget.ini"
                            else None
                        ),
                    )
                    # for widget config use innermost_directory/widget.ini for
                    # tar which is relative to innermost_directory
                    relative_widget_ini = name + "/" + "widget.ini"
                    tarinfo = tarfile.TarInfo(relative_widget_ini)
                    tarinfo.size = len(data)
                    tar.addfile(tarinfo, widget_config)

                data_dict = {"data": base64.b64encode(binary_data.getvalue()).decode()}
        except Exception as e:
            raise ValueError(e)

        headers = {"Content-Type": "application/json"}
        url = "%(ep)s/v0/%(tenant)s/widgets/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": name,
        }
        res = self._perform_request(
            "post", url, data=json.dumps(data_dict), headers=headers
        )
        return self._process_response(res, [201])

    def delete_dashboard_widget(self, name):
        """Delete a specific custom dashboard widget.

        :param name: Name of widget (in current tenant)

        Example::

            >>> client.delete_dashboard_widget('custom_widget')
        """
        url = "%(ep)s/v0/%(tenant)s/widgets/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": name,
        }
        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    #
    # Custom Assets
    #

    def get_assets(self, asset_type, global_assets=False):
        """Return all assets of `asset_type` for tenant.

        :param global_assets: Return all global assets if True.

        :returns: A list of custom assets dictionaries.

        Example::

            >>> client.get_assets('dashboard_loader')
            [{u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
              u'title': u'Layers and Sections Dashboard Loader',
              u'scope': u'custom',
              u'definition': [{u'background': u'#ffffff',
                               u'titleColor': u'#525252',
                               .....}]}]
        """
        url = "%(ep)s/v0/%(tenant)s/assets/%(asset_type)s" % {
            "ep": self.topic_api_url,
            "tenant": "_global" if global_assets else self.tenant,
            "asset_type": asset_type,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_asset(self, asset_type, name, global_asset=False, include_files=False):
        """Return a specific custom asset.

        :param asset_type: Type of asset (e.g. 'dashboard_loader')
        :param name: Name of asset (in current tenant)
        :param global_asset: Return a global asset if True.
        :param include_files: Bool, Returns  all files with content of the
            asset if True. Default: False

        :returns: A dictionary of the named asset.

        Example::

            >>> client.get_asset('dashboard_loader', 'layer_loader')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'title': u'Layer Dashboard Loader',
             u'scope': u'custom',
             u'definition': [{u'background': u'#ffffff',
                             u'titleColor': u'#525252',
                             .....}]}]
        """
        url = "%(ep)s/v0/%(tenant)s/assets/%(asset_type)s/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": "_global" if global_asset else self.tenant,
            "asset_type": asset_type,
            "name": name,
        }

        params = {}
        if include_files:
            params["include_files"] = include_files

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def delete_asset(self, asset_type, name, global_asset=False):
        """Delete a specific custom asset.

        :param asset_type: Type of asset (e.g. 'dashboard_loader')
        :param name: Name of asset (in current tenant)
        :param global_asset: Enables deletion of a global asset if True

        Example::

            >>> client.delete_asset('dashboard_loader', 'layer_loader')
        """
        url = "%(ep)s/v0/%(tenant)s/assets/%(asset_type)s/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": "_global" if global_asset else self.tenant,
            "asset_type": asset_type,
            "name": name,
        }
        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def new_asset(self, asset_type, folder, global_asset=False):
        """Upload a custom asset to squirro.

        :param asset_type: Type of asset (e.g. 'dashboard_loader')
        :param folder: name of a directory to be packaged into a tar.gz format
            and passed to the Squirro server. Configuration can be passed
            inside a file named `folder`/`asset_type`.json. The `name` and
            `hash` properties are reserved for internal use.
        :param global_asset: Upload a global asset if True.

        Example::

            >>> client.new_asset(
            >>>     asset_type='dashboard_loader',
            >>>     folder='./my_dashboard_loader')
        """
        name = os.path.basename(folder.rstrip("/"))

        if not name.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                'The folder name "'
                + name
                + '" '
                + "needs to be alphanumeric or can contain - or _"
                + ". Please rename the folder."
            )

        config = {}
        asset_json = os.path.join(folder, asset_type + ".json")

        if os.path.exists(asset_json):
            with open(asset_json, "r") as asset_config:
                config = hjson.load(fp=asset_config)

        if "hash" in config:
            raise ValueError('Reserved "hash" property in ' + asset_json)

        config["hash"] = str(uuid.uuid1())

        url = "%(ep)s/v0/%(tenant)s/assets/%(asset_type)s/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": "_global" if global_asset else self.tenant,
            "asset_type": asset_type,
            "name": name,
        }

        # Send the data as base64. For unknown reasons sending the file
        # natively via python's requests.files did not work.
        try:
            binary_data = io.BytesIO()
            with tarfile.open(fileobj=binary_data, mode="w|gz") as tar:
                tar.add(folder, arcname=name, recursive=True)

            tar_gz_base64 = base64.b64encode(binary_data.getvalue())
        except Exception as e:
            raise ValueError(e)

        res = self._perform_request(
            "post", url, data={"config": json.dumps(config), "data": tar_gz_base64}
        )

        return self._process_response(res, [201])
