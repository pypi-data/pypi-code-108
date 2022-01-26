#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import os
import sys
import termios
import time
import signal
import urllib
import re
import tempfile
import urllib.parse

from injector import inject
from requests import ConnectionError
from datetime import datetime
from yams_cli.logic.core.manager import Manager, StaticsPathBuilder, DocumentsPathBuilder, ImagesPathBuilder
from yams_cli.profile import Profile
from yams_cli.utils import generate_pretty_print, id_generator, configure_logging, str2bool, dispatcher_exception_safe, \
    get_directory, get_timestamp, is_not_blank


log = logging.getLogger('yams-cli.dispatcher')

DEFAULT_BUCKET_STATICS = "false"
DEFAULT_BUCKET_MAX_AGE = 2678400  # 31 days


class Dispatcher(object):
    @inject
    def __init__(self, manager: Manager, profile: Profile):
        self._manager = manager
        self._profile = profile

    @property
    def tenant_id(self):
        return self._profile.get_profile_value('tenant_id')

    # ######################################################
    # TENANTS
    # ######################################################

    @dispatcher_exception_safe(Exception)
    def tenant_info(self, args):
        tenant = self._manager.get_tenant(self.tenant_id)
        self.show_result(tenant)
        return True

    @dispatcher_exception_safe(Exception)
    def tenant_list(self, args):
        result = self._manager.get_tenants()
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def tenant_delete(self, args):
        self._manager.delete_tenant(self.tenant_id)
        log.info("Tenant successfully deleted")
        return True

    # ######################################################
    # DISTRIBUTIONS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def distribution_info(self, args):
        distribution_id = args['distribution_id']
        distribution_info = self._manager.get_distribution(self.tenant_id, distribution_id)
        self.show_result(distribution_info)
        return True

    @dispatcher_exception_safe(Exception)
    def distribution_list(self, args):
        result = self._manager.get_distributions(self.tenant_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def distribution_create(self, args):
        dns_name = args['dns_name']
        auto_format = args['auto_format']
        result = self._manager.create_distribution(self.tenant_id, dns_name, auto_format)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def distribution_update(self, args):
        distribution_id = args['distribution_id']
        auto_format = args['auto_format']
        result = self._manager.update_distribution(self.tenant_id, distribution_id, auto_format)
        self.show_result(result)
        log.info("Distribution is in process of being updated")
        return True

    @dispatcher_exception_safe(Exception)
    def distribution_delete(self, args):
        distribution_id = args['distribution_id']
        self._manager.delete_distribution(self.tenant_id, distribution_id)
        log.info("Distribution is in process of being deleted")
        return True

    # ######################################################
    # DOMAINS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def domain_info(self, args):
        domain_id = args['domain_id']
        domain_info = self._manager.get_domain(self.tenant_id, domain_id)
        self.show_result(domain_info)
        return True

    @dispatcher_exception_safe(Exception)
    def domain_list(self, args):
        result = self._manager.get_domains(self.tenant_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def domain_create(self, args):
        domain_name = args['domain_name']
        domain_status = args['domain_status']
        result = self._manager.create_domain(self.tenant_id, domain_name, domain_status)
        self.show_result({
            "tenant_id": result.tenant_id,
            "domain_id": result.domain_id,
            "alias": result.alias
        })
        return True

    @dispatcher_exception_safe(Exception)
    def domain_delete(self, args):
        domain_id = args['domain_id']
        self._manager.delete_domain(self.tenant_id, domain_id)
        log.info("Domain successfully deleted")
        return True

    # ######################################################
    # RULES
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def rule_list(self, args):
        domain_id = args['domain_id']
        result = self._manager.get_rules(self.tenant_id, domain_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def rule_info(self, args):
        domain_id = args['domain_id']
        rule_id = args['rule_id']
        result = self._manager.get_rule(self.tenant_id, domain_id, rule_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def rule_create(self, args):
        domain_id = args['domain_id']
        rule_json = self._get_json_or_none(args, 'rule_json')
        create_rule_result = self._manager.create_rule(self.tenant_id, domain_id, rule_json)
        # log.info("create rule: {}".format(create_rule_result))
        self.show_result({
            "tenant_id": create_rule_result.tenant_id,
            "domain_id": create_rule_result.domain_id,
            "rule_id": create_rule_result.rule_id,
            "alias": create_rule_result.alias
        })
        return True

    @dispatcher_exception_safe(Exception)
    def rule_delete(self, args):
        domain_id = args['domain_id']
        rule_id = args['rule_id']
        self._manager.delete_rule(self.tenant_id, domain_id, rule_id)
        log.info("Rule successfully deleted")
        return True

    @dispatcher_exception_safe(Exception)
    def rule_update(self, args):
        domain_id = args['domain_id']
        rule_id = args['rule_id']
        rule_json = self._get_json_or_none(args, 'rule_json')
        result = self._manager.update_rule(self.tenant_id, domain_id, rule_id, rule_json)
        self.show_result(result)
        return True

    # ######################################################
    # POLICIES
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def policy_list(self, args):
        result = self._manager.get_policies(self.tenant_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def policy_info(self, args):
        policy_id = args['policy_id']
        result = self._manager.get_policy(self.tenant_id, policy_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def policy_create(self, args):
        policy_json = self._get_json_or_none(args, 'policy_json')
        create_policy_result = self._manager.create_policy(self.tenant_id, policy_json)
        self.show_result({
            "tenant_id": create_policy_result.tenant_id,
            "policy_id": create_policy_result.policy_id
        })
        return True

    @dispatcher_exception_safe(Exception)
    def policy_update(self, args):
        policy_json = self._get_json_or_none(args, 'policy_json')
        policy_id = args['policy_id']
        result = self._manager.update_policy(self.tenant_id, policy_id, policy_json)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def policy_delete(self, args):
        policy_id = args['policy_id']
        self._manager.delete_policy(self.tenant_id, policy_id)
        log.info("Policy successfully deleted")
        return True

    # ######################################################
    # ACCESS-KEYS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def accesskey_list(self, args):
        result = self._manager.get_access_keys(self.tenant_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_info(self, args):
        accesskey_id = args['accesskey_id']
        result = self._manager.get_access_key(self.tenant_id, accesskey_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_create(self, args):
        description = args.get('description')
        result = self._manager.create_access_key(self.tenant_id, description)
        self.show_result({
            "tenant_id": result.tenant_id,
            "access_key_id": result.access_key_id,
            "private_key": result.private_key
        })
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_provide(self, args):
        public_key = args['public_key']
        description = args.get('description')
        result = self._manager.provide_access_key(self.tenant_id, public_key, description)
        self.show_result({
            "tenant_id": result.tenant_id,
            "access_key_id": result.access_key_id
        })
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_update(self, args):
        accesskey_id = args['accesskey_id']
        description = args.get('description')
        active = None
        if args.get('enable'):
            active = True
        if args.get('disable'):
            active = False
        result = self._manager.update_access_key(self.tenant_id, accesskey_id, active, description)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_delete(self, args):
        accesskey_id = args['accesskey_id']
        self._manager.delete_access_key(self.tenant_id, accesskey_id)
        log.info("AccessKey successfully deleted")
        return True

    # ######################################################
    # ATTACHED-POLICIES
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def accesskey_list_policies(self, args):
        accesskey_id = args['accesskey_id']
        result = self._manager.get_attached_policies(self.tenant_id, accesskey_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_attach_policy(self, args):
        accesskey_id = args['accesskey_id']
        policy_id = args['policy_id']
        result = self._manager.attach_policy(self.tenant_id, accesskey_id, policy_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def accesskey_detach_policy(self, args):
        accesskey_id = args['accesskey_id']
        policy_id = args['policy_id']
        result = self._manager.detach_policy(self.tenant_id, accesskey_id, policy_id)
        self.show_result(result)
        return True

    # ######################################################
    # WATERMARKS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def watermark_list(self, args):
        domain_id = args['domain_id']
        result = self._manager.list_watermarks(self.tenant_id, domain_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def watermark_fetch(self, args):
        domain_id = args['domain_id']
        watermark_id = args['watermark_id']
        filename = args.get('watermark_file')
        if filename is None:
            if args.get('store_file'):
                filename = '{}/{}'.format(tempfile.gettempdir(), watermark_id)

        result = self._manager.get_watermark(self.tenant_id, domain_id, watermark_id)
        if filename:
            with open(filename, 'wb') as f:
                f.write(result.content)
                log.info("Object file saved at {}".format(filename))
        return True

    @dispatcher_exception_safe(Exception)
    def watermark_create(self, args):
        watermark_file = args['watermark_file']
        alias = args.get('alias')

        if not os.path.exists(watermark_file):
            log.error("Given watermark file does not exist: {}".format(watermark_file))
            return False

        if os.path.isdir(watermark_file):
            log.error("Given watermark file is a directory: {}".format(watermark_file))
            return False

        domain_id = args['domain_id']
        log.info("Uploading watermark '{}' into domain '{}'".format(watermark_file, domain_id))
        with open(watermark_file, 'rb') as f:
            file_data = f.read()
        result = self._manager.create_watermark(self.tenant_id, domain_id, alias, file_data)
        self.show_result({
            "tenant_id": result.tenant_id,
            "domain_id": result.domain_id,
            "watermark_id": result.watermark_id
        })
        return True

    @dispatcher_exception_safe(Exception)
    def watermark_update(self, args):
        domain_id = args['domain_id']
        watermark_id = args['watermark_id']
        alias = args.get('alias')
        result = self._manager.update_watermark(self.tenant_id, domain_id, watermark_id, alias)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def watermark_delete(self, args):
        domain_id = args['domain_id']
        watermark_id = args['watermark_id']
        self._manager.delete_watermark(self.tenant_id, domain_id, watermark_id)
        log.info("Watermark successfully deleted")
        return True

    # ######################################################
    # METRICS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def metrics_list(self, args):
        domain_id = args.get('domain_id')
        bucket_id = args.get('bucket_id')
        result = self._manager.get_bucket_metric_names(self.tenant_id, domain_id, bucket_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def metrics_info(self, args):
        domain_id = args.get('domain_id')
        bucket_id = args.get('bucket_id')
        metric_name = args.get('metric_name')
        year_month = args['year_month']
        result = self._manager.get_bucket_metric(self.tenant_id, domain_id, bucket_id, metric_name, year_month)
        self.show_result(result)
        return True

    # ######################################################
    # BUCKETS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def bucket_list(self, args):
        domain_id = args['domain_id']
        result = self._manager.get_buckets(self.tenant_id, domain_id)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def bucket_info(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        self.show_result(self._manager.get_bucket(self.tenant_id, domain_id, bucket_id))
        return True

    @dispatcher_exception_safe(Exception)
    def bucket_create(self, args):
        domain_id = args['domain_id']
        bucket_name = args['bucket_name']
        bucket_continent = args['bucket_continent']

        bucket_statics = args.get('bucket_statics')
        if bucket_statics is None:
            bucket_statics = DEFAULT_BUCKET_STATICS
        bucket_statics = str2bool(bucket_statics)

        bucket_cache_max_age = args.get('bucket_cache_max_age')
        if bucket_cache_max_age is None:
            bucket_cache_max_age = DEFAULT_BUCKET_MAX_AGE

        result = self._manager.create_bucket(self.tenant_id, domain_id, bucket_name, bucket_continent,
                                             bucket_statics, bucket_cache_max_age)
        self.show_result({
            "tenant_id": result.tenant_id,
            "domain_id": result.domain_id,
            "bucket_id": result.bucket_id,
            "alias": result.alias
        })
        return True

    @dispatcher_exception_safe(Exception)
    def bucket_update(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        bucket_name = args.get('bucket_name')
        bucket_cache_max_age = args.get('bucket_cache_max_age')

        bucket_statics = args.get('bucket_statics')
        if bucket_statics:
            bucket_statics = str2bool(bucket_statics)

        result = self._manager.update_bucket(self.tenant_id, domain_id, bucket_id, bucket_name,
                                             bucket_statics, bucket_cache_max_age)
        self.show_result(result)
        return True

    @dispatcher_exception_safe(Exception)
    def bucket_delete(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        self._manager.delete_bucket(self.tenant_id, domain_id, bucket_id)
        log.info("Bucket successfully deleted")
        return True

    # ######################################################
    # OBJECTS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def object_describe(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']

        print(self._manager.head_object(self.tenant_id, domain_id, bucket_id, object_id))
        return True

    @dispatcher_exception_safe(Exception)
    def object_fetch(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        filename = args.get('directory')
        if filename is None:
            filename = "{}".format(urllib.parse.unquote(object_id))
        else:
            filename += "/{}".format(urllib.parse.unquote(object_id))

        filename = re.sub(r"/+", "/", filename)

        if "/" in filename:
            directory = get_directory(filename)

            if not os.path.exists(directory):
                os.makedirs(directory)

        get_object_result = self._manager.get_object(self.tenant_id, domain_id, bucket_id, object_id)
        with open(filename, 'wb') as f:
            if get_object_result.content is not None and len(get_object_result.content) > 0:
                f.write(get_object_result.content)
            log.info("Object file saved at {}".format(filename))
        return True

    @dispatcher_exception_safe(Exception)
    def object_list(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        options = {}
        if args.get("show_recoverable"):
            options["show-recoverable"] = True

        if args.get('prefix'):
            options['prefix'] = args['prefix']

        if args.get('list_backup'):
            options['list-backup'] = True

        if args.get('start_date'):
            options['start-date'] = get_timestamp(args['start_date'])

        if args.get('end_date'):
            options['end-date'] = get_timestamp(args['end_date'])

        self.print_object_header(args)

        token = None
        while True:
            content = self._manager.list_objects(self.tenant_id, domain_id, bucket_id, options, token)

            token = content.get('continuation_token')
            objects = content.get('objects')

            for record in objects:
                self.print_object_record(record, args)

            if token is None:
                break

        return True

    @staticmethod
    def print_object_header(args):
        if args.get('with_headers'):
            line = "object_id"
            if args.get('long'):
                line = "size\tmd5\tlast_modified\tobject_id"

            if args.get('show_recoverable'):
                line += "\tdeleted"

            print(line)

    @staticmethod
    def print_object_record(record, args):
        line = record.get('object_id')
        if args.get('long'):
            ts = int(record.get('last_modified') / 1000)
            date_formatted = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            line = "{}\t{}\t{}\t{}".format(record.get('size'), record.get('md5'), date_formatted,
                                           record.get('object_id'))

        if args.get('show_recoverable'):
            line += "\t{}".format(record.get('deleted'))

        print(line)

    @dispatcher_exception_safe(Exception)
    def object_push(self, args):
        file_or_directory = args['object']
        if not os.path.exists(file_or_directory):
            log.error("Given file or path does not exist: {}".format(file_or_directory))
            return False

        domain_id = args['domain_id']
        bucket_id = args['bucket_id']

        expiration = args.get('expiration')
        if os.path.isdir(file_or_directory):
            recursive = args.get('recursive')
            if not recursive:
                log.error("Object path {} is a directory but --recursive was not set".format(file_or_directory))
                return False

            files = os.listdir(file_or_directory)

            for idx, file_name_dir in enumerate(files):
                files[idx] = os.path.join(file_or_directory, file_name_dir)

            files = filter(os.path.isfile, files)
            idx = 0
            result = True
            for file_name in files:
                log.info("Uploading {} into {}".format(file_name, bucket_id))
                result &= self._object_push(domain_id, bucket_id, file_name, "image_{}".format(idx), expiration)
                log.info("Uploaded {} into {}".format(file_name, bucket_id))
                idx += 1
            return result
        else:
            object_name = args['object_name']
            return self._object_push(domain_id, bucket_id, file_or_directory, object_name, expiration)

    def _object_push(self, domain_id, bucket_id, file_path, object_name=None, expiration=None):
        log.debug("Filename: {}".format(file_path))
        result = self._manager.put_object(self.tenant_id, domain_id, bucket_id, object_name, file_path, expiration)
        self.show_result({
            "tenant_id": result.tenant_id,
            "domain_id": result.domain_id,
            "bucket_id": result.bucket_id,
            "object_id": result.object_id
        })
        return True

    @dispatcher_exception_safe(Exception)
    def object_remove(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        force = args.get('force', False)

        self._manager.delete_object(self.tenant_id, domain_id, bucket_id, object_id, force)
        return True

    # @dispatcher_exception_safe(Exception)
    def object_restore(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']

        self._manager.delete_delete_marker(self.tenant_id, domain_id, bucket_id, object_id)
        return True

    @dispatcher_exception_safe(Exception)
    def object_uncache(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']

        self.show_result(self._manager.uncache_object(self.tenant_id, domain_id, bucket_id, object_id))
        return True

    # ######################################################
    # OBJECTS METADATA
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def object_metadata_info(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']

        self.show_result(self._manager.get_object_metadata(self.tenant_id, domain_id, bucket_id, object_id))
        return True

    def object_metadata_update(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        expiration = args.get('expiration')
        self._manager.update_object_metadata(self.tenant_id, domain_id, bucket_id, object_id, expiration)
        return True

    # ######################################################
    # ML MODELS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def processing_start(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        models = args['models'].split(',')

        self.show_result(self._manager.processing_start(self.tenant_id, domain_id, bucket_id, object_id, models))
        return True

    @dispatcher_exception_safe(Exception)
    def processing_sync(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        models = args['models'].split(',')

        self.show_result(self._manager.processing_sync(self.tenant_id, domain_id, bucket_id, object_id, models))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_list(self, args):
        self.show_result(self._manager.get_models_list(self.tenant_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_list(self, args):
        self.show_result(self._manager.get_models_config_list(self.tenant_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_info(self, args):
        config_id = args['config_id']
        self.show_result(self._manager.get_model_config_info(self.tenant_id, config_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_create(self, args):
        config = args['config']
        self.show_result(self._manager.post_model_config(self.tenant_id, config))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_delete(self, args):
        config_id = args['config_id']
        self.show_result(self._manager.delete_model_config(self.tenant_id, config_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_list_attached(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']

        self.show_result(self._manager.list_attached_model_configs(self.tenant_id, domain_id, bucket_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_attach(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        config_id = args['config_id']

        self.show_result(self._manager.attach_model_config(self.tenant_id, domain_id, bucket_id, config_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_detach(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        config_id = args['config_id']

        self.show_result(self._manager.detach_model_config(self.tenant_id, domain_id, bucket_id, config_id))
        return True

    @dispatcher_exception_safe(Exception)
    def ml_models_config_replace(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        config_id_from = args['config_id_from']
        config_id_to = args['config_id_to']

        self.show_result(self._manager.replace_model_config(self.tenant_id, domain_id, bucket_id, config_id_from,
                                                            config_id_to))
        return True

    # ######################################################
    # IMAGES
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def image_fetch(self, args):
        rule_id = args.get('rule_id')
        rule_json = args.get('rule_json')

        path_builder = ImagesPathBuilder(
            tenant_id=self.tenant_id,
            domain_id=args.get('domain_id'),
            bucket_id=args.get('bucket_id'),
            bucket_alias=args.get('bucket_alias'),
            object_id=args['object_id']
        )

        if path_builder.can_create_path():
            if rule_id:
                self._print_url(self._manager.fetch_object(path_builder, rule_id))
            elif rule_json:
                rule_json = json.loads(rule_json)
                self._print_url(
                    self._manager.fetch_object_with_rule(path_builder, rule_json))
            else:
                log.warning("When fetching an image, --rule-id or --rule-json must be provided")
                return False
        else:
            log.warning(path_builder.error_message())
            return False

        return True

    # ######################################################
    # DOCUMENTS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def document_fetch(self, args):
        rule_id = args.get('rule_id')
        rule_json = args.get('rule_json')

        path_builder = DocumentsPathBuilder(
            tenant_id=self.tenant_id,
            domain_id=args.get('domain_id'),
            bucket_id=args.get('bucket_id'),
            bucket_alias=args.get('bucket_alias'),
            object_id=args['object_id']
        )

        if path_builder.can_create_path():
            if rule_id:
                self._print_url(self._manager.fetch_document(path_builder, rule_id))
            elif rule_json:
                rule_json = json.loads(rule_json)
                self._print_url(
                    self._manager.fetch_document_with_rule(path_builder, rule_json))
            else:
                log.warning("When fetching a document, --rule-id or --rule-json must be provided")
                return False
        else:
            log.warning(path_builder.error_message(self))
            return False

        return True

    # ######################################################
    # STATICS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def static_fetch(self, args):
        path_builder = StaticsPathBuilder(
            tenant_id=self.tenant_id,
            domain_id=args.get('domain_id'),
            bucket_id=args.get('bucket_id'),
            bucket_alias=args.get('bucket_alias'),
            object_id=args['object_id']
        )

        if path_builder.can_create_path():
            self._print_url(self._manager.fetch_static_object(path_builder))
        else:
            log.warning(path_builder.error_message(self))
            return False

        return True

    # ######################################################
    # VIDEOS
    # ######################################################
    @dispatcher_exception_safe(Exception)
    def video_processing_start(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        object_id = args['object_id']
        self.show_result(self._manager.start_video_processing(self.tenant_id, domain_id, bucket_id, object_id))
        return True

    @dispatcher_exception_safe(Exception)
    def video_processing_status(self, args):
        domain_id = args['domain_id']
        bucket_id = args['bucket_id']
        processing_id = args['processing_id']
        self.show_result(self._manager.video_processing_status(self.tenant_id, domain_id, bucket_id, processing_id))
        return True

    # ######################################################
    # CONFIGURE
    # ######################################################
    def configure(self, args):
        """ Helper to create and configure credentials file.
        :param args:
        :return:
        """

        signal.signal(signal.SIGINT, self._signal_handler)

        # create credentials file if it doesn't exist
        created = self._profile.create_credentials_file_if_needed()
        tenant_id = input('[>] YAMS Tenant ID [{}]: '.format(self._profile.get_profile_value_or_none('tenant_id')))
        access_key_id = input("[>] YAMS Access Key ID [{}]: ".format(
            '****' if self._profile.get_profile_value_or_none('access_key_id') else "None"))

        private_secret_key = self._raw_input("[>] YAMS Private Key [{}]: ".format(
            '****' if self._profile.get_profile_value_or_none('private_secret_key') else "None"))

        # once profile data recollected, create in profile file if it doesn't exist
        self._profile.create_profile(tenant_id, access_key_id, private_secret_key)

        print("[!] Profile file {} successfully!".format("created" if created else "updated"))
        return True

    def _raw_input(self, message):
        fd = sys.stdin.fileno()
        new_attrs = termios.tcgetattr(fd)
        old_attrs = termios.tcgetattr(fd)

        # New terminal setting unbuffered
        new_attrs[3] = (new_attrs[3] & ~termios.ICANON)
        termios.tcsetattr(fd, termios.TCSAFLUSH, new_attrs)
        try:
            return input(message)
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, old_attrs)

    def _print_url(self, url):
        print("URL: {}".format(url))

    @staticmethod
    def _signal_handler(signum, frame):
        print("\n[I] Captured ^C signal. Aborting.")
        Dispatcher._show_goodbye()

    @staticmethod
    def show_result(result):
        try:
            print(generate_pretty_print(result))
        except ValueError:
            log.info("Content is binary and is not shown here")
            # raising a value error con content is because it's downloading a binary
            pass

    @staticmethod
    def _show_extra_options(starting_idx):
        if starting_idx == 0:
            print("Allowed actions:")
        else:
            print("Or:")
        print("   {}. Create new one".format(starting_idx))
        print("   {}. Exit".format(starting_idx + 1))

    @staticmethod
    def _show_goodbye():
        print('')
        print(' .d8888b.                         888 888                         888')
        print('d88P  Y88b                        888 888                         888')
        print('888    888                        888 888                         888')
        print('888         .d88b.   .d88b.   .d88888 88888b.  888  888  .d88b.   888')
        print('888  88888 d88""88b d88""88b d88" 888 888 "88b 888  888 d8P  Y8b  888')
        print('888    888 888  888 888  888 888  888 888  888 888  888 88888888  Y8P')
        print('Y88b  d88P Y88..88P Y88..88P Y88b 888 888 d88P Y88b 888 Y8b.       " ')
        print(' "Y8888P88  "Y88P"   "Y88P"   "Y88888 88888P"   "Y88888  "Y8888   888')
        print('                                                    888              ')
        print('                                               Y8b d88P              ')
        print('                                                "Y88P"               ')

        sys.exit(0)

    # ######################################################
    # UTILS
    # ######################################################
    @staticmethod
    def _get_json_or_none(args, param):
        if not args.get(param):
            return None
        return json.loads(args[param])
