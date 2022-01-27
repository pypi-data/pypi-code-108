import os
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import click
import requests
from tabulate import tabulate

from montecarlodata.config import Config
from montecarlodata.errors import manage_errors, complain_and_abort
from montecarlodata.fs_utils import mkdirs
from montecarlodata.insights.fields import EXPECTED_GET_INSIGHTS_FIELD, FILE_SCHEME, S3_SCHEME, \
    EXPECTED_GET_REPORT_FIELD, INSIGHTS_DEFAULT_EXTENSION, SCHEME_DELIM, LIST_INSIGHTS_HEADERS
from montecarlodata.queries.insights import GET_INSIGHTS, GET_INSIGHT_REPORT
from montecarlodata.utils import GqlWrapper, AwsClientWrapper


class InsightsService:

    def __init__(self, config: Config, request_wrapper: Optional[GqlWrapper] = None):
        self._abort_on_error = True
        self._profile = config.aws_profile

        self._request_wrapper = request_wrapper or GqlWrapper(mcd_id=config.mcd_id, mcd_token=config.mcd_token)

        self.scheme_handler = {
            FILE_SCHEME: self._save_insight_to_disk,
            S3_SCHEME: self._save_insight_to_s3
        }

    @manage_errors
    def echo_insights(self, headers: Optional[str] = 'firstrow', table_format: Optional[str] = 'fancy_grid') -> None:
        """
        Echo insights as a pretty table
        """
        table = [LIST_INSIGHTS_HEADERS]
        for insight in self._request_wrapper.make_request_v2(query=GET_INSIGHTS,
                                                             operation=EXPECTED_GET_INSIGHTS_FIELD).data:
            table.append(
                [
                    insight.title,
                    insight.description if insight.description.endswith('.') else f'{insight.description}.',
                    insight.available
                ]
            )
        click.echo(tabulate(table, headers=headers, tablefmt=table_format))

    @manage_errors
    def get_insight(self, insight: str, destination: str, aws_profile: Optional[str] = None,
                    dry: Optional[bool] = False) -> None:
        """
        Get insight, if available, and either persist to S3 or local file system
        """
        parsed_destination = urlparse(destination)
        scheme = parsed_destination.scheme
        netloc_with_path = parsed_destination.geturl().replace(f'{scheme}{SCHEME_DELIM}', '', 1)

        try:
            handler = self.scheme_handler[scheme]
        except KeyError:
            complain_and_abort('Scheme either missing or not supported.')
        else:
            insight_url = self._get_insight_url(insight=insight)
            if dry:
                click.echo(insight_url)
                return
            click.echo(f'Saving insight to \'{destination}\'.')
            handler(insight_url=insight_url, destination=netloc_with_path, aws_profile=aws_profile)
            click.echo('Complete. Have a nice day!')

    def _get_insight_url(self, insight: str) -> str:
        """
        Get insight URL from the monolith
        """
        url = self._request_wrapper.make_request_v2(
            query=GET_INSIGHT_REPORT,
            operation=EXPECTED_GET_REPORT_FIELD,
            variables=dict(
                insight_name=insight,
                report_name=str(Path(insight).with_suffix(INSIGHTS_DEFAULT_EXTENSION))
            )
        ).data.url
        if not url:
            complain_and_abort('Insight not found. This insight might not be available for your account.')
        return url

    def _save_insight_to_disk(self, insight_url: str, destination: str, **kwargs) -> None:
        """
        Save insight to the local filesystem
        """
        if not destination:
            complain_and_abort(f'Invalid path. Expected format: \'{FILE_SCHEME}{SCHEME_DELIM}folder/file.csv\'')
        mkdirs(os.path.dirname(destination))
        urllib.request.urlretrieve(insight_url, destination)

    def _save_insight_to_s3(self, insight_url: str, destination: str, aws_profile: Optional[str] = None) -> None:
        """
        Save insight to S3
        """
        try:
            bucket, key = destination.split('/', maxsplit=1)
            if not key:
                raise ValueError
        except (ValueError, AttributeError):
            complain_and_abort(f'Invalid path. Expected format: \'{S3_SCHEME}{SCHEME_DELIM}bucket/key.csv\'')
        else:
            AwsClientWrapper(profile_name=aws_profile or self._profile).upload_stream_to_s3(
                data=requests.get(insight_url, stream=True).raw,
                bucket=bucket,
                key=key
            )
