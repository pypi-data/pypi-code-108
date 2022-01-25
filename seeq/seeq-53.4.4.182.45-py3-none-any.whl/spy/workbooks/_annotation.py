import io
import json
import os
import re
from typing import Optional, Union

import requests
from bs4 import BeautifulSoup

from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks import _item
from seeq.spy.workbooks import _render
from seeq.spy.workbooks._content import Content, DateRange
from seeq.spy.workbooks._workstep import AnalysisWorkstep


class Annotation:
    def __init__(self, worksheet, annotation_type):
        """
        :type worksheet: Worksheet
        """
        self.annotation_type = annotation_type
        self.worksheet = worksheet
        self._html = ''
        self.images = dict()
        self.plots_to_render = set()
        if not self.id:
            self.id = _common.new_placeholder_guid()

    @property
    def id(self):
        # We store this on the worksheet because it's the only piece of metadata we need for the annotation and it's
        # convenient to have it in the worksheet's JSON when saved.
        return _common.get(self.worksheet, 'Annotation ID')

    @id.setter
    def id(self, _id):
        self.worksheet['Annotation ID'] = _id

    def refresh_from(self, new_item, item_map):
        self.annotation_type = new_item.annotation_type
        # Note that we purposefully don't touch the worksheet reference, since it will have stayed the same
        self.html = new_item.html
        self.images = new_item.images

    def _find_image_references(self):
        if not self.html:
            return list()

        matches = re.finditer(r'src="/api(/annotations/(.*?)/images/(.*?))"', self.html)
        return [(match.group(1), match.group(2), match.group(3)) for match in matches]

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, value):
        self._set_html(value)

    def _set_html(self, value):
        if value is None:
            self._html = ''
        else:
            self._html = value

    @property
    def referenced_items(self):
        return list()

    @property
    def referenced_worksteps(self):
        return self._find_workstep_references()

    def _find_workstep_references(self):
        return set()

    def find_workbook_links(self, session: Session):
        if not self.html:
            return dict()

        url = _common.get(self.worksheet.workbook, 'Original Server URL')
        if not url:
            return dict()

        # TODO can this be converted to use the _common.workbook_worksheet_url_regex methods?
        edit_link_no_folder_regex = \
            r'%s/workbook/(?P<workbook>%s)/worksheet/(?P<worksheet>%s)' % (url,
                                                                           _common.GUID_REGEX,
                                                                           _common.GUID_REGEX)

        edit_link_with_folder_regex = \
            r'%s/%s/workbook/(?P<workbook>%s)/worksheet/(?P<worksheet>%s)' % (url,
                                                                              _common.GUID_REGEX,
                                                                              _common.GUID_REGEX,
                                                                              _common.GUID_REGEX)

        view_link_regex = \
            r'%s/view/(?P<worksheet>%s)' % (url, _common.GUID_REGEX)

        present_link_regex = \
            r'%s/present/worksheet/(?P<workbook>%s)/(?P<worksheet>%s)' % (url,
                                                                          _common.GUID_REGEX,
                                                                          _common.GUID_REGEX)

        workstep_tuples = dict()
        for regex in [edit_link_no_folder_regex, edit_link_with_folder_regex, view_link_regex, present_link_regex]:
            matches = re.finditer(regex, self.html, re.IGNORECASE)

            for match in matches:
                group_dict = dict(match.groupdict())
                if 'workbook' not in group_dict:
                    items_api = ItemsApi(session.client)
                    item_output = items_api.get_item_and_all_properties(
                        id=group_dict['worksheet'])  # type: ItemOutputV1
                    href_regex = r'/workbooks/(?P<workbook>%s)/worksheets/(?P<worksheet>%s)' % (_common.GUID_REGEX,
                                                                                                _common.GUID_REGEX)
                    group_dict['workbook'] = re.fullmatch(href_regex, item_output.href).group('workbook')

                if group_dict['workbook'].upper() not in workstep_tuples:
                    workstep_tuples[group_dict['workbook'].upper()] = set()

                workstep_tuples[group_dict['workbook'].upper()].add(
                    (group_dict['workbook'].upper(), group_dict['worksheet'].upper(), None))

        return workstep_tuples

    def pull(self, session: Session, *, include_images=True):
        session = Session.validate(session)
        self.images = dict()
        annotations_api = AnnotationsApi(session.client)
        annotations = annotations_api.get_annotations(
            annotates=[self.worksheet.id])  # type: AnnotationListOutputV1

        annotation_output = None
        for annotation_item in annotations.items:  # type: AnnotationOutputV1
            candidate = annotations_api.get_annotation(id=annotation_item.id)  # AnnotationOutputV1
            if candidate.type == self.annotation_type:
                annotation_output = candidate
                break

        if not annotation_output:
            # This seems possible (although rare) and it seems like the annotation gets created immediately if the
            # user clicks on the Journal tab. So just return nothing but allow this Annotation object to persist with
            # a placeholder ID.
            return None

        self.id = annotation_output.id
        self._set_html(annotation_output.document)

        if include_images:
            image_references = self._find_image_references()
            for query_params, annotation_id, image_id in image_references:
                if (annotation_id, image_id) in self.images:
                    continue

                self.worksheet.workbook.update_status('Pulling image', 1)

                api_client_url = session.get_api_url()
                request_url = api_client_url + query_params

                self.images[(annotation_id, image_id)] = _login.pull_image(session, request_url)

        return annotation_output

    def push(self, session: Session, pushed_workbook_id, pushed_worksheet_id, item_map, datasource_output,
             push_images, label, item_push_errors=None):
        self.render_plots()

        bs = BeautifulSoup(self.html, features='html.parser')
        find_result = bs.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title'])
        name = 'Unnamed'
        description = None

        if len(find_result) > 0:
            name = ' '.join(re.split(r'[\s\n]+', find_result[0].get_text().strip())[:20])
        if len(find_result) > 1:
            description = ' '.join(re.split(r'[\s\n]+', find_result[1].get_text().strip())[:50])

        new_annotation = AnnotationInputV1()
        new_annotation.document = ''
        new_annotation.name = name if len(name.strip()) > 0 else 'Unnamed'
        new_annotation.description = description
        new_annotation.type = self.annotation_type

        annotations_api = AnnotationsApi(session.client)
        annotations = annotations_api.get_annotations(
            annotates=[pushed_worksheet_id])  # type: AnnotationListOutputV1

        relevant_annotations = [a for a in annotations.items if a.type == self.annotation_type]
        if len(relevant_annotations) == 0:
            if isinstance(self, Report):
                # In 49+, creating a report requires an OptionalReportInputV1
                new_annotation.report_input = OptionalReportInputV1()
            else:
                new_annotation.interests = [
                    AnnotationInterestInputV1(interest_id=pushed_worksheet_id)
                ]

                if isinstance(self, Journal):
                    # Reports cannot have an interest to the workbook, see CRAB-18738
                    new_annotation.interests.append(AnnotationInterestInputV1(interest_id=pushed_workbook_id))

            relevant_annotation = annotations_api.create_annotation(body=new_annotation)  # type: AnnotationOutputV1
        else:
            relevant_annotation = relevant_annotations[0]

        item_map[self.id.upper()] = relevant_annotation.id

        if push_images:
            for query_params, annotation_id, image_id in self._find_image_references():
                api_client_url = session.get_api_url()
                request_url = api_client_url + '/annotations/%s/images' % relevant_annotation.id

                self.worksheet.workbook.update_status('Pushing image', 1)

                response = requests.post(url=request_url,
                                         files={
                                             "file": (image_id, io.BytesIO(self.images[(annotation_id, image_id)]))
                                         },
                                         headers={
                                             "Accept": "application/vnd.seeq.v1+json",
                                             "x-sq-auth": session.client.auth_token
                                         },
                                         verify=session.https_verify_ssl)

                if response.status_code != 201:
                    raise SPyRuntimeError(
                        f'Could not upload image file {image_id} for worksheet {pushed_worksheet_id}:\n'
                        f'Response code: {response.status_code}\n'
                        f'Response content: {response.content}')

                link_json = json.loads(response.content)

                match = re.match(r'.*?images/(.*)', link_json['link'])
                new_image_id = match.group(1)

                item_map[image_id] = new_image_id

        self._push_specific(session, item_map, datasource_output, label, new_annotation, relevant_annotation,
                            item_push_errors)

        doc = self.html

        # When a workbook is duplicated via the Workbench UI, the workstep links within Journals actually refer to
        # the original workbook. This works in the UI because workstep content has no real dependency on the
        # workbook/worksheet they're associated with. When pulling, we accommodate this by pulling a Workstep and
        # associating it with the "proper" Worksheet object, but then during push we have to fix up the links in case
        # the "original" workbook/worksheet wasn't included in the workbooks to be pushed.
        workstep_map = _common.get(item_map, self.worksheet.item_map_worksteps_key())
        if workstep_map:
            doc = _item.replace_items(doc, workstep_map)

        doc = _item.replace_items(doc, item_map)

        worksheet_link_replacement = r'links?type=workstep&amp;workbook=%s&amp;worksheet=%s&amp;' % (
            pushed_workbook_id, pushed_worksheet_id
        )

        doc = re.sub(_common.WORKSHEET_LINK_REGEX, worksheet_link_replacement, doc, flags=re.IGNORECASE)

        original_server_url = _common.get(self.worksheet.workbook, 'Original Server URL')
        new_server_url = _item.get_canonical_server_url(session)
        if len(doc) > 0 and original_server_url:
            doc = doc.replace(original_server_url, new_server_url)

        new_annotation.document = doc
        new_annotation.interests = list()
        for interest in relevant_annotation.interests:  # type: AnnotationInterestOutputV1
            interest_item = interest.item  # type: ItemPreviewV1
            # At Chevron, we encountered a case where there were multiple interests returned with the same ID, which
            # caused Appserver to choke when updating the annotation. So filter those out.
            if any(interest_item.id == i.interest_id for i in new_annotation.interests):
                continue
            if isinstance(self, Report) and interest_item.id == pushed_workbook_id:
                # Reports cannot have an interest to the workbook, see CRAB-18738
                continue
            new_interest = AnnotationInterestInputV1()
            new_interest.interest_id = interest_item.id
            new_interest.detail_id = interest.capsule
            new_annotation.interests.append(new_interest)

        new_annotation.created_by_id = relevant_annotation.created_by.id

        annotations_api.update_annotation(id=relevant_annotation.id, body=new_annotation)  # type: AnnotationOutputV1

    def _push_specific(self, session: Session, item_map, datasource_output, label, new_annotation, annotation,
                       item_push_errors=None):
        # This will be overridden in derived classes to do some specific work like pushing Content and DateRanges
        pass

    def _get_annotation_file(self, workbook_folder):
        return os.path.join(workbook_folder, '%s_%s' % (self.annotation_type, self.worksheet.id))

    @staticmethod
    def _get_image_file(workbook_folder, image_id_tuple):
        return os.path.join(workbook_folder, 'Image_%s_%s' % image_id_tuple)

    @staticmethod
    def _get_html_attr(fragment, attribute):
        attr_match = re.findall(r'\s+%s="(.*?)"' % attribute, fragment)
        return attr_match[0] if len(attr_match) > 0 else None

    def save(self, workbook_folder, *, include_rendered_content=False, pretty_print_html=False):
        self.render_plots()
        html_file = f'{self._get_annotation_file(workbook_folder)}.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            if self.html:
                if pretty_print_html:
                    html_to_save = BeautifulSoup(self.html, features='html.parser').prettify()
                    # If we don't trim the spaces within <a> tags, you'll get extra spaces underlined in the UI
                    html_to_save = re.sub(r'(<a .*?>)[\s\n]+(.*?)[\s\n]+(</a>)', r'\1\2\3', html_to_save)
                else:
                    html_to_save = self.html

                f.write(html_to_save)

        _common.save_image_files(self.images, workbook_folder)

    def _load(self, workbook_folder):
        html_file = f'{self._get_annotation_file(workbook_folder)}.html'

        with open(html_file, 'r', encoding='utf-8') as f:
            self.html = f.read()

        matches = re.finditer(r'src="/api(/annotations/(.*?)/images/(.*?))"', self.html)
        for match in matches:
            image_id_tuple = (match.group(2), match.group(3))
            image_file = _common.get_image_file(workbook_folder, image_id_tuple)

            with open(image_file, 'rb') as f:
                self.images[image_id_tuple] = f.read()

    def add_image(self, *, filename=None, buffer=None, image_format=None, placement=None, just_src=False):
        """
        Add an image to the annotation.

        Parameters
        ----------
        filename: str
            The full path to the image file
        buffer: str
            The bytes of the image in memory (must also specify image_format)
        image_format
            The image format of what is supplied in bytes (e.g. 'png', 'jpg')
        placement : {'end', 'beginning', None}, default None
            The location to add the image to an existing document.
        just_src : bool
            False if full <img> html tags desired, True if you just want the
            url to put in the <img src="<url>"> attribute yourself.
        """
        if filename and buffer:
            raise SPyValueError('Either filename or buffer must be supplied to image function -- not both')

        if buffer and not image_format:
            raise SPyValueError('image_format must be specified if buffer is supplied')

        if placement not in ['end', 'beginning', None]:
            raise SPyValueError(f"placement must be one of {['end', 'beginning', None]}")

        if placement and just_src:
            raise SPyValueError(f"placement must None if just_src is True")

        html = self.html
        if filename:
            image_name = os.path.basename(filename)
            with open(filename, 'rb') as img:
                self.images[(self.id, image_name)] = img.read()
        else:
            image_name = f'{_common.new_placeholder_guid()}.{image_format}'
            self.images[(self.id, image_name)] = buffer

        url = f'/api/annotations/{self.id}/images/{image_name}'
        if just_src:
            return url

        image_html = f'<img class="fr-fic fr-fin fr-dii" src="{url}">'
        if placement is not None:
            if placement == 'beginning':
                html = image_html + html
            else:
                html += image_html
            self._set_html(html)

        return image_html

    def add_plot_to_render(self, plot_render_info, date_range):
        image_id = _common.new_placeholder_guid()
        filename = f'{image_id}.{plot_render_info.image_format}'
        self.plots_to_render.add((self.id, filename, plot_render_info, date_range))
        return f'<img class="fr-fic fr-fin fr-dii" src="/api/annotations/{self.id}/images/{filename}"/>'

    def render_plots(self):
        for annotation_id, filename, plot_render_info, date_range in self.plots_to_render:
            self.images[annotation_id, filename] = plot_render_info.render_function(date_range)

        self.plots_to_render.clear()


class Journal(Annotation):
    def __init__(self, worksheet):
        super().__init__(worksheet, 'Journal')

    @staticmethod
    def load(worksheet, workbook_folder):
        journal = Journal(worksheet)
        journal._load(workbook_folder)
        return journal

    @property
    def referenced_items(self):
        referenced_items = list()
        if self.html:
            matches = re.finditer(r'item%s(%s)' % (_common.HTML_EQUALS_REGEX, _common.GUID_REGEX), self.html,
                                  re.IGNORECASE)
            for match in matches:
                referenced_items.append(_item.Reference(match.group(1).upper(), _item.Reference.JOURNAL,
                                                        self.worksheet))

        return referenced_items

    def _find_workstep_references(self):
        if not self.html:
            return set()

        workstep_references = set()
        regex = r'workbook%s(%s)&amp;worksheet%s(%s)&amp;workstep%s(%s)' % (
            _common.HTML_EQUALS_REGEX, _common.GUID_REGEX,
            _common.HTML_EQUALS_REGEX, _common.GUID_REGEX,
            _common.HTML_EQUALS_REGEX, _common.GUID_REGEX)
        matches = re.finditer(regex, self.html, re.IGNORECASE)

        for match in matches:
            workstep_references.add((match.group(1).upper(), match.group(2).upper(), match.group(3).upper()))

        return workstep_references


class Report(Annotation):
    rendered_content_images: Optional[dict]

    def __init__(self, worksheet):
        super().__init__(worksheet, 'Report')
        self.rendered_content_images = None

        self.date_ranges = dict()
        self.content = dict()
        self.schedule = None
        self.data = None

    def pull(self, session: Session, include_images=True):
        session = Session.validate(session)
        annotation_output = super().pull(session, include_images=include_images)

        content_api = ContentApi(session.client)
        contents = content_api.get_contents_with_all_metadata(report_id=annotation_output.id)
        for content in contents.content_items:
            new_date_range = None
            if content.date_range is not None:
                new_date_range = DateRange.pull(content.date_range, report=self)
                self.date_ranges[new_date_range.id] = new_date_range

            new_content_definition = {'Name': content.name,
                                      'ID': content.id,
                                      'Width': content.width,
                                      'Height': content.height,
                                      'Workbook ID': content.source_workbook,
                                      'Worksheet ID': content.source_worksheet,
                                      'Workstep ID': content.source_workstep,
                                      'Scale': content.scale,
                                      'selector': content.selector,
                                      'Date Range ID': content.date_range.id if new_date_range is not None else None}

            new_content = Content(new_content_definition, self)
            self.content[new_content.definition['ID']] = new_content

        # Go back through the date range IDs on the annotation in case they aren't associated with any content and
        # therefore won't be in the output from the get_contents_with_all_metadata call.
        for date_range_id in annotation_output.date_range_ids:
            if date_range_id not in self.date_ranges.keys():
                new_date_range = DateRange.pull(date_range_id, report=self)
                self.date_ranges[new_date_range.id] = new_date_range

        # There is a cron schedule only if it is not null or the list is not empty
        if annotation_output.cron_schedule:
            self.schedule = {
                'Cron Schedule': annotation_output.cron_schedule,
                'Background': annotation_output.background
            }

    @staticmethod
    def _refresh_child_dict(existing_item_dict: dict, new_item_dict: dict, item_map: dict):
        existing_items = list(existing_item_dict.values())
        for existing_item in existing_items:
            if existing_item.id not in item_map:
                # The Content or DateRange failed to get pushed. Keep going.
                del existing_item_dict[existing_item.id]
                continue
            new_item_id = item_map[existing_item.id]
            if new_item_id not in new_item_dict:
                continue
            new_item = new_item_dict[new_item_id]

            # Update the map
            del existing_item_dict[existing_item.id]
            existing_item_dict[new_item_id] = existing_item

            # Refresh item itself
            existing_item.refresh_from(new_item, item_map)

    def refresh_from(self, new_item, item_map):
        super().refresh_from(new_item, item_map)

        Report._refresh_child_dict(self.date_ranges, new_item.date_ranges, item_map)
        Report._refresh_child_dict(self.content, new_item.content, item_map)

    def _push_specific(self, session: Session, item_map, datasource_output, label, new_annotation, existing_annotation,
                       item_push_errors=None):
        date_range_ids_to_archive = list(existing_annotation.date_range_ids)
        content_ids_to_archive = list(existing_annotation.content_ids)

        existing_date_ranges = dict()
        for date_range_id in existing_annotation.date_range_ids:
            existing_date_range = DateRange.pull(date_range_id)
            existing_date_ranges[existing_date_range.id] = existing_date_range
            existing_date_ranges[existing_date_range.name] = existing_date_range

        existing_contents = dict()
        for content_id in existing_annotation.content_ids:
            existing_content = Content.pull(content_id)
            existing_contents[existing_content.id] = existing_content
            existing_contents[existing_content.name] = existing_content

        # Pushing date ranges and content has to be done in a couple of steps. First, we push the date ranges and get
        # their corresponding Seeq guids. Then, we update the content to use those date range guids so that we can
        # create content in the backend with the correct date ranges. Next, we update the report input with the newly
        # created content and date range ids to create the association. Finally, we push up the report.
        optional_report = OptionalReportInputV1(enabled=False, cron_schedule=None)

        def _push_it(_item_type, _item_dict, _existing, _ids_to_archive):
            for _item_object in _item_dict.values():  # type: Union[DateRange, AssetSelection, Content]
                try:
                    _item_output = _item_object.push(session, item_map, _existing)
                    if _item_output.id in _ids_to_archive:
                        _ids_to_archive.remove(_item_output.id)
                except ApiException as e:
                    if item_push_errors is not None and e.status == 400:
                        item_push_errors.add(f'Error processing {_item_type}: {_item_object}\n{e.body}')
                    continue

        _push_it('Date Range', self.date_ranges, existing_date_ranges, date_range_ids_to_archive)
        _push_it('Content', self.content, existing_contents, content_ids_to_archive)

        if self.schedule is not None:
            optional_report.enabled = True
            optional_report.background = self.schedule['Background']
            optional_report.cron_schedule = self.schedule['Cron Schedule']

        content_api = ContentApi(session.client)
        items_api = ItemsApi(session.client)
        for content_id_to_archive in content_ids_to_archive:
            content_output = content_api.get_content(id=content_id_to_archive)  # type: ContentOutputV1
            content_api.update_content(id=content_id_to_archive,
                                       body=ContentInputV1(name='SPy archived this!',
                                                           date_range_id=None,
                                                           width=content_output.width,
                                                           height=content_output.height,
                                                           worksheet_id=content_output.source_worksheet,
                                                           workstep_id=content_output.source_workstep,
                                                           selector=content_output.selector,
                                                           report_id=None,
                                                           archived=True))

        for date_range_id_to_archive in date_range_ids_to_archive:
            items_api.archive_item(id=date_range_id_to_archive)

        new_annotation.report_input = optional_report

    def save(self, workbook_folder, *, include_rendered_content=False, pretty_print_html=False):
        super().save(workbook_folder, include_rendered_content=include_rendered_content,
                     pretty_print_html=pretty_print_html)

        json_file = f'{self._get_annotation_file(workbook_folder)}.json'
        json_dict = {
            'Schedule': self.schedule,
            'Date Ranges': [d.definition for d in self.date_ranges.values()],
            'Content': [c.definition for c in self.content.values()]
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=4, sort_keys=True)

        if include_rendered_content:
            _render.save(self, workbook_folder)

    @staticmethod
    def load(worksheet, workbook_folder):
        report = Report(worksheet)
        report._load(workbook_folder)
        return report

    def _load(self, workbook_folder):
        super()._load(workbook_folder)

        json_file = f'{self._get_annotation_file(workbook_folder)}.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            json_dict = json.load(f)

        self.schedule = json_dict['Schedule']

        for date_range_dict in json_dict['Date Ranges']:
            new_date_range = DateRange(date_range_dict, self)
            self.date_ranges[new_date_range.id] = new_date_range

        for content_dict in json_dict['Content']:
            new_content = Content(content_dict, self)
            self.content[new_content.id] = new_content

    def pull_rendered_content(self, session: Session, *, errors='raise', quiet=False, status: Status = None):
        status = Status.validate(status, quiet)
        _render.pull(session, self, errors=errors, quiet=quiet, status=status)

    def get_embedded_content_html(self,
                                  display,  # type: AnalysisWorkstep
                                  date_range=None,  # type: Optional[DateRange]
                                  size='medium',  # type: str
                                  shape='rectangle',  # type: str
                                  width=None,  # type: Optional[int]
                                  height=None,  # type: Optional[int]
                                  scale=1.0,  # type: float
                                  selector=''  # type: str
                                  ):
        # type: (...) -> str
        if width is None and height is None:
            shape = Content.CONTENT_SHAPE[shape]
            width = Content.CONTENT_SIZE[size]
            height = int(width * shape['height'] / shape['width'])
        elif width is None and height is not None:
            raise SPyValueError('You must specify a width if you specify a height')
        elif height is None and width is not None:
            raise SPyValueError('You must specify a height if you specify a width')

        new_content_definition = {'Name': f'SPy_content_{_common.new_placeholder_guid()}',
                                  'Width': width,
                                  'Height': height,
                                  'Workbook ID': display.worksheet.workbook.id,
                                  'Worksheet ID': display.worksheet.id,
                                  'Workstep ID': display.id,
                                  'selector': selector,
                                  'Scale': float(scale)}

        new_content = Content(new_content_definition, self)
        self.content[new_content.id] = new_content

        if date_range is not None:
            existing_date_range = None
            # If a date range with an existing name is input, use that date range for the new content
            for dr in self.date_ranges.values():
                if dr.definition['Name'] == date_range.definition['Name']:
                    existing_date_range = dr

            if existing_date_range is not None:
                new_content.definition['Date Range ID'] = existing_date_range.id
            else:
                new_date_range = DateRange(date_range.definition, self)
                new_content = Content(new_content_definition, self)
                new_content.definition['Date Range ID'] = new_date_range.id
                self.date_ranges[new_date_range.id] = new_date_range

        _html = f'<a href="/api/content/{new_content.id}/sourceUrl" rel="nofollow noopener noreferrer"> ' \
                f'<img data-seeq-content="{new_content.id}" class="report-image-border fr-fic fr-dii contentLoaded ' \
                f'fr-draggable" src="/api/content/{new_content.id}/image"></a>'

        return _html

    def _find_workstep_references(self):
        if not self.html:
            return set()

        workstep_references = set()
        for content in self.content.values():
            workstep_references.add((content.definition['Workbook ID'], content.definition['Worksheet ID'],
                                     content.definition['Workstep ID']))

        return workstep_references
