from fair_dynamic_rec.core.util.errors import InvalidConfiguration
from fair_dynamic_rec.core.util.files import Files
from fair_dynamic_rec.core.util.xml_utils import xml_load_from_path
from pathlib import Path
import itertools

class ConfigCmd:
    """
    Loads the configuration file, inserts appropriate library contents,
    identifies the parameter variations and creates separate configurations
    for all combinations.
    """

    # _PARAM_NAME_PATH_RE = ".+\[@name='(.+)'\]"
    # _CV_DIR_RE = "cv_\d+"

    def __init__(self, config_file, target, log_filename=None):
        self._files = Files()
        self._target = target
        # self._log_filename = log_filename
        # self._count = None
        #
        self._files.set_study_path(target)
        self._files.set_config_file(config_file)
        # self._files.create_temp_dir()

        self._xml_input = self.read_xml(self._files.get_config_file_path())
        if self._xml_input is None:
            raise InvalidConfiguration('Parsing of config file failed.')
        # xml_data.findall('rec-alg/item-reg/value')
        # self.protected_features = ProtectedFeature(ProtectedFeature.parse_protected(self), self._files.get_temp_dir_path())
        #
        # if self.is_valid():
        #     self._files.set_data_path(self._xml_input)
        #     self._var_coll = VarColl()
        #     self._libraries = LibraryColl()
        #     self._bbo_steps = 0
        #
        #     self._key_password = None

        # self.ranker_config = self.get_rankers()

        self.seed = self.get_random_seed()

        self.rankers = self.get_ranker_params()
        self.simulator_name = self.get_simulator()
        if self.simulator_name == 'onlinesimulator':
            self.get_online_simulator_settings()

    def get_target(self):
        return self._target

    def set_target(self, target):
        self._target = target

    def get_random_seed(self):
        return int(self._xml_input.findall('random-seed')[0].text)

    def get_general(self):
        return

    def get_data_path(self):
        return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text)
    def get_rating_file_path(self):
        if self._xml_input.findall('data/rating-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/rating-file')[0].text
        return None
    def get_train_file_path(self):
        if self._xml_input.findall('data/train-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/train-file')[0].text
        return None
    def get_test_file_path(self):
        if self._xml_input.findall('data/test-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/test-file')[0].text
        return None
    def get_user_file_path(self):
        if self._xml_input.findall('data/user-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/user-file')[0].text
        return None
    def get_item_file_path(self):
        if self._xml_input.findall('data/item-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/item-file')[0].text
        return None
    def get_supplier_file_path(self):
        if self._xml_input.findall('data/supplier-file'):
            return self.get_target() / Path(self._xml_input.findall('data/data-dir')[0].text) / self._xml_input.findall('data/supplier-file')[0].text
        return None

    def get_rating_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/rating-file')[0].attrib['delimiter']).decode("unicode_escape")
    def get_train_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/train-file')[0].attrib['delimiter']).decode("unicode_escape")
    def get_test_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/test-file')[0].attrib['delimiter']).decode("unicode_escape")
    def get_user_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/user-file')[0].attrib['delimiter']).decode("unicode_escape")
    def get_item_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/item-file')[0].attrib['delimiter']).decode("unicode_escape")
    def get_supplier_data_delimiter(self):
        return str.encode(self._xml_input.findall('data/supplier-file')[0].attrib['delimiter']).decode("unicode_escape")

    def get_item_data_category_column(self):
        return int(self._xml_input.findall('data/item-file')[0].attrib['category_column'])
    def get_item_data_category_delimiter(self):
        return self._xml_input.findall('data/item-file')[0].attrib['category_delimiter']

    def get_splitter_model(self):
        splitter_model = 'splittraintest'
        if self._xml_input.findall('splitter/model'):
            splitter_model = self._xml_input.findall('splitter/model')[0].text
        return splitter_model
    def get_sampling_model(self):
        sampling_model = None
        if self._xml_input.findall('splitter/sampling'):
            sampling_model = self._xml_input.findall('splitter/sampling')[0].text
            if 'max-user' in self._xml_input.findall('splitter/sampling')[0].attrib:
                self.max_user = int(self._xml_input.findall('splitter/sampling')[0].attrib['max-user'])
            if 'max-item' in self._xml_input.findall('splitter/sampling')[0].attrib:
                self.max_item = int(self._xml_input.findall('splitter/sampling')[0].attrib['max-item'])
        return sampling_model
    def get_splitter_model_traintest_ratio(self):
        ratio = 0.5
        if self._xml_input.findall('splitter/model'):
            ratio = float(self._xml_input.findall('splitter/model')[0].attrib['ratio'])
        return ratio
    def get_data_binarization(self):
        binarize = False
        one_if_greater_than = 0
        if self._xml_input.findall('splitter/binarize'):
            binarize = self._xml_input.findall('splitter/binarize')[0].text == 'True'
            if 'one-if-greater-than' in self._xml_input.findall('splitter/binarize')[0].attrib:
                one_if_greater_than = float(self._xml_input.findall('splitter/binarize')[0].attrib['one-if-greater-than'])
        return binarize, one_if_greater_than

    def get_save_txt_data_info(self):
        save_data = False
        train_file_name, test_file_name = 'train.txt', 'test.txt'
        if self._xml_input.findall('splitter/save-txt'):
            save_data = self._xml_input.findall('splitter/save-txt')[0].text == 'True'
            train_file_name = None
            test_file_name = None
            if 'train-file-name' in self._xml_input.findall('splitter/save-txt')[0].attrib:
                train_file_name = self._xml_input.findall('splitter/save-txt')[0].attrib['train-file-name']
            if 'test-file-name' in self._xml_input.findall('splitter/save-txt')[0].attrib:
                test_file_name = self._xml_input.findall('splitter/save-txt')[0].attrib['test-file-name']
        return save_data, train_file_name, test_file_name
    def get_save_pkl_data_info(self):
        save_data = False
        file_name = 'data.pkl'
        if self._xml_input.findall('splitter/save-pkl'):
            save_data = self._xml_input.findall('splitter/save-pkl')[0].text
            file_name = self._xml_input.findall('splitter/save-pkl')[0].attrib['file-name']
        return save_data, file_name

    def get_ranker_params(self):
        rankers = []
        ranker_params = self._xml_input.findall('rankers/ranker')
        for ranker_param in ranker_params:
            ranker_single_val_params = {}
            _ranker_multiple_val_params = {}
            for child in ranker_param:
                if len(child) == 0:
                    ranker_single_val_params[child.tag] = {'value': child.text, 'attr': child.attrib}
                else:
                    _ranker_multiple_val_params[child.tag] = []
                    for i in range(len(child)):
                        _ranker_multiple_val_params[child.tag].append({'value': child.findall('value')[i].text, 'attr': child.attrib})

            ranker_multiple_val_params = {}
            if _ranker_multiple_val_params:
                keys, values = zip(*_ranker_multiple_val_params.items())
                ranker_multiple_val_params = [dict(zip(keys, v)) for v in itertools.product(*values)]
            rankers.append({'single_val_params': ranker_single_val_params, 'multiple_val_params': ranker_multiple_val_params})
        return rankers

    def get_simulator(self):
        return self._xml_input.findall('simulator/name')[0].text
    def get_online_simulator_settings(self):
        self.rounds = 1000
        if self._xml_input.findall('simulator/rounds'):
            self.rounds = int(self._xml_input.findall('simulator/rounds')[0].text)

        self.n_users_per_round = 100
        if self._xml_input.findall('simulator/n-users-per-round'):
            self.n_users_per_round = int(self._xml_input.findall('simulator/n-users-per-round')[0].text)

        self.delayed_update = False
        if self._xml_input.findall('simulator/delayed-update'):
            self.delayed_update = self._xml_input.findall('simulator/delayed-update')[0].text

        self.feedback_model = False
        if self._xml_input.findall('simulator/feedback-model'):
            self.feedback_model = self._xml_input.findall('simulator/feedback-model')[0].text

        self.optimal_ranker = 'naive_relevance'
        self.full_feature = False
        if self._xml_input.findall('simulator/optimal-ranker'):
            self.optimal_ranker = self._xml_input.findall('simulator/optimal-ranker')[0].text
            if 'full-feature' in self._xml_input.findall('simulator/optimal-ranker')[0].attrib:
                self.full_feature = self._xml_input.findall('simulator/optimal-ranker')[0].attrib['full-feature']
            if 'lmbda' in self._xml_input.findall('simulator/optimal-ranker')[0].attrib:
                self.lmbda = float(self._xml_input.findall('simulator/optimal-ranker')[0].attrib['lmbda'])

        self.optimal_reward_function = 'naive_relevance'
        if self._xml_input.findall('simulator/optimal-reward-function'):
            self.optimal_reward_function = self._xml_input.findall('simulator/optimal-reward-function')[0].text

        self.list_size = 10
        if self._xml_input.findall('simulator/list-size'):
            self.list_size = int(self._xml_input.findall('simulator/list-size')[0].text)
    def get_optimal_ranker(self):
        self.optimal_ranker = 'naive_relevance'
        self.full_feature = False
        if self._xml_input.findall('simulator/optimal-ranker'):
            self.optimal_ranker = self._xml_input.findall('simulator/optimal-ranker')[0].text
            if self._xml_input.findall('simulator/optimal-ranker')[0].attrib['full-feature'] is not None:
                self.full_feature = self._xml_input.findall('simulator/optimal-ranker')[0].attrib['full-feature']

    def get_latent_feature_dim(self):
        latent_feature_dim = 10
        if self._xml_input.findall('features/latent_feature_dim'):
            latent_feature_dim = int(self._xml_input.findall('features/latent_feature_dim')[0].text)
        return latent_feature_dim
    def normalize_latent_feature(self):
        normalize_latent_feature = False
        if self._xml_input.findall('features/latent_feature_normalize'):
            normalize_latent_feature = self._xml_input.findall('features/latent_feature_normalize')[0].text == 'True'
        return normalize_latent_feature
    def save_item_features(self):
        save_features = False
        if self._xml_input.findall('features/save-item-feature'):
            save_features = self._xml_input.findall('features/save-item-feature')[0].text == 'True'
        return save_features
    def get_features_derivation_type(self):
        features_derivation_type = []
        if self._xml_input.findall('features/derivation-type'):
            if len(self._xml_input.findall('features/derivation-type')) > 1:
                for child in self._xml_input.findall('features/derivation-type'):
                    features_derivation_type.append(child.findall('value').text.strip())
            else:
                features_derivation_type.append(self._xml_input.findall('features/derivation-type')[0].text.strip())
        return features_derivation_type

    def get_metrics(self):
        self.metrics = []
        for child in self._xml_input.findall('metric/value'):
            _dict = {'name': child.text}
            for key, value in child.attrib.items():
                _dict[key] = value
            self.metrics.append(_dict)

    # def get_xml(self):
    #     return self._xml_input
    #
    # def get_librec_auto_log_name(self):
    #     return self._log_filename
    #
    # # def get_var_data(self):
    # #     return self._var_data
    #
    # def get_key_password(self):
    #     return self._key_password
    #
    # def set_key_password(self, pw):
    #     self._key_password = pw
    #
    # def get_value_conf(self, subexp_no):
    #     return self._var_coll.var_confs[subexp_no]
    #
    # def has_alg_script(self):
    #     alg_script_elem = single_xpath(self._xml_input, '/librec-auto/alg/script')
    #     return (alg_script_elem is not None)
    #
    # def get_bbo_steps(self):
    #     if self._bbo_steps > 0:
    #         return self._bbo_steps
    #     else:
    #         return None
    #
    # def get_sub_exp_count(self):
    #     exp_count = len(self._var_coll.var_confs)
    #
    #     if self.get_bbo_steps() is not None:
    #         self._count = self.get_bbo_steps()
    #
    #     if self._count is not None:
    #         return self._count
    #     elif exp_count == 0:
    #         return 1
    #     else:
    #         return exp_count
    #
    # def get_files(self):
    #     return self._files

    def read_xml(self, path_str):
        path = self._files.get_config_file_path()
        if (path.exists()):
            xml_input = xml_load_from_path(path)
            return xml_input
        else:
            return None

    # def ensure_experiments(self, exp_no=None):
    #     if self.get_bbo_steps() is None:
    #         exp_count = len(self._var_coll.var_confs)
    #         if exp_no is not None:
    #             exp_count = exp_no
    #         if exp_count == 0:
    #             exp_count = 1
    #     else:
    #         exp_count = self.get_bbo_steps()
    #     self.get_files().ensure_exp_paths(exp_count)
    #
    # def load_libraries(self):
    #     lib_paths = []
    #     lib_elems = self._xml_input.xpath('/librec-auto/library')
    #     for elem in lib_elems:
    #         self._libraries.add_lib(
    #             Library(elem.text, elem.get('src'), self._files))

    # # Process config takes the config file and produces a dictionary of the following form:
    # # xpath-string => list of values
    # # or xpath-string => (range-to, range-from) pair
    # # Right now, we will assume the first
    # def process_config(self):
    #     self.setup_bbo()
    #     self._var_data = defaultdict(list)
    #     self.substitute_library()
    #     self.collect_vars()
    #     self.ensure_experiments()

    # def setup_bbo(self):
    #     opt_elem = single_xpath(self._xml_input, '/librec-auto/optimize')
    #     if opt_elem is None:
    #         self._bbo_steps = 0
    #     else:
    #         self._bbo_steps = int(single_xpath(opt_elem, 'iterations').text)

    # # Have to wait to writes experiment-specific XML configurations to each exp directory
    # # in case a purge is happening.
    # def setup_exp_configs(self, startflag=None):
    #     self.write_exp_configs(startflag)
    #
    # def substitute_library(self):
    #     ref_elems = self._xml_input.xpath('//*[@ref]')
    #     pro_feat_names = self.protected_features.get_protected_feature_names()
    #     for ref_elem in ref_elems:
    #         ref_name = ref_elem.get('ref')
    #         named_elem = self._libraries.get_elem(ref_name)
    #         if named_elem is not None:
    #             merged_elem = merge_elements(named_elem, ref_elem)
    #             ref_elem.getparent().replace(ref_elem, merged_elem)
    #         else:
    #             if ref_name in pro_feat_names:
    #                 continue
    #             else:
    #                 logging.warning(f"No such element in library {ref_name}")
    #
    # def collect_vars(self):
    #     self.collect_librec_vars()
    #     self.collect_rerank_vars()
    #     self._var_coll.compute_var_configurations()
    #
    # def collect_librec_vars(self):
    #     Tag = 'value'
    #
    #     value_elems = self._xml_input.xpath(
    #         '/librec-auto/*[not(self::rerank)]/*/value')
    #
    #     value_optimize_elems = self._xml_input.xpath(
    #         '/librec-auto/alg/*//lower')
    #
    #     check_multiple_values = [elem.getparent() for elem in value_elems]
    #     check_multiple_values = list(set(check_multiple_values))
    #
    #     has_optimize = len(self._xml_input.xpath('/librec-auto/optimize')) > 0
    #
    #     if len(check_multiple_values) != len(value_elems) and len(value_optimize_elems) > 0:
    #         raise InvalidConfiguration("optimization", "You may only use upper/lower for optimizing ranges")
    #     elif len(value_optimize_elems) > 0 and not has_optimize:
    #         raise InvalidConfiguration("optimization", "You may only use upper/lower for optimizing ranges")
    #     elif len(value_elems) > 0 and has_optimize:
    #         raise InvalidConfiguration("optimization", "Use of upper/lower value bounds requires optimize tag")
    #     elif len(value_optimize_elems) > 0:
    #         value_elems = value_optimize_elems + self._xml_input.xpath(
    #             '/librec-auto/alg/*//upper')
    #         parents = [elem.getparent() for elem in value_elems]
    #
    #         Tag = 'lower'
    #
    #     parents = [elem.getparent() for elem in value_elems]
    #     parents = list(set(parents))
    #     if Tag == 'value':
    #         for parent in parents:
    #             vals = [elem.text for elem in parent.iterchildren(tag=Tag)]
    #             parent_path = build_parent_path(parent)
    #             self._var_coll.add_var('librec', parent_path, vals)
    #
    #     else:
    #         for parent in parents:
    #             val_lower = [elem.text for elem in parent.iterchildren(tag='lower')]
    #             val_upper = [elem.text for elem in parent.iterchildren(tag='upper')]
    #             vals = []
    #             # print(val_lower,val_upper)
    #             for i in range(len(val_lower)):
    #                 vals.append(val_lower[i])
    #                 vals.append(val_upper[i])
    #
    #             parent_path = build_parent_path(parent)
    #             self._var_coll.add_var('librec', parent_path, vals)
    #
    # def collect_rerank_vars(self):
    #     value_elems = self._xml_input.xpath('/librec-auto/rerank/*//value')
    #     parents = [elem.getparent() for elem in value_elems]
    #     parents = list(set(parents))
    #     for parent in parents:
    #         vals = [elem.text for elem in parent.iterchildren(tag='value')]
    #         parent_path = build_parent_path(parent)
    #         self._var_coll.add_var('rerank', parent_path, vals)
    #
    # # Write versions of the config file in which the parameters with multiple values are replaced with
    # # a single value
    # def write_exp_configs(self, startflag=None, val=None, iteration=None):
    #
    #     configs = list(
    #         zip(self.get_files().get_exp_paths_iterator(),
    #             iter(self._var_coll.var_confs)))
    #     if self.get_bbo_steps() is not None and startflag is None:
    #         exp, vconf = configs[0]
    #
    #         for x in range(len(val)):
    #             vconf.vars[x].val = val[x]
    #         vconf.exp_no = None
    #         vconf.exp_dir = exp.exp_name
    #
    #         current_exp_path = self._files.get_study_path() / self._files.get_exp_name(iteration)
    #
    #         exp.set_path('conf', current_exp_path / 'conf')
    #         exp.exp_name = self._files.get_exp_name(iteration)
    #         self.write_exp_config(exp, vconf, current_exp_path)
    #
    #
    #     elif startflag is not None:
    #         i = 0
    #         for exp, vconf in configs[:1]:
    #             vconf.exp_no = i
    #             vconf.exp_dir = exp.exp_name
    #             self.write_exp_config(exp, vconf)
    #     else:
    #         i = 0
    #         for exp, vconf in configs:
    #             vconf.exp_no = i
    #             vconf.exp_dir = exp.exp_name
    #             self.write_exp_config(exp, vconf)
    #
    # def write_exp_config(self, exp, vconf, iteration=None):
    #     new_xml = copy.deepcopy(self._xml_input)
    #     # Remove libraries. All substitutions have already happened.
    #     for lib in new_xml.xpath('/librec-auto/library'):
    #         lib.getparent().remove(lib)
    #
    #     pat = re.compile(ConfigCmd._PARAM_NAME_PATH_RE)
    #     for vinfo in vconf.vars:
    #         var_elem = new_xml.xpath(vinfo.path)[0]
    #         attr_save = copy.copy(var_elem.attrib)
    #         var_elem.clear()
    #         var_elem.text = str(vinfo.val)
    #         var_elem.set("var", "true")
    #         if var_elem.tag == 'param':  # params are distinguished by name attributes
    #             mat = pat.match(vinfo.path)
    #             var_elem.attrib['name'] = mat.group(1)
    #         for key in attr_save.keys():
    #             var_elem.attrib[key] = attr_save[key]
    #     new_xml = self.protected_features.replace_referenced_protected_features(new_xml)
    #     new_xml.append(
    #         etree.Comment(
    #             'This configuration file was automatically generated by librec-auto. '
    #             +
    #             'Editing may produce unpredictable results and is not recommended.'
    #         ))
    #     outpath = exp.get_path('conf') / Files.DEFAULT_CONFIG_FILENAME
    #     logging.info('Writing config file ' + str(outpath))
    #     new_xml.getroottree().write(outpath.absolute().as_posix(),
    #                                 pretty_print=True)
    #
    #     props = LibrecProperties(new_xml, self._files)
    #     exp.add_to_config(props.properties, 'librec_result')
    #
    #     if iteration is not None:
    #         props.properties['dfs.result.dir'] = exp.exp_name + '/result'
    #
    #     props.save(exp)
    #
    #     if vconf.ref_config:
    #         path = exp.get_ref_exp_flag_path()
    #         with path.open(mode='w') as fh:
    #             fh.write(vconf.ref_config.exp_dir)
    #             fh.write('\n')
    #
    # def has_rerank(self):
    #     rerank_elems = self._xml_input.xpath('/librec-auto/rerank')
    #     return len(rerank_elems) > 0
    #
    # def has_post(self):
    #     post_elems = self._xml_input.xpath('/librec-auto/post')
    #     return len(post_elems) > 0
    #
    # def cross_validation(self):
    #     model_elem = single_xpath(self._xml_input,
    #                               '/librec-auto/splitter/model')
    #     if model_elem.text == 'kcv':
    #         return int(model_elem.get('count'))
    #     else:
    #         return 1

    def is_valid(self):
        return self._xml_input is not None

    # def thread_count(self):
    #     thread_elems = self._xml_input.xpath('/librec-auto/thread-count')
    #     if len(thread_elems) == 0:
    #         return 1
    #     else:
    #         return int(thread_elems[0].text)

    # def get_python_metrics(self):
    #     """
    #     Gets the XML elements for python-side metrics
    #     """
    #     return self._xml_input.findall('metric/script[@lang="python3"]')
    #
    # def get_cv_directories(self, absolute=False) -> List[Path]:
    #     """
    #     Gets the list of cv directories as Path objects.
    #     """
    #     data_path = self._files.get_data_path()
    #
    #     # Should really dispatch through the Files object
    #     split_dir = data_path / Path('split')  # cv splits live here
    #
    #     dir_strings = os.listdir(split_dir)  # ['cv_1', 'cv_2', ...]
    #
    #     dir_pat = re.compile(self._CV_DIR_RE)
    #
    #     cv_dir_strings = list(filter(dir_pat.match, dir_strings))
    #
    #     dirs = [split_dir / cv_dir_string for cv_dir_string in cv_dir_strings]
    #
    #     if absolute:
    #         return [dir.absolute() for dir in dirs]
    #     else:
    #         return dirs

def read_config_file(config_file, target, log_filename=None):
    config = ConfigCmd(config_file, target, log_filename)
    # print(target)
    # if config.is_valid():
    #     print()
        # config.load_libraries()
        # config.process_config()
    # else:
    #     raise InvalidConfiguration("Configuration file load error", "There was an error loading the configuration file.")
    return config