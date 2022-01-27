import configparser
import os
from pymongo import MongoClient

ANNOTATOR_COLLECTION = 'Annotators'
SCHEME_COLLECTION = 'Schemes'
STREAM_COLLECTION = 'Streams'
ROLE_COLLECTION = 'Roles'
ANNOTATION_COLLECTION = 'Annotations'
SESSION_COLLECTION = 'Sessions'
ANNOTATION_DATA_COLLECTION = 'AnnotationData'

class NovaDBHandler():

  def __init__(self, db_config_path=None, db_config_dict=None):

    # Connecting to the database
    if db_config_path:
      if os.path.isfile(db_config_path):
        cfg = self.read_config(db_config_path)
        self.ip = str(cfg['DB']['ip'])
        self.port = int(cfg['DB']['port'])
        self.user = str(cfg['DB']['user'])
        self.password = str(cfg['DB']['password'])
      else:
        raise FileNotFoundError('No database config file found at {}'.format(db_config_path))

    # If a db config_dict is specified overwrite the config from path
    if db_config_dict:
      if db_config_path:
        print('WARNING! database config are specifed as file AND and as dictionary. Using the dictionary.')
      self.ip = db_config_dict['ip']
      self.port = db_config_dict['port']
      self.user = db_config_dict['user']
      self.password = db_config_dict['password']

    if not (self.ip or self.port or self.user or self.password):
      print('WARNING! No valid nova database config found for path {} and dict {} \n Found config parameters are ip:{}, port{}, user: {}. Also check your password.'.format(db_config_path, db_config_dict, self.ip, self.port, self.user))

    self.client = MongoClient(host=self.ip, port=self.port, username=self.user, password=self.password)
    self.datasets = self.client.list_database_names()

  def print_config(self, cfg, cfg_path):
    print('Loaded config from {}:'.format(cfg_path))
    print('---------------------')
    for sec_name, sec_dict in cfg._sections.items():
      print(sec_name)
      for k, v in sec_dict.items():
        if k == 'password':
          continue
        else:
          print('\t{} : {}'.format(k, v))
    print('---------------------')

  def read_config(self, cfg_path):
    config = configparser.RawConfigParser()
    config.read(cfg_path)
    self.print_config(config, cfg_path)
    return config

  def get_docs_by_prop(self, vals, property, database, collection):
    """

    Args:
      vals:
      property:
      database:
      collection:
      client:

    Returns:

    """
    filter = []

    if not type(vals) == type(list()):
      vals = [vals]

    for n in vals:
      filter.append({property: n})

    filter = {"$or": filter}
    ret = list(self.client[database][collection].find(filter))
    return ret

  def get_schemes(self, dataset, schemes):
    """
    Fetches the scheme object that matches the specified criteria from the nova database and returns them as a python readable dictionary.
    Args:
      ip:
      port:
      user:
      password:
      dataset:
      scheme:

    Returns:

    """

    if not schemes:
      print('WARNING: No Schemes have been requested. Returning empty list.')
      return []

    if not dataset in self.datasets:
      raise ValueError('{} not found in datasets'.format(dataset))

    mongo_schemes = []
    for scheme in schemes:
      mongo_scheme = self.get_docs_by_prop(scheme, 'name', dataset, SCHEME_COLLECTION)
      if not mongo_scheme:
        print('WARNING: No scheme {} found in database'.format(scheme))
      else:
        mongo_schemes.append(mongo_scheme[0])

    if not mongo_schemes:
      raise ValueError('No entries for schemes {} found in database'.format(schemes))

    return mongo_schemes

  def get_session_info(self, dataset, session):
    """
    Fetches the session object that matches the specified criteria from the nova database and returns them as a python readable dictionary.

    Args:
      dataset:
      session:

    Returns:

    """
    mongo_session = self.get_docs_by_prop(session, 'name', dataset, SESSION_COLLECTION)
    return mongo_session

  def get_data_streams(self, dataset, data_streams):
    """
    Fetches the stream objects that matches the specified criteria from the nova database and returns them as a python readable dictionary.
    Args:
      dataset:
      session:
      role_list:
      data_stream_list:
    """
    if not dataset in self.datasets:
      raise ValueError('{} not found in datasets'.format(dataset))

    if not data_streams:
      print('WARNING: No Datastreams have been requested. Returning empty list.')
      return []

    mongo_streams = []
    for stream in data_streams:
      mongo_stream = self.get_docs_by_prop(stream, 'name', dataset, STREAM_COLLECTION)
      if not mongo_stream:
        print('WARNING: No stream {} found in database'.format(stream))
      else:
        mongo_streams.append(mongo_stream[0])

    if not mongo_streams:
      raise ValueError('no entries for datastream {} found'.format(data_streams))

    return mongo_streams

  def get_annotation_docs(self, mongo_schemes, mongo_sessions, mongo_annotators, mongo_roles, database, collection):
    """
    Fetches all annotationobjects that match the specified criteria from the nova database
    Args:
      mongo_schemes:
      mongo_sessions:
      mongo_annotators:
      mongo_roles:
      database:
      collection:
      client:

    Returns:

    """
    scheme_filter = []
    role_filter = []
    annotator_filter = []
    session_filter = []

    for ms in mongo_schemes:
      scheme_filter.append({'scheme_id': ms['_id']})

    for mse in mongo_sessions:
      session_filter.append({'session_id': mse['_id']})

    for ma in mongo_annotators:
      annotator_filter.append({'annotator_id': ma['_id']})

    for mr in mongo_roles:
      role_filter.append({'role_id': mr['_id']})

    filter = {
      '$and': [
        {'$or': scheme_filter},
        {'$or': session_filter},
        {'$or': role_filter},
        {'$or': annotator_filter},
      ]
    }

    ret = list(self.client[database][collection].find(filter))
    return ret

  def get_annos(self, dataset, scheme, session, annotator, roles):
    """
    Fetches all annotations that matche the specified criteria from the nova database and returns them as a python readable dictionary.
    Args:
      ip:
      port:
      user:
      password:
      dataset:
      scheme:
      session:
      annotator:
      roles:

    Returns:

    """
    if not dataset in self.datasets:
      print('{} not found in datasets'.format(dataset))

    mongo_schemes = self.get_docs_by_prop(scheme, 'name', dataset, SCHEME_COLLECTION)
    if not mongo_schemes:
      print('No entries with scheme {} found'.format(scheme))
      #TODO: replace with exceptions for better handling
      exit()
    mongo_annotators = self.get_docs_by_prop(annotator, 'name', dataset, ANNOTATOR_COLLECTION)
    if not mongo_annotators:
      print('No entries for annotator {} found'.format(annotator))
      exit()
    mongo_roles = self.get_docs_by_prop(roles, 'name', dataset, ROLE_COLLECTION)
    if not mongo_roles:
      print('No entries for role {} found'.format(roles))
      exit()
    mongo_sessions = self.get_docs_by_prop(session, 'name', dataset, SESSION_COLLECTION)
    if not mongo_sessions:
      print('No entries for session {} found'.format(session))
      exit()

    mongo_annos = self.get_annotation_docs(mongo_schemes, mongo_sessions, mongo_annotators, mongo_roles, dataset, ANNOTATION_COLLECTION)

    # getting the annotation data and the session name
    if not mongo_annos:
      print(f'No annotions found for \n\t-annotator: {annotator}\n\t-scheme: {scheme}\n\t-session: {session}\n\t-role: {roles}')
      return -1

    else:
      label = self.get_docs_by_prop(mongo_annos[0]['data_id'], '_id', dataset, ANNOTATION_DATA_COLLECTION)
      label = label[0]['labels']

    return label


if __name__ == '__main__':

  db_handler = NovaDBHandler('db.cfg')

  dataset = 'DFG_A1_A2b'
  session = 'NP001'
  scheme = 'IEng'
  annotator = 'gold'
  roles = ['caretaker', 'infant']

  mongo_scheme = db_handler.get_schemes(dataset=dataset, scheme=scheme)
  mongo_annos = db_handler.get_annos(dataset=dataset, scheme=scheme, session=session, annotator=annotator, roles=roles)
  print('Done')
