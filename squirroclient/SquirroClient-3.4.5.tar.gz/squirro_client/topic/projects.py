import base64
import json
import logging
import re

log = logging.getLogger(__name__)


class ProjectsMixin:

    PROJECT_ATTRIBUTES = {
        "default_search",
        "title",
        "description",
        "default_sort",
        "locator",
        "guide_completed_steps",
        "theme",
        "integration_dashboards",
        "first_visit",
        "newsletter_config",
        "photo",
    }

    def get_user_projects(self):
        """Get projects for the provided user.

        :returns: A list of projects.

        Example::

            >>> client.get_user_projects()
            [{u'id': u'Sz7LLLbyTzy_SddblwIxaA',
              u'title': u'My Contacts'},
             {u'id': u'2aEVClLRRA-vCCIvnuEAvQ',
              u'title': u'My Organizations'}]

        """

        url = "{ep}/{version}/{tenant}/projects".format(
            ep=self.topic_api_url, version=self.version, tenant=self.tenant,
        )

        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_project(self, project_id):
        """Get project details.

        :param project_id: Project identifier.
        :returns: A dictionary which contains the project.

        Example::

            >>> client.get_project('2aEVClLRRA-vCCIvnuEAvQ')
            {u'id': u'2aEVClLRRA-vCCIvnuEAvQ',
             u'title': u'My Organizations',
             u'type': u'my organizations'}

        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        res = self._perform_request("get", url)
        return self._process_response(res)

    def new_project(
        self,
        title,
        description=None,
        owner_id=None,
        locator=None,
        default_sort=None,
        project_id=None,
        photo=None,
    ):
        """Create a new project.

        :param title: Project title.
        :param description: Project description (optional).
        :param owner_id: User identifier which owns the objects.
        :param locator: Custom index locator configuration which is a
            dictionary which contains the `index_server` (full URI including
            the port for index server) key.
            For advanced usage the locator can also be split into a reader and
            a writer locator: {"reader": {"index_server":
            "https://reader:9200"}, "writer": {"index_server":
            "https://writer:9200"}}
        :param default_sort: Custom default sort configuration which is a
            dictionary which contains the `sort` (valid values are `date` and
            `relevance`) and `order` (valid values are `asc` and `desc`) keys.
        :param project_id: Optional string parameter to create the
            project with the provided id. The length of the parameter must
            be 22 characters. Useful when exporting and importing projects
            across multiple Squirro servers.
        :param photo: Address to the photo of the project
        :returns: A dictionary which contains the project identifier.

        Example::

            >>> locator = {'index_server': 'http://10.0.0.1:9200'}
            >>> default_sort = [{'relevance': {'order': 'asc'}}]
            >>> client.new_project(
                    'My Project',
                    description=description,
                    locator=locator,
                    default_sort=default_sort,
                    photo='https://twitter.com/Cristiano/photo',
                )
            {u'id': u'gd9eIipOQ-KobU0SwJ8VcQ'}
        """

        url = "{ep}/{version}/{tenant}/projects".format(
            ep=self.topic_api_url, version=self.version, tenant=self.tenant,
        )

        # build data
        data = {"title": title, "token": self.refresh_token}
        if project_id is not None:
            data["project_id"] = project_id
        if description is not None:
            data["description"] = description
        if owner_id is not None:
            data["owner_id"] = owner_id
        if locator is not None:
            data["locator"] = json.dumps(locator)
        if default_sort is not None:
            data["default_sort"] = json.dumps(default_sort)
        if photo is not None:
            data["photo"] = photo

        res = self._perform_request("post", url, data=data)
        return self._process_response(res, [201])

    def new_project_from_template(
        self,
        title,
        description=None,
        locator=None,
        template_name=None,
        template_path=None,
        project_id=None,
        keep_ids=False,
        import_app_nav_bar=True,
        import_default_sort=True,
        import_dashboards=True,
        import_dashboard_widgets=True,
        import_dashboard_loaders=True,
        import_email_templates=True,
        import_pipeline_workflows=True,
        import_enrichments=True,
        import_enrichment_pipelets=True,
        import_facets=True,
        import_community_types=True,
        import_communities=True,
        import_synonyms=True,
        import_machinelearning_workflows=True,
        import_machinelearning_jobs=True,
        import_machinelearning_models=True,
        import_project_configuration=True,
        import_project_translations=True,
        import_project_picture=True,
        import_smartfilters=True,
        import_sources=True,
        import_sources_dataloader_plugins=True,
        import_trends=True,
        import_items=True,
        import_guide_file=True,
        import_ais_published_models=True,
    ):
        """Create a new project from a project template.

        :param title: Project title.
        :param description: Project description.
        :param locator: Custom index locator configuration which is a
            dictionary which contains the `index_server` (full URI including
            the port for index server) key.
            For advanced usage the locator can also be split into a reader and
            a writer locator: {"reader": {"index_server":
            "https://reader:9200"}, "writer": {"index_server":
            "https://writer:9200"}}
        :param template_name: String. Name of a template to use. The project
            needs to be uploaded to the server first with the squirro_asset
            tool.
        :param template_path: String. Relative path of a squirro project file
            you want to use as a template. The project needs to be uploaded to
            the server first with `squirro_client.new_templfile` call first.
            This parameter is mutually exclusive with `template_name`. If
            `template_name` is set and exists it takes precedence.
        :param project_id: Optional string parameter to create the
            project with the provided id. The length of the parameter must
            be 22 characters. Useful when exporting and importing projects
            across multiple Squirro servers.
        :param import_app_nav_bar: Boolean. Whether to include the
            app & nav bar. Defaults to `True`.
        :param import_default_sort: Boolean. Whether to include the
            project default sort settings. Defaults to `True`.
        :param keep_ids: Boolean. Whether to try to create entities
            (project_id, dashboards, sources) with the same ID as the original's project
        :param import_dashboards: Boolean. Whether to include the dashboards,
            defaults to `True`.
        :param import_dashboard_widgets: Boolean. Whether to include the
            dashboards custom widgets. This only applies if `import_dashboards`
            is set to `True`. Defaults to `True`.
        :param import_dashboard_loaders: Boolean. Whether to include the
            dashboards loaders and dashboards themes. This only applies if
            `import_dashboards` is set to `True`. Defaults to `True`.
        :param import_email_templates: Boolean. Whether to include the email
            templates. Defaults to `True`. NOT USED AT THE MOMENT
        :param import_pipeline_workflows: Boolean. Whether to include the
            pipeline workflows. Defaults to `True`.
        :param import_enrichments: Boolean. Whether to include the enrichments,
            defaults to `True`.
        :param import_enrichment_pipelets: Boolean. Whether to include the
            pipelets together with the enrichments. This only applies of the
            `import_enrichments` is set to `True`. Defaults to `True`.
            defaults to `True`.
        :param import_facets: Boolean. Whether to include the facets,
            defaults to `True`. Needs the `import_synonyms` to be set to `True`
            also.
        :param import_community_types: Boolean. Whether to include the community_types,
            defaults to `True`. Needs `import_facets` to be True.
        :param import_communities: Boolean. Whether to include the communities,
            defaults to `True`. Needs `import_community_types` to be True.
        :param import_synonyms: Boolean. Whether to include the synonyms lists,
            defaults to 'True'.
        :param import_machinelearning_workflows: Boolean. Whether to include
            the machinelearning workflows. Defaults to `True`.
        :param import_machinelearning_jobs: Boolean. Whether to include the
            machinelearning jobs. Defaults to `True`.
        :param import_machinelearning_models: Boolean. Whether to include the
            machinelearning models. Defaults to `True`.
        :param import_project_configuration: Boolean. Whether to include the
            project configuration, defaults to `True`.
        :param import_project_translations: Boolean. Whether to include the
            project translations, defaults to `True`.
        :param import_project_picture: Boolean. Whether to include the
            project picture, defaults to `True`.
        :param import_smartfilters: Boolean. Whether to include the
            smartfilters, defaults to `True`.
        :param import_sources: Boolean. Whether to include the sources,
            defaults to `True`.
        :param import_sources_dataloader_plugins: Boolean. Whether to include
            the dataloaders, defaults to `True`.
        :param import_trends: Boolean. Whether to include the trends,
            defaults to `True`.
        :param import_items: Boolean. Whether to include the items,
            defaults to `True`. Needs the `import_facets` to be set to `True`
            also.
        :param import_guide_file: Boolean. Whether to include the project
            guide file, defaults to `True`.
        :param import_ais_published_models: Boolean. Whether to include the
            ais published models, defaults to `True`.
        :returns: A dictionary which contains the project identifier.

        Example::

            >>> client.new_project_from_template('My Project',
                                                 template_name="My Template")
            {u'id': u'gd9eIipOQ-KobU0SwJ8VcQ'}
        """

        url = "{ep}/{version}/{tenant}/projects_from_template".format(
            ep=self.topic_api_url, version=self.version, tenant=self.tenant,
        )

        # build data
        data = {"title": title}
        if description is not None:
            data["description"] = description
        if template_name is not None:
            data["template_name"] = template_name
        if template_path is not None:
            data["template_path"] = template_path
        if project_id is not None:
            data["project_id"] = project_id
        if locator is not None:
            data["locator"] = json.dumps(locator)
        if keep_ids:
            # Even though eventually keep_ids will end up as part of import_options,
            # let's keep the separation for the user's convenience
            data["keep_ids"] = True

        import_options = {
            "import_app_nav_bar": import_app_nav_bar,
            "import_default_sort": import_default_sort,
            "import_dashboards": import_dashboards,
            "import_dashboard_widgets": import_dashboard_widgets,
            "import_dashboard_loaders": import_dashboard_loaders,
            # 'import_email_templates': import_email_templates,
            "import_enrichments": import_enrichments,
            "import_enrichment_pipelets": import_enrichment_pipelets,
            "import_facets": import_facets,
            "import_community_types": import_community_types,
            "import_communities": import_communities,
            "import_machinelearning_workflows": import_machinelearning_workflows,
            "import_machinelearning_jobs": import_machinelearning_jobs,
            "import_machinelearning_models": import_machinelearning_models,
            "import_pipeline_workflows": import_pipeline_workflows,
            "import_project_configuration": import_project_configuration,
            "import_project_translations": import_project_translations,
            "import_project_picture": import_project_picture,
            "import_smartfilters": import_smartfilters,
            "import_sources": import_sources,
            "import_sources_dataloader_plugins": import_sources_dataloader_plugins,
            "import_trends": import_trends,
            "import_items": import_items,
            "import_synonyms": import_synonyms,
            "import_guide_file": import_guide_file,
            "import_ais_published_models": import_ais_published_models,
        }
        data["import_options"] = json.dumps(import_options)

        data["token"] = self.refresh_token

        res = self._perform_request("post", url, data=data)
        return self._process_response(res, [201])

    def modify_project(self, project_id, **kwargs):
        """Modify a project.

        :param project_id: Project identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the
            [[Projects#Update Project|Update Project]] resource for all
            possible parameters.

        Example::

            >>> client.modify_project('gd9eIipOQ-KobU0SwJ8VcQ',
            ...                       title='My Other Project')

        """
        url = "{ep}/{version}/{tenant}/projects/{project_id}".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        # build data
        data = {}
        for key in self.PROJECT_ATTRIBUTES:
            if key in kwargs:
                data[key] = kwargs[key]

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201, 204])

    def delete_project(self, project_id):
        """Delete a project.

        :param project_id: Project identifier.

        Example::

            >>> client.delete_project('gd9eIipOQ-KobU0SwJ8VcQ')

        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def reset_project(
        self,
        project_id,
        reset_dashboards=None,
        reset_elasticsearch_index=None,
        reset_facets=None,
    ):
        """Resets different entities of a project based on boolean flags.

        :param project_id: Project identifier.
        :param reset_dashboards: Boolean flag to decide whether to reset the
            project dashboards or not. If True, will delete all the dashboards
            in the current project. Defaults to False if not specified.
        :param reset_elasticsearch_index: Boolean flag to decide whether to
            reset/delete all documents in a project's elasticsearch index or
            not without deleting the index itself. Defaults to False if not
            specified.
        :param reset_facets: Boolean flag to decide whether to delete all the
            facets in the project. This needs the `reset_elasticsearch_index`
            flag to be set to True. Be aware that all the dashboards and other
            Squirro entities dependent on the current facets will stop working
            with the reset of facets.
            Defaults to False if not specified.

        Example::

            >>> client.reset_project(
                    'gd9eIipOQ-KobU0SwJ8VcQ', reset_dashboards=True,
                    reset_elasticsearch_index=True, reset_facets=True)

        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}/reset".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        headers = {"Content-Type": "application/json"}

        args = {
            "reset_dashboards": reset_dashboards,
            "reset_elasticsearch_index": reset_elasticsearch_index,
            "reset_facets": reset_facets,
        }
        data = {k: v for k, v in args.items() if v is not None}

        if data:
            res = self._perform_request(
                "post", url, data=json.dumps(data), headers=headers
            )
        else:
            res = {}
        self._process_response(res, [200])

    def export_project(
        self,
        project_id,
        export_app_nav_bar=True,
        export_default_sort=True,
        export_dashboards=True,
        export_dashboard_widgets=True,
        export_dashboard_loaders=True,
        export_email_templates=True,
        export_pipeline_workflows=True,
        export_enrichments=True,
        export_enrichment_pipelets=True,
        export_facets=True,
        export_community_types=True,
        export_communities=True,
        export_synonyms=True,
        export_machinelearning_workflows=True,
        export_machinelearning_jobs=True,
        export_machinelearning_models=True,
        export_project_configuration=True,
        export_project_translations=True,
        export_project_picture=True,
        export_smartfilters=True,
        export_sources=True,
        export_sources_dataloader_plugins=True,
        export_trends=True,
        export_guide_file=True,
        export_ais_published_models=True,
        export_items=False,
        export_items_config=None,
    ):
        """Exports parts or all configuration and metadata of a project.

        The following entities can be exported:
            - dashboards
                - optionally include dashboard loaders
                - optionally include custom widgets
            - email_templates
            - pipeline workflows
            - enrichments
                - optionally include pipelets
            - facets
            - community_types
            - communities
            - machinelearning workflow
                - optionally include jobs
                - optionally include models
            - project configuration
                - optionally include values
            - smartfilters
            - sources
                - optionally include dataloaders
            - trends
            - items
                - Requires `export_facets` parameter to be set to True

        By default all entities except items are exported. You can skip some by
        setting the corresponding keyword argument to `False` or `True`
        respectively.

        The content of the response contains an export_id which can be then used
        as a parameter to :func:`get_project_export` method to retrieve the zip
        archive.

        :param project_id: Project identifier.
        :param export_app_nav_bar: Boolean. Whether to include the
            app & nav bar. Defaults to `True`.
        :param export_default_sort: Boolean. Whether to include the
            default_sort. Defaults to `True`.
        :param export_dashboards: Boolean. Whether to include the dashboards,
            defaults to `True`.
        :param export_dashboard_widgets: Boolean. Whether to include the
            dashboards custom widgets. This only applies if `export_dashboards`
            is set to `True`. Defaults to `True`.
        :param export_dashboard_loaders: Boolean. Whether to include the
            dashboards loaders and dashboards themes. This only applies if `export_dashboards`
            is set to `True`. Defaults to `True`.
        :param export_email_templates: Boolean. Whether to include the email
            templates. Defaults to `True`.
        :param export_pipeline_workflows: Boolean. Whether to include the
            pipeline workflows. Defaults to `True`.
        :param export_enrichments: Boolean. Whether to include the enrichments,
            defaults to `True`.
        :param export_enrichment_pipelets: Boolean. Whether to include the
            pipelets together with the enrichments. This only applies of the
            `export_enrichments` is set to `True`. Defaults to `True`.
        :param export_facets: Boolean. Whether to include the facets,
            defaults to `True`. Needs `export_synonyms` to be True.
        :param export_community_types: Boolean. Whether to include the community_types,
            defaults to `True`. Needs `export_facets` to be True.
        :param export_communities: Boolean. Whether to include the communities,
            defaults to `True`. Needs `export_community_types` to be True.
        :param export_synonyms: Boolean. Whether to include the synonyms lists,
            defaults to 'True'.
        :param export_machinelearning_workflows: Boolean. Whether to include
            the machinelearning workflows. Defaults to `True`.
        :param export_machinelearning_jobs: Boolean. Whether to include the
            machinelearning jobs. Defaults to `True`.
        :param export_machinelearning_models: Boolean. Whether to include the
            machinelearning models. Defaults to `True`.
        :param export_project_configuration: Boolean. Whether to include the
            project configuration, defaults to `True`.
        :param export_project_translations: Boolean. Whether to include the
            project translations, defaults to `True`.
        :param export_project_picture: Boolean. Whether to include the
            project picture, defaults to `True`.
        :param export_smartfilters: Boolean. Whether to include the
            smartfilters, defaults to `True`.
        :param export_sources: Boolean. Whether to include the sources,
            defaults to `True`.
        :param export_sources_dataloader_plugins: Boolean. Whether to include
            the dataloaders, defaults to `True`.
        :param export_trends: Boolean. Whether to include the trends,
            defaults to `True`.
        :param export_guide_file: Boolean. Whether to include the guide file,
            defaults to `True`.
        :param export_items: Boolean. Whether to include the items,
            defaults to `False`. Needs the `export_facets` to be True.
        :param export_items_config: Dict. Containing the query parameters that
            can be used to filter down the exported items. Currently only
            `query` and `count` parameters are supported.
        :param export_ais_published_models: Boolean. Whether to include
            the published ml models, defaults to `True`.
        :return: Returns a dictionary containing the API response data and
            headers.

        Example::

            >>> res = client.export_project(
                    'gd9eIipOQ-KobU0SwJ8VcQ', {'dashboards': True})


        For saving the archive, refer to :func:`get_project_export` method.
        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}/export".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        headers = {"Content-Type": "application/json"}

        export_options = {
            "export_app_nav_bar": export_app_nav_bar,
            "export_default_sort": export_default_sort,
            "export_dashboards": export_dashboards,
            "export_dashboard_widgets": export_dashboard_widgets,
            "export_dashboard_loaders": export_dashboard_loaders,
            # 'export_email_templates': export_email_templates,
            "export_enrichments": export_enrichments,
            "export_enrichment_pipelets": export_enrichment_pipelets,
            "export_facets": export_facets,
            "export_community_types": export_community_types,
            "export_communities": export_communities,
            "export_machinelearning_workflows": export_machinelearning_workflows,
            "export_machinelearning_jobs": export_machinelearning_jobs,
            "export_machinelearning_models": export_machinelearning_models,
            "export_pipeline_workflows": export_pipeline_workflows,
            "export_project_configuration": export_project_configuration,
            "export_project_translations": export_project_translations,
            "export_project_picture": export_project_picture,
            "export_smartfilters": export_smartfilters,
            "export_sources": export_sources,
            "export_sources_dataloader_plugins": export_sources_dataloader_plugins,
            "export_trends": export_trends,
            "export_guide_file": export_guide_file,
            "export_items": export_items,
            "export_ais_published_models": export_ais_published_models,
            "export_synonyms": export_synonyms,
            "export_items_config": export_items_config,
        }
        export_options["token"] = self.refresh_token

        data = {k: v for k, v in export_options.items() if v is not None}

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)

        if res.status_code != 201:
            res.raise_for_status()

        return {"data": res.content, "headers": res.headers}

    def get_project_export(self, project_id, export_id, write_to_disk=False):
        """Retrieve a project export.

        If the export zip has not yet been created/finished, status will be
        'processing' and no data will be returned

        :param project_id: Project identifier.
        :param export_id: str. ID of project export.
        :param write_to_disk: Boolean. Whether or not to write the exported
            project onto the local Filesystem (in the current directory).

        Example::

            >>> res = client.get_project_export(
                    'gd9eIipOQ-KobU0SwJ8VcQ', 'sdf23fjjjdeobU0S3J83c3')

            If you want to store the zip archive in a file, do e.g.

            while within_max_time:
                ret = get_project_export()
                if ret.get('data'):
                    break

            with open('/tmp/archive.tar.gz', 'wb') as f:
                f.write(ret.get('data'))
        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}/export".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        headers = {"Content-Type": "application/json"}

        res = self._perform_request(
            "get", url, params={"export_id": export_id}, headers=headers
        )

        if res.status_code == 201:
            return {"data": None, "headers": res.headers, "status": "processing"}
        elif res.status_code != 200:
            res.raise_for_status()

        if write_to_disk:
            exported_file = self._get_file_name(res)
            with open(exported_file, "wb") as exported_project:
                exported_project.write(res.content)
                log.info("Exported project to ./%s", exported_file)
            return

        return {"data": res.content, "headers": res.headers, "status": "done"}

    def import_project(
        self,
        project_id,
        project_archive,
        import_app_nav_bar=True,
        import_default_sort=True,
        import_dashboards=True,
        import_dashboard_widgets=True,
        import_dashboard_loaders=True,
        import_email_templates=True,
        import_pipeline_workflows=True,
        import_enrichments=True,
        import_enrichment_pipelets=True,
        import_facets=True,
        import_community_types=True,
        import_communities=True,
        import_synonyms=True,
        import_machinelearning_workflows=True,
        import_machinelearning_jobs=True,
        import_machinelearning_models=True,
        import_project_configuration=True,
        import_project_translations=True,
        import_project_picture=True,
        import_smartfilters=True,
        import_sources=True,
        import_sources_dataloader_plugins=True,
        import_trends=True,
        import_items=True,
        import_guide_file=True,
        import_ais_published_models=True,
    ):

        """Imports parts or all configuration and metadata of a project.

        The following entities can be imported:
            - dashboards
                - optionally include dashboard loaders
                - optionally include custom widgets
            - email_templates
            - pipeline workflows
            - enrichments
                - optionally include pipelets
            - facets
            - community_types
            - communities
            - machinelearning workflow
                - optionally include jobs
                - optionally include models
            - project configuration
                - optionally include values
            - smartfilters
            - sources
                - optionally include dataloaders
            - trends
            - items
                - Requires `import_facets` parameter to be set to True

        By default all entities are imported. You can skip some by setting the
        corresponding keyword argument to `False` or `True` respectively.

        :param project_id: Project identifier.
        :param project_archive: Path to project archive.
        :param import_app_nav_bar: Boolean. Whether to include the
            app & nav bar. Defaults to `True`.
        :param import_default_sort: Boolean. Whether to include the
            project default sort. Defaults to `True`.
        :param import_dashboards: Boolean. Whether to include the dashboards,
            defaults to `True`.
        :param import_dashboard_widgets: Boolean. Whether to include the
            dashboards custom widgets. This only applies if `import_dashboards`
            is set to `True`. Defaults to `True`.
        :param import_dashboard_loaders: Boolean. Whether to include the
            dashboards loaders and dashboards themes. This only applies if
            `import_dashboards` is set to `True`. Defaults to `True`.
        :param import_email_templates: Boolean. Whether to include the email
            templates. Defaults to `True`.
        :param import_pipeline_workflows: Boolean. Whether to include the
            pipeline workflows. Defaults to `True`.
        :param import_enrichments: Boolean. Whether to include the enrichments,
            defaults to `True`.
        :param import_enrichment_pipelets: Boolean. Whether to include the
            pipelets together with the enrichments. This only applies of the
            `import_enrichments` is set to `True`. Defaults to `True`.
        :param import_facets: Boolean. Whether to include the facets,
            defaults to `True`. Needs the `import_synonyms` to be set to `True`
            also.
        :param import_community_types: Boolean. Whether to include the community_types,
            defaults to `True`. Needs `import_facets` to be True.
        :param import_communities: Boolean. Whether to include the communities,
            defaults to `True`. Needs `import_community_types` to be True.
        :param import_synonyms: Boolean. Whether to include the synonyms lists,
            defaults to 'True'.
        :param import_machinelearning_workflows: Boolean. Whether to include
            the machinelearning workflows. Defaults to `True`.
        :param import_machinelearning_jobs: Boolean. Whether to include the
            machinelearning jobs. Defaults to `True`.
        :param import_machinelearning_models: Boolean. Whether to include the
            machinelearning models. Defaults to `True`.
        :param import_project_configuration: Boolean. Whether to include the
            project configuration, defaults to `True`.
        :param import_project_translations: Boolean. Whether to include the
            project translations, defaults to `True`.
        :param import_project_picture: Boolean. Whether to include the
            project picture, defaults to `True`.
        :param import_smartfilters: Boolean. Whether to include the
            smartfilters, defaults to `True`.
        :param import_sources: Boolean. Whether to include the sources,
            defaults to `True`.
        :param import_sources_dataloader_plugins: Boolean. Whether to include
            the dataloaders, defaults to `True`.
        :param import_trends: Boolean. Whether to include the trends,
            defaults to `True`.
        :param import_items: Boolean. Whether to include the items,
            defaults to `True`. Needs the `import_facets` to be set to `True`
            also.
        :param import_guide_file: Boolean. Whether to include the project guide file,
            defaults to `True`.
        :param import_ais_published_models: Boolean. Whether to include the ais published models,
            defaults to `True`.
        :return: Returns a dictionary containing the API response data and
            headers.

        Example::

            >>> res = client.import_project(
                    'gd9eIipOQ-KobU0SwJ8VcQ', '/path/to/my.sqproj',
                    {'dashboards': False})
        """

        url = "{ep}/{version}/{tenant}/projects/{project_id}/import".format(
            ep=self.topic_api_url,
            version=self.version,
            tenant=self.tenant,
            project_id=project_id,
        )

        headers = {"Content-Type": "application/json"}

        import_options = {
            "import_app_nav_bar": import_app_nav_bar,
            "import_default_sort": import_default_sort,
            "import_dashboards": import_dashboards,
            "import_dashboard_widgets": import_dashboard_widgets,
            "import_dashboard_loaders": import_dashboard_loaders,
            # 'import_email_templates': import_email_templates,
            "import_enrichments": import_enrichments,
            "import_enrichment_pipelets": import_enrichment_pipelets,
            "import_facets": import_facets,
            "import_community_types": import_community_types,
            "import_communities": import_communities,
            "import_machinelearning_workflows": import_machinelearning_workflows,
            "import_machinelearning_jobs": import_machinelearning_jobs,
            "import_machinelearning_models": import_machinelearning_models,
            "import_pipeline_workflows": import_pipeline_workflows,
            "import_project_configuration": import_project_configuration,
            "import_project_translations": import_project_translations,
            "import_project_picture": import_project_picture,
            "import_smartfilters": import_smartfilters,
            "import_sources": import_sources,
            "import_sources_dataloader_plugins": import_sources_dataloader_plugins,
            "import_trends": import_trends,
            "import_items": import_items,
            "import_synonyms": import_synonyms,
            "import_guide_file": import_guide_file,
            "import_ais_published_models": import_ais_published_models,
        }
        import_options["token"] = self.refresh_token

        data = {k: v for k, v in import_options.items() if v is not None}

        with open(project_archive, "rb") as f:
            data["archive"] = base64.b64encode(f.read()).decode("utf-8")

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)

        if res.status_code != 201:
            res.raise_for_status()

        return {"data": res.content, "headers": res.headers}

    def _get_file_name(self, res):
        # Default file name
        file_name = "exported_project.sqproj"

        # File name from the header
        cd_header = res.headers.get("Content-Disposition")
        if cd_header:
            file_name = re.findall("filename=(.+)", cd_header)[0]

        return file_name
