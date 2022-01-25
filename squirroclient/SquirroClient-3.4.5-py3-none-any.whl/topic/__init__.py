# encoding: utf-8

import json
import logging
import sys

from ..util import deprecation
from .communities import CommunitiesMixin
from .community_subscription import CommunitySubscriptionsMixin
from .community_types import CommunityTypesMixin
from .configuration import ConfigurationMixin
from .contributingrecords import ContributingRecordsMixin
from .dashboards import DashboardsMixin
from .email_templates import EmailTemplatesMixin
from .enrichments import EnrichmentsMixin
from .entities import EntitiesMixin
from .facets import FacetsMixin
from .file_upload import FileUploadMixin
from .globaltemp import GlobalTempMixin
from .guidefiles import ProjectGuideFilesMixin
from .machinelearning import MachineLearningMixin
from .ml_candidate_set import MLCandidateSetMixin
from .ml_groundtruth import MLGroundTruthMixin
from .ml_model import MLModelsMixin
from .ml_publish import MLPublishMixin
from .ml_sentence_splitter import MLSentenceSplitterMixin
from .ml_template import MLTemplatesMixin
from .ml_user_feedback import MLUserFeedbackMixin
from .objects import ObjectsMixin
from .pipeline_sections import PipelineSectionsMixin
from .pipeline_status import PipelineStatusMixin
from .pipeline_workflows import PipelineWorkflowMixin
from .project_translations import ProjectTranslationsMixin
from .projects import ProjectsMixin
from .savedsearches import SavedSearchesMixin
from .smartfilters import SmartfiltersMixin
from .sources import SourcesMixin
from .subscriptions import SubscriptionsMixin
from .synonyms import SynonymsMixin
from .tasks import TasksMixin
from .themes import ThemesMixin
from .trenddetection import TrendDetectionMixin
from .widgets_assets import WidgetsAndAssetsMixin

MAX_UPDATE_COUNT = 10000  # ES hard limit is 10000
MAX_UPDATE_SIZE = 80 * 1024 * 1024  # 80 MB (nginx has 96 MB limit)


class TopicApiBaseMixin(object):
    def get_projects(self):
        """Return all projects."""
        # Build URL
        url = "%(ep)s/v0/%(tenant)s/projects" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_pipelets(self):
        """Return all available pipelets.

        These pipelets can be used for enrichments of type `pipelet`.

        :returns: A dictionary where the value for `pipelets`
            is a list of pipelets.

        Example::

            >>> client.get_pipelets()
            {'pipelets': [{'id': 'tenant01/textrazor',
                            'name': 'textrazor'}]}
        """
        url = "%(ep)s/v0/%(tenant)s/pipelets" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_pipelet(self, name):
        """Return details for one pipelet.

        :returns: A dictionary with pipelet details.

        Example::

            >>> client.get_pipelet('textrazor')
            {'description': 'Entity extraction with `TextRazor`.',
             'description_html': '<p>Entity extraction with
             '<code>TextRazor</code>.</p>',
             'id': 'tenant01/textrazor',
             'name': 'textrazor',
             'source': 'from squirro.sdk.pipelet import PipeletV1\n\n\n...'}
        """
        url = "%(ep)s/v0/%(tenant)s/pipelets/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": name,
        }
        res = self._perform_request("get", url)
        return self._process_response(res)

    def delete_pipelet(self, name):
        """Delete a pipelet.

        This will break existing enrichments if they still make use of this
        pipelet.

        Example::

            >>> client.delete_pipelet('textrazor')
        """
        url = "%(ep)s/v0/%(tenant)s/pipelets/%(name)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "name": name,
        }
        res = self._perform_request("delete", url)
        self._process_response(res, [204])

    def get_version(self):
        """Get current squirro version and build number.

        :return: Dictionary contains 'version', 'build' and 'components'.
            'components' is used for numeric comparison.

        Example::

            >>> client.get_version()
            {
                "version": "2.4.5",
                "build": "2874"
                "components": [2, 4, 5]
            }
        """
        url = "%(ep)s/v0/version" % {"ep": self.topic_api_url}
        res = self._perform_request("get", url)
        return self._process_response(res, [200])

    #
    # Items
    #
    def get_encrypted_query(
        self,
        project_id,
        query=None,
        aggregations=None,
        fields=None,
        created_before=None,
        created_after=None,
        options=None,
        **kwargs
    ):
        """Encrypts and signs the `query` and returns it. If set the
        `aggregations`, `created_before`, `created_after`, `fields` and
        `options` are part of the encrypted query as well.

        :param project_id: Project identifier.
        :param query: query to encrypt.

        For additional parameters see `self.query()`.

        :returns: A dictionary which contains the encrypted query

        Example::

            >>> client.get_encrypted_query(
                    '2aEVClLRRA-vCCIvnuEAvQ',
                    query='test_query')
            {'encrypted_query': 'YR4h147YAldsARmTmIrOcJqpuntiJULXPV3ZrX_'
            'blVWvbCavvESTw4Jis6sTgGC9a1LhrLd9Nq-77CNX2eeieMEDnPFPRqlPGO8V'
            'e2rlwuKuVQJGQx3-F_-eFqF-CE-uoA6yoXoPyYqh71syalWFfc-tuvp0a7c6e'
            'eKAO6hoxwNbZlb9y9pha0X084JdI-_l6hew9XKZTXLjT95Pt42vmoU_t6vh_w1'
            'hXdgUZMYe81LyudvhoVZ6zr2tzuvZuMoYtP8iMcVL_Z0XlEBAaMWAyM5hk_tAG'
            '7AbqGejZfUrDN3TJqdrmHUeeknpxpMp8nLTnbFMuHVwnj2hSmoxD-2r7BYbolJ'
            'iRFZuTqrpVi0='}
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/items/query_encryption"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        args = {
            "query": query,
            "aggregations": aggregations,
            "fields": fields,
            "options": options,
            "created_before": created_before,
            "created_after": created_after,
        }
        args.update(kwargs)
        data = dict([(k, v) for k, v in list(args.items()) if v is not None])

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def query(
        self,
        project_id,
        query=None,
        aggregations=None,
        start=None,
        count=None,
        fields=None,
        highlight=None,
        next_params=None,
        created_before=None,
        created_after=None,
        options=None,
        encrypted_query=None,
        child_count=None,
        **kwargs
    ):
        """Returns items for the provided project.

        This is the successor to the `get_items` method and should be used in
        its place.

        :param project_id: Project identifier.
        :param query: Optional query to run.
        :param start: Zero based starting point.
        :param count: Maximum number of items to return.
        :param child_count: Maximum number of entities to return with items.
        :param fields: Fields to return.
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.
        :param options: Dictionary of options that influence the
            result-set. Valid options are:

                - `fold_near_duplicates` to fold near-duplicates together and
                  filter them out of the result-stream. Defaults to False.
                - `abstract_size` to set the length of the returned abstract in
                  number of characters. Defaults to the configured
                  default_abstract_size (500).
                - `update_cache` if `False` the result won't be cached. Used
                  for non-interactive queries that iterate over a large number
                  of items. Defaults to `True`.
        :param encrypted_query: Optional Encrypted query returned by
            `get_encrypted_query` method. This parameter overrides the `query`
            parameter and `query_template_params` (as part of `options`
            parameter), if provided. Returns a 403 if the encrypted query is
            expired or has been altered with.
        :param next_params: Parameter that were sent with the previous
            response as `next_params`.
        :param created_before: Restrict result set to items created before
            `created_before`.
        :param created_after: Restrict result set to items created after
            `created_after`.
        :param kwargs: Additional query parameters. All keyword arguments are
            passed on verbatim to the API.
        """
        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/query"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        args = {
            "query": query,
            "aggregations": aggregations,
            "start": start,
            "count": count,
            "child_count": child_count,
            "fields": fields,
            "highlight": highlight,
            "next_params": next_params,
            "options": options,
            "created_before": created_before,
            "created_after": created_after,
            "encrypted_query": encrypted_query,
        }
        if "scroll" in kwargs:
            logging.warning(
                "Wrong usage of `scroll` parameter! Has no effect for `query` method since v3.3.8. "
                "Use `scan` method to perform scrolling."
            )
            kwargs.pop("scroll")
        args.update(kwargs)
        data = dict([(k, v) for k, v in list(args.items()) if v is not None])

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def recommend(
        self,
        project_id,
        item_id=None,
        external_id=None,
        text=None,
        method=None,
        related_fields=None,
        count=10,
        fields=None,
        created_before=None,
        options=None,
        created_after=None,
        query=None,
        aggregations=None,
        method_params=None,
        **kwargs
    ):
        """Returns recommended items for the provided ids or text.

        :param project_id: Project identifier.
        :param item_id: ID of item used for recommendation (optional).
        :param external_id: External ID of item used for recommendation if
            item_id is not provided (optional)
        :param text: Text content used for recommendation if neither item_id nor
            external_id are not provided (optional)
        :param method: Recommendation method (optional).
        :param method_params: Dictionary of method parameters used for
            recommendations (optional).
        :param related_fields: Fields used to find relationship for between
            items for recommendation. If this param is not set, we use the title
            and the body of the item.
        :param count: Maximum number of items to return.
        :param fields: Fields to return.
        :param options: Dictionary of options that influence the
            result-set. Valid options are:

                - `fold_near_duplicates` to fold near-duplicates together and
                  filter them out of the result-stream. Defaults to False.
        :param created_before: Restrict result set to items created before
            `created_before`.
        :param created_after: Restrict result set to items created after
            `created_after`.
        :param query: Search query to restrict the recommendation set.
        :param aggregations: Aggregation of faceted fields
        """

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/recommend"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        args = {
            "item_id": item_id,
            "external_id": external_id,
            "text": text,
            "method": method,
            "method_params": method_params,
            "related_fields": related_fields,
            "count": count,
            "fields": fields,
            "options": options,
            "created_before": created_before,
            "created_after": created_after,
            "query": query,
            "aggregations": aggregations,
        }
        args.update(kwargs)
        data = dict((k, v) for k, v in list(args.items()) if v is not None)

        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def recommendation_methods(self, project_id):
        """Returns the available recommendation methods.

        :param project_id: Project identifier.
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/items/recommend/methods"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def recommend_facets(
        self, project_id, method=None, count=10, explanation_count=1, data=None
    ):
        """Recommend facet value based on input facets

        :param project_id: Project identifier.
        :param method: Method of recommendation. Possible values:

            - conprob: use conditional probability for scoring
            - composition: use sum of individual feature scores for scoring
            - ml_classification: use squirro machine learning service with
              classifcation workflow
            - ml_regression_aggregation: use squirro machine learning service
              with regression aggregation workflow

        :param count: number of return recommendations
        :param explanation_count: number of return explanations for each
            recommendations, explanations are sorted by score, default is 1
        :param data: input data, json object containing flowing fields:

            - input_features: dictionary of input facets. Each feature is a
              facet name and list of values. Accept range of values,
              using elasticsearch range query syntax.
            - filter_query: query to filter data set for recommendations,
              adhere squirro query syntax (optional)
            - target_feature: name of target facet
            - return_features: list of return facets in recommendation. If
              this field is not set then name of target facet is used.
            - ml_workflow_id: Identififer of machine learning workflow. Could
              be None in "adhoc" recommendation methods (e.g conprob,
              composition) which do not need machine learning training.

        :return: Recommendation response

        Example::

            data = {
                "input_features": {
                    "Job": ["Head of Sales", "Head of Marketing"],
                    "City": ["Zurich", "London"],
                    "Salary": [{
                        "gte": 80000,
                        "lte": 120000
                    }]
                },
                "filter_query": "$item_created_at>=2018-03-20T00:00:00",
                "target_feature": "Person_Id",
                "return_features": ["Name"],
                "ml_workflow_id": None
            }

            >>> client.recommend_facets(
            ...     project_id='2aEVClLRRA-vCCIvnuEAvQ',
            ...     method='conprob', data=data, count=3)

            response = {
                "count": 3,
                "time_ms": 79,
                "params": {...},
                "total": 989,
                "method": {
                    "last_updated": null,
                    "name": "conprob",
                    "ml_workflow_id": null
                },
                "recommendations": [{
                    "target_feature": "Person_Id",
                    "score": 1.0,
                    "explanation": [
                        {
                            "score": 0.7713846764962218,
                            "feature": "City",
                            "value": "Zurich"
                        },
                        {
                            "score": 0.7461064995415513,
                            "feature": "Job",
                            "value": "Head of Sales"
                        },
                        {
                            "score": 0.7289157048296231,
                            "feature": "Salary",
                            "value": {
                                "gte": 80000,
                                "lte": 100000
                            }
                        }
                    ],
                    "return_features": {
                        "Name": "Amber Duncan"
                    },
                    "target_value": "1234"},
                    ...
                ]
            }
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/facets/recommend"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        if not data:
            data = {}
        data["feature_type"] = "facet"
        data["count"] = count
        data["explanation_count"] = explanation_count
        data["method"] = method
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def recommend_facets_explore(
        self,
        project_id,
        method=None,
        count=10,
        data=None,
        start=None,
        next_params=None,
        highlight=None,
    ):
        """Explore results of facet recommendation

        :param project_id: Project identifier.
        :param method: Method of recommendation. Possible values:

            - conprob: use conditional probability for scoring
            - composition: use sum of individual feature scores for scoring
            - ml_classification: use squirro machine learning service with
              classifcation workflow
            - ml_regression_aggregation: use squirro machine learning service
              with regression aggregation workflow

        :param count: number of return recommendations
        :param data: input data, json object containing flowing fields:

            - input_features: dictionary of input facets. Each feature is a
              facet name and list of values. Accept range of values,
              using elasticsearch range query syntax.
            - filter_query: query to filter data set for recommendations,
              adhere squirro query syntax (optional)
            - target_feature: name of target facet
            - target_value: value of target facet
            - filter_features: dictionary of facets used to filter items.
              Similar format as input_features
            - return_features: list of return facets in recommendation. If
              this field is not set then name of target facet is used.
            - ml_workflow_id: Identififer of machine learning workflow. Could
              be None in "adhoc" recommendation methods (e.g conprob,
              composition) which do not need machine learning training.

        :param start: Zero based starting point.
        :param next_params: Parameter that were sent with the previous
            response as `next_params`.
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.

        :return: List of items with facets satisfied input

        Example::

            data = {
                "input_features": {
                    "Job": ["Head of Sales", "Head of Marketing"],
                    "City": ["Zurich", "London"],
                    "Salary": [{
                        "gte": 80000,
                        "lte": 120000
                    }]
                },
                "filter_query": "$item_created_at>=2018-03-20T00:00:00",
                "target_feature": "Person_Id",
                "target_value": "Squirro",
                "filter_features": {
                    "Job": ["Head of Sales"]
                },
                "ml_workflow_id": None
            }

            >>> client.recommend_facets_explore(
            ...     project_id='2aEVClLRRA-vCCIvnuEAvQ',
            ...     method='conprob', data=data, count=10)
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/facets/recommend/explorequery"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        if not data:
            data = {}
        data["feature_type"] = "facet"
        data["count"] = count
        data["method"] = method
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)

        json_response = self._process_response(res)
        if json_response:
            query = json_response.get("query")
            aggregations = json_response.get("aggregations")
            if query and aggregations:
                res = self.query(
                    project_id=project_id,
                    query=query,
                    count=count,
                    child_count=count,
                    aggregations=aggregations,
                    start=start,
                    next_params=next_params,
                    highlight=highlight,
                )
                res["aggregations"] = {
                    key: {
                        "values": [
                            v
                            for v in value[key]["values"]
                            if v["key"] in data["input_features"][key]
                        ]
                    }
                    for key, value in list(res["aggregations"].items())
                }
                return res

        return {}

    def recommend_facets_methods(self, project_id):
        """Returns the available facet recommendation methods.

        :param project_id: Project identifier.
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/facets/recommend/methods"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def recommend_entities(
        self, project_id, method=None, count=10, explanation_count=1, data=None
    ):
        """Recommend entity property based on input entity properties

        :param project_id: Project identifier.
        :param method: Method of recommendation. Possible values:

            - conprob: use conditional probability for scoring
            - composition: use sum of individual feature scores for scoring
            - ml_classification: use squirro machine learning service with
              classifcation workflow
            - ml_regression_aggregation: use squirro machine learning service
              with regression aggregation workflow

        :param count: number of return recommendations
        :param explanation_count: number of return explanations for each
            recommendations, explanations are sorted by score, default is 1
        :param data: input data, json object containing flowing fields:

            - input_features: dictionary of input entity properties. Each
              feature is a property name and list of values. Accept range of
              values, using elasticsearch range query syntax.
            - entity_type: type of entity to filter data for recommendation.
            - filter_query: query to filter data set for recommendations,
              adhere squirro query syntax (optional)
            - target_feature: name of target property
            - return_features: list of return properties in recommendation. If
              this field is not set then name of target property is used.
            - ml_workflow_id: Identififer of machine learning workflow. Could
              be None in "adhoc" recommendation methods (e.g conprob,
              composition) which do not need machine learning training.

        :return: Recommendation response

        Example::

            data = {
                "input_features": {
                    "job": ["Head of Sales", "Head of Marketing"],
                    "city": ["Zurich", "London"],
                    "salary": [{
                        "gte": 80000,
                        "lte": 120000
                    }]
                },
                "filter_query": "$item_created_at>=2018-03-20T00:00:00",
                "target_feature": "person_id",
                "return_features": ["name"],
                "ml_workflow_id": None,
                "entity_type": "career"
            }

            >>> client.recommend_entities(
            ...     project_id='2aEVClLRRA-vCCIvnuEAvQ',
            ...     method='conprob', data=data, count=3)

            response = {
                "count": 3,
                "time_ms": 79,
                "params": {...},
                "total": 989,
                "method": {
                    "last_updated": null,
                    "name": "conprob",
                    "ml_workflow_id": null
                },
                "recommendations": [{
                    "target_feature": "person_id",
                    "score": 1.0,
                    "explanations": [
                        {
                            "score": 0.7713846764962218,
                            "feature": "city",
                            "value": "Zurich"
                        },
                        {
                            "score": 0.7461064995415513,
                            "feature": "job",
                            "value": "Head of Sales"
                        },
                        {
                            "score": 0.7289157048296231,
                            "feature": "salary",
                            "value": {
                                "gte": 80000,
                                "lte": 100000
                            }
                        }
                    ],
                    "return_features": {
                        "name": "Amber Duncan"
                    },
                    "target_value": "person_1234"},
                    ...
                ]
            }
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/entities/recommend"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        if not data:
            data = {}
        data["feature_type"] = "entity"
        data["count"] = count
        data["explanation_count"] = explanation_count
        data["method"] = method
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def query_entities(
        self,
        project_id,
        query=None,
        fields=None,
        aggregations=None,
        start=None,
        count=None,
        **kwargs
    ):
        """Query entity and return aggregations of some entity fields

        :param project_id: Project identifier.
        :param count: number of return entities
        :param start: zero based starting point of return entities
        :param fields: List of fields to return
        :param query: query to match entity. Use item query syntax,
            e.g entity:{type:career}
        :param aggregations: Aggregation of entity fields. For numeric
            property you need to add prefix `numeric_` to field name,
            e.g. `numeric_properties.salary`. We support 2 methods of
            aggregations: "terms" and "stats" (for numeric properties).
            Default method is "terms" aggregation.

        :return: List of entities and aggregations

        Example::

            aggregations = {
                "city": {
                    "fields": "properties.city",
                    "size": 3
                },
                "salary": {
                    "fields": "numeric_properties.salary",
                    "method": "stats"
                },
                "job": {
                    "fields": "properties.job",
                    "size": 3
                },
            }

            >>> client.query_entities(project_id='2aEVClLRRA-vCCIvnuEAvQ',
            ...     query='entity:{properties.name:And*}', count=3,
            ...     aggregations=aggregations)

            response = {
                "count": 3,
                "entities": [
                    {
                        "confidence": 0.8,
                        "name": "Andrea Warren",
                        "external_id": "entity_288",
                        "extracts": [
                            {
                                ...
                            }
                        ],
                        "properties": {
                            "person_id": "id_andrea warren",
                            "city": "Cooperville",
                            "job": "Tax inspector",
                            "name": "Andrea Warren",
                            "salary": 511937
                        },
                        "item_id": "-xkKQf2SBlS-ZRkIfw4Suw",
                        "relevance": 0.8,
                        "child_id": "wQ_atc8Nuk4eqj_xSugMOg",
                        "type": "career",
                        "id": "entity_288"
                    },
                    ...
                ],
                "total": 1213,
                "aggregations": {
                    "salary": {
                        "stats": {
                            "count": 969,
                            "max": 998787.0,
                            "sum": 490231470.0,
                            "avg": 505914.8297213622,
                            "min": 130.0
                        }
                    },
                    "job": {
                        "values": [
                            {
                                "key": "Conservation officer, nature",
                                "value": 6
                            },
                            {
                                "key": "Geneticist, molecular",
                                "value": 6
                            },
                            {
                                "key": "Immigration officer",
                                "value": 6
                            }
                        ]
                    },
                    ...
                },
                "time_ms": 62
            }
        """

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/entities/query"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        args = {
            "query": query,
            "fields": fields,
            "start": start,
            "count": count,
            "aggregations": aggregations,
        }
        args.update(kwargs)
        data = dict([(k, v) for k, v in list(args.items()) if v is not None])
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def recommend_entities_explore(
        self,
        project_id,
        method=None,
        count=10,
        data=None,
        start=None,
        next_params=None,
        highlight=None,
    ):
        """Explore results of entity recommendation

        :param project_id: Project identifier.
        :param method: Method of recommendation. Possible values:

            - conprob: use conditional probability for scoring
            - composition: use sum of individual feature scores for scoring

        :param count: number of return entities
        :param data: input data, json object containing flowing fields:

            - input_features: dictionary of input entity properties. Each
              feature is a property name and list of values. Accept range of
              values, using elasticsearch range query syntax.
            - entity_type: type of entity to filter data for recommendation.
            - filter_query: query to filter data set for recommendations,
              adhere squirro query syntax (optional)
            - target_feature: name of target property
            - target_value: value of target property
            - filter_features: dictionary of entity properties used for
              filtering entities. Similar format as input_features
            - ml_workflow_id: Identififer of machine learning workflow. Could
              be None in "adhoc" recommendation methods (e.g conprob,
              composition) which do not need machine learning training.

        :param start: Zero based starting point.
        :param next_params: Parameter that were sent with the previous
            response as `next_params`.
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.
        :return: List of items and entities satisfied input

        Example::

            data = {
                "input_features": {
                    "job": ["Head of Sales", "Head of Marketing"],
                    "city": ["Zurich", "London"],
                    "salary": [{
                        "gte": 80000,
                        "lte": 120000
                    }]
                },
                "filter_query": "$item_created_at>=2018-03-20T00:00:00",
                "target_feature": "person_id",
                "target_value": "a_squirro_employee",
                "filter_features": {
                    "job": ["Head of Sales"]
                },
                "ml_workflow_id": None,
                "entity_type": "career"
            }

            >>> client.recommend_entities_explore(
            ...     project_id='2aEVClLRRA-vCCIvnuEAvQ',
            ...     method='conprob', data=data, count=10)
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/entities/recommend/explorequery"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        if not data:
            data = {}
        data["feature_type"] = "entity"
        data["count"] = count
        data["method"] = method
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)

        json_response = self._process_response(res)
        if json_response:
            query = json_response.get("query")
            aggregations = json_response.get("aggregations")
            if query and aggregations:
                res = self.query(
                    project_id=project_id,
                    query=query,
                    count=count,
                    child_count=count,
                    start=start,
                    next_params=next_params,
                    highlight=highlight,
                )
                agg_res = self.query_entities(
                    project_id=project_id,
                    query=query,
                    count=count,
                    aggregations=aggregations,
                )
                res["query"] = query
                res["aggregations"] = {
                    key: {
                        "values": [
                            v
                            for v in value["values"]
                            if v["key"] in data["input_features"][key]
                        ]
                    }
                    for key, value in list(agg_res["aggregations"].items())
                }
                return res
        return {}

    def recommend_entities_methods(self, project_id):
        """Returns the available entity recommendation methods.

        :param project_id: Project identifier.
        """
        url = (
            "%(ep)s/%(version)s/%(tenant)s"
            "/projects/%(project_id)s/entities/recommend/methods"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def scan(
        self,
        project_id,
        query=None,
        scroll="5m",
        count=1000,
        fields=None,
        highlight=None,
        created_before=None,
        created_after=None,
        options=None,
        encrypted_query=None,
        child_count=100,
    ):
        """
        Returns an iterator to scan through all items of a project.

        Note: For smartfilter queries this still returns at maximum 10000
        results.

        :param project_id: The id of the project you want to scan
        :param query: An optional query string to limit the items to a matching
            subset.
        :param scroll: A time to use as window to keep the search context
            active in Elasticsearch.
            See https://www.elastic.co/guide/en/elasticsearch
            /reference/current/search-request-scroll.html
            for more details.
        :param count: The number of results fetched per batch. You only need
            to adjust this if you e.g. have very big documents. The maximum
            value that can be set is 10'000.
        :param fields: Fields to return
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.
        :param created_before: Restrict result set to items created before
            `created_before`.
        :param created_after: Restrict result set to items created after
            `created_after`.
        :param options: Dictionary of options that influence the
            result-set. Valid options are: `abstract_size` to set the length
            of the returned abstract in number of characters. Defaults to the
            configured default_abstract_size (500).
        :param child_count: Maximum number of matching entities to return with
            items. The maximum value that can be set is 100.

        :return: An iterator over all (matching) items.

        Open issues/current limitations:
            - ensure this works for encrypted queries too.
            - support fold_near_duplicate option
            - support smart filter queries with more than 10k results

        Example::

        >>> for item in client.scan(project_id='Sz7LLLbyTzy_SddblwIxaA', query='country:CH AND plants',
        ...                         count=500, scroll='1m'):
                # process matched item

        """
        assert scroll, "`scroll` cannot be empty for scan."
        if options:
            assert "fold_near_duplicate" not in options

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/query"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}

        args = {
            "query": query,
            "scroll": scroll,
            "count": min(count, 10000),
            "child_count": min(child_count, 100),
            "fields": fields,
            "highlight": highlight,
            "options": options,
            "created_before": created_before,
            "created_after": created_after,
        }
        data = dict([(k, v) for k, v in args.items() if v is not None])

        items = True
        while items:
            res = self._process_response(
                self._perform_request(
                    "post", url, data=json.dumps(data), headers=headers
                )
            )
            items = res.get("items", [])
            for item in items:
                yield item
            if not res.get("eof"):
                data["next_params"] = res.get("next_params")
            else:
                break

    def get_items(self, project_id, **kwargs):
        """Returns items for the provided project.

        DEPRECATED. The `query` method is more powerful.

        :param project_id: Project identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Items#List Items|List Items]]
            resource for all possible parameters.
        :returns: A dictionary which contains the items for the project.

        Example::

            >>> client.get_items('2aEVClLRRA-vCCIvnuEAvQ', count=1)
            {'count': 1,
             'eof': False,
             'items': [{'created_at': '2012-10-06T08:27:58',
                         'id': 'haG6fhr9RLCm7ZKz1Meouw',
                         'link': 'https://www.youtube.com/...',
                         'read': True,
                         'item_score': 0.5,
                         'score': 0.56,
                         'sources': [{'id': 'oMNOQ-3rQo21q3UmaiaLHw',
                                       'link': 'https://gdata.youtube...',
                                       'provider': 'feed',
                                       'title': 'Uploads by mymemonic'},
                                      {'id': 'H4nd0CasQQe_PMNDM0DnNA',
                                       'link': None,
                                       'provider': 'savedsearch',
                                       'title': 'Squirro Alerts for "mmonic"'
                                      }],
                         'starred': False,
                         'thumbler_url': '[long url]...jpg',
                         'title': 'Web Clipping - made easy with Memonic',
                         'webshot_height': 360,
                         'webshot_url': 'http://webshot.trunk....jpg',
                         'webshot_width': 480}],
             'now': '2012-10-11T14:39:54'}

        """
        deprecation("Please use the query method instead.")

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        res = self._perform_request("get", url, params=kwargs)
        return self._process_response(res)

    def get_item(self, project_id, item_id, **kwargs):
        """Returns the requested item for the provided project.

        :param project_id: Project identifier.
        :param item_id: Item identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Items#Get Item|Get Item]] resource
            for all possible parameters.
        :returns: A dictionary which contains the individual item.

        Example::

            >>> client.get_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw')
            {'item': {'created_at': '2012-10-06T08:27:58',
                       'id': 'haG6fhr9RLCm7ZKz1Meouw',
                       'link': 'https://www.youtube.com/watch?v=Zzvhu42dWAc',
                       'read': True,
                       'item_score': 0.5,
                       'score': 0.56,
                       'sources': [{'id': 'oMNOQ-3rQo21q3UmaiaLHw',
                                     'link': 'https://gdata.youtube.com/...',
                                     'provider': 'feed',
                                     'title': 'Uploads by mymemonic'},
                                    {'id': 'H4nd0CasQQe_PMNDM0DnNA',
                                     'link': None,
                                     'provider': 'savedsearch',
                                     'title': 'Squirro Alerts for "memonic"'}
                                   ],
                       'starred': False,
                       'thumbler_url': '[long url]...jpg',
                       'title': 'Web Clipping - made easy with Memonic',
                       'webshot_height': 360,
                       'webshot_url': 'http://webshot.trunk....jpg',
                       'webshot_width': 480}}

        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/%(item_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "item_id": item_id,
        }

        res = self._perform_request("get", url, params=kwargs)
        return self._process_response(res)

    def _build_item_update(self, star, read, keywords, entities):
        """Builds an update for a single item.

        :param star: Starred flag for the item, either `True` or `False`.
        :param read: Read flag for the item, either `True` or `False`.
        :param keywords: Updates to the `keywords` of the item.
        :param entities: Updates to the `entities` of the item.
        """

        # build item state
        state = {}
        if star is not None:
            state["starred"] = star
        if read is not None:
            state["read"] = read

        data = {"state": state}

        if keywords is not None:
            data["keywords"] = keywords

        if entities is not None:
            data["entities"] = entities

        return data

    def modify_item(
        self,
        project_id,
        item_id,
        star=None,
        read=None,
        keywords=None,
        entities=None,
        force_cache_clear=None,
    ):
        """Updates the flags, entities, and/or keywords of an item.

        You can only update `star`, `read`, and `keywords`.
        The new values will overwrite all old values.

        :param project_id: Project identifier.
        :param item_id: Item identifier.
        :param star: Starred flag for the item, either `True` or `False`.
        :param read: Read flag for the item, either `True` or `False`.
        :param keywords: Updates to the `keywords` of the item.
        :param entities: Updates to the `entities` of the item.
        :param force_cache_clear: Deprecated. This is the default behavior now.
            Force all relevant caches to be cleared

        Example::

            >>> client.modify_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw',
            ...     star=True,
            ...     read=False,
            ...     entities=[],
            ...     keywords={'Canton': ['Zurich'], 'Topic': None,
            ...               'sports': [{'hockey', 0.9}, {'baseball', 0.1}]

        """

        if force_cache_clear:
            deprecation(
                "`force_cache_clear` is the default behavior now. This"
                "parameter is not needed anymore"
            )

        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/%(item_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "item_id": item_id,
        }

        data = self._build_item_update(star, read, keywords, entities)

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("put", url, data=json.dumps(data), headers=headers)
        self._process_response(res, [204])

    def modify_items(
        self, project_id, items, batch_size=MAX_UPDATE_COUNT, force_cache_clear=None
    ):
        """Updates the flags and/or keywords of a list of items.

        You can only update `star`, `read`, and `keywords`.
        The new values will overwrite all old values.

        :param project_id: Project identifier.
        :param items: List of items.
        :param batch_size: An optional batch size (defaults to MAX_UPDATE_COUNT)
        :param force_cache_clear: Deprecated. This is the default behavior now.
            Force all relevant caches to be cleared

        Example::

            >>> client.modify_items(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', [
            ...     {
            ...         'id': 'haG6fhr9RLCm7ZKz1Meouw',
            ...         'star': True,
            ...         'read': False,
            ...         'keywords': {'Canton': ['Berne'], 'Topic': None,
            ...                      'sports': [{'hockey': 0.3},
            ...                                 {'baseball': 0.5}]
            ...     },
            ...     {
            ...         'id': 'masnnawefna9MMf3lk',
            ...         'star': False,
            ...         'read': True,
            ...         'keywords': {'Canton': ['Zurich'], 'Topic': None,
            ...                      'sports': [{'hockey': 0.9},
            ...                                 {'baseball': 0.1}]
            ...     }],
            ...     batch_size=1000
            ... )

        """
        if force_cache_clear:
            deprecation(
                "`force_cache_clear` is the default behavior now. This"
                "parameter is not needed anymore"
            )

        if batch_size > MAX_UPDATE_COUNT:
            raise ValueError(
                "Batch size of %r > MAX_UPDATE_COUNT %r"
                % (batch_size, MAX_UPDATE_COUNT)
            )

        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        # create item sets
        item_sets = [[]]
        for item in items:
            item_size = sys.getsizeof(item)
            if item_size > MAX_UPDATE_SIZE:
                raise ValueError(
                    "Item size %r > MAX_UPDATE_SIZE %r" % (item_size, MAX_UPDATE_SIZE)
                )
            item_set_size = sys.getsizeof(item_sets[-1])
            if ((item_set_size + item_size) > MAX_UPDATE_SIZE) or (
                len(item_sets[-1]) == batch_size
            ):
                item_sets.append([])  # splitting into another set
            item_sets[-1].append(item)

        # build data package
        for item_set in item_sets:
            data = {"updates": []}
            for item in item_set:
                item_id = item.get("id")
                star = item.get("star")
                read = item.get("read")
                keywords = item.get("keywords")
                entities = item.get("entities")

                update = self._build_item_update(star, read, keywords, entities)

                if not item_id:
                    raise ValueError("Missing field `id` %r" % (item))
                update["id"] = item_id

                data["updates"].append(update)

            headers = {"Content-Type": "application/json"}

            res = self._perform_request(
                "put", url, data=json.dumps(data), headers=headers
            )
            self._process_response(res, [204])

    def delete_item(self, project_id, item_id):
        """Deletes an item.

        :param project_id: Project identifier.
        :param item_id: Item identifier.

        Example::

            >>> client.delete_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw')
        """

        url = (
            "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/items/%(item_id)s"
        )
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
            "item_id": item_id,
        }

        # build params
        params = {}

        res = self._perform_request("delete", url, params=params)
        self._process_response(res, [204])

    #
    #
    # Typeahead
    #

    def get_typeahead_suggestions(
        self,
        project_id,
        searchbar_query,
        cursor_pos,
        max_suggestions=None,
        options=None,
        filter_query=None,
    ):
        """Get the typeahead suggestions for a query `searchbar_query` in the
        project identified by the id `project_id`.

        :param project_id: Project identifier from which the typeahead
            suggestions should be returned.
        :param searchbar_query: The full query that goes into a searchbar. The
            `searchbar_query` will automatically be parsed and the suggestion
            on the field defined by the `cursor_pos` and filtered by the rest
            of the query will be returned. `searchbar_query` can not be None.
        :param cursor_pos: The position in the searchbar_query on which the
            typeahead is needed. `cursor_pos` parameter follow a 0-index
            convention, i.e. the first position in the searchbar-query is 0.
            `cursor_pos` should be a positive integer.
        :param max_suggestions: Maximum number of typeahead suggestions to be
            returned. `max_suggestions` should be a non-negative integer.
        :param options: Dictionary of options that influence the result-set.
            Valid options are:
            - `template_params` dict containing the query template parameters
            - `select_suggesters` (optional) list containing suggesters to be used.
                If no suggesters are selected, all suggesters are executed by default.
                Available suggesters:
                - "facet_value": Complete on facet-values that have "autocomplete" enabled (Exact Search)
                - "facet_name: Help to find the correct facet
                - "content_phrase": Complete on key-phrases + item-title (Fuzzy Search) added via NLP-Tagger
                - "saved_search": Complete on queries saved by the user
                - "popular_query": Complete on popular queries on the project, filtered by user_id (optional)
                - "search_history": Triggered only to pre-populate and show default-suggestions.
                                    Returns last-N searches, filtered by project_id and user_id.
        :param filter_query: Squirro query to limit the typeahead suggestions.
            Must be of type `string`. Defaults to `None` if not specified. As
            an example, this parameter can be used to filter the typeahead
            suggestions by a dashboard query on a Squirro dashboard.

        :returns: A dict of suggestions

        Example::

            # Default usage

            >>> client.get_typeahead_suggestions(project_id='Sz7LLLbyTzy_SddblwIxaA',
            ...                                 searchbar_query='Country:India c',
            ...                                 cursor_pos=15)
            {'suggestions': [
                {'type': 'facetvalue', 'key': 'Country:India
                City:Calcutta', 'value': 'city:Calcutta', 'score': 12,
                'cursor_pos': 26, 'group': 'country'},
                {'type': 'facetvalue', 'key': 'Country:India
                Name:Caesar', 'value': 'name:Caesar', 'score': 8,
                'cursor_pos': 24, 'group': 'country'},
                {'type': 'facetname', 'key': 'Country:India city:',
                'value': 'City', 'score': 6, 'cursor_pos': 19, 'group':
                'Fields'}
            ]}


        Example::

            # Autocomplete on one specific suggester like `content_phrase`
            # - The "content_phrase" suggester completes on key-phrases and item titles added by
            #  `NLP-Tagger <https://squirro.atlassian.net/wiki/spaces/DOC/pages/2396061784/Content-based+Typeahead>`__
            # - Autocompletion supports in-order phrase & fuzzy string matching
            # - Highlighted tokens are returned as <b> html tags (highlight_cursor_start/end is not used)

            >>> client.get_typeahead_suggestions(project_id=project_id,
            ...         searchbar_query="pla",
            ...         cursor_pos=0, # cursor_pos not used for this suggester, but parameter is required on API level
            ...         options={"select_suggesters": ["content_phrase"]})
            {"suggestions":[
                  {
                     "type":"text",
                     "key":" \"plant material\"",
                     "value":"<b>plant</b> material",
                     "group_name":"By Content",
                     "highlight_cursor_start":0,
                     "highlight_cursor_end":0
                  },
                  {
                     "type":"text",
                     "key":" \"plant proteins\"",
                     "value":"<b>plant</b> proteins",
                     "group_name":"By Content",
                     "highlight_cursor_start":0,
                     "highlight_cursor_end":0
                  }]
            }

        """

        # construct the url
        url = "%(ep)s/%(version)s/%(tenant)s" "/projects/%(project_id)s/typeahead"
        url = url % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        # prepare the parameters dict
        params = {}
        params["searchbar_query"] = searchbar_query
        params["cursor_pos"] = cursor_pos
        params["max_suggestions"] = max_suggestions
        params["filter_query"] = filter_query

        if options:
            params["options"] = json.dumps(options)

        # issue request
        res = self._perform_request("get", url, params=params)

        return self._process_response(res)

    #
    # Permission Check
    #

    def assert_permission(
        self, project_id=None, user_permissions=None, project_permissions=None
    ):
        """Ensure the user has the right permissions on the project.

        :param project_id: Project identifier.
        :param user_permissions: User permissions required.
        :param project_permissions: Project permissions required.
        :returns: True if the permissions are met.

        Example::

            >>> client.assert_permissions('2aEVClLRRA-vCCIvnuEAvQ',
            user_permissions='admin')

        Or with multiple permissions (at least one permission needs to match):

            >>> client.assert_permissions('2aEVClLRRA-vCCIvnuEAvQ',
            project_permissions=['items.read', 'project.read'])
        """

        url = ("%(ep)s/%(version)s/%(tenant)s/permission") % {
            "ep": self.topic_api_url,
            "version": self.version,
            "tenant": self.tenant,
        }

        # build params
        params = {
            "project_id": project_id,
            "user_permissions": user_permissions,
            "project_permissions": project_permissions,
        }

        headers = {"Content-Type": "application/json"}
        data = json.dumps(params)
        res = self._perform_request("post", url, headers=headers, data=data)
        # This errors out if permissions are missing
        self._process_response(res, [204])
        return True


class TopicApiMixin(
    TopicApiBaseMixin,
    CommunitiesMixin,
    CommunitySubscriptionsMixin,
    CommunityTypesMixin,
    ConfigurationMixin,
    ContributingRecordsMixin,
    DashboardsMixin,
    EmailTemplatesMixin,
    EntitiesMixin,
    EnrichmentsMixin,
    FacetsMixin,
    FileUploadMixin,
    GlobalTempMixin,
    MachineLearningMixin,
    ObjectsMixin,
    PipelineSectionsMixin,
    PipelineStatusMixin,
    PipelineWorkflowMixin,
    ProjectGuideFilesMixin,
    ProjectTranslationsMixin,
    ProjectsMixin,
    SavedSearchesMixin,
    SmartfiltersMixin,
    SourcesMixin,
    SubscriptionsMixin,
    SynonymsMixin,
    TasksMixin,
    ThemesMixin,
    TrendDetectionMixin,
    WidgetsAndAssetsMixin,
    MLCandidateSetMixin,
    MLGroundTruthMixin,
    MLTemplatesMixin,
    MLModelsMixin,
    MLPublishMixin,
    MLUserFeedbackMixin,
    MLSentenceSplitterMixin,
):
    pass
