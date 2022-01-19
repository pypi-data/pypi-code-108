import typer
import yaml

from continual import continual as c
from continual.python.cli import utils
from itertools import groupby

YAML_TEMPLATE = """type: {{TYPE}}
name: {{NAME}}{{ENTITY}}{{TARGET}}{{INDEX}}{{TIME_INDEX}}{{SPLIT}}{{COLUMNS}}{{EXCLUDED_COLUMNS}}{{TRAINING_CONFIG}}{{PREDICTION_CONFIG}}{{PROMOTION_CONFIG}}{{TABLE_OR_QUERY}}
"""

SQL_STUB_TEMPLATE = """{{
  config(
    materialized = 'view',
    meta = {'continual.enabled' : False},
    )
}}
SELECT * from {{PRED_DB}}
"""

EXPOSURE_TEMPLATE = """
  - name: {{NAME}}
    type: ml
    url: {{URL}}
    description: >
      Created automatically via Continual dbt integration. View more details about this model and its predictions at {{URL}}
    tags: ['continual'] 

    depends_on:{{TABLE_LIST}}
    owner:
      email: {{EMAIL}}
"""

SOURCES_TEMPLATE = """version: 2 

sources: 
    - name: {{SCHEMA}}
      database: {{DATABASE}}
      description: Created by Continual dbt Integration. 
      tags: ['continual']
      tables: {{TABLES}}   
"""

# builds yaml from template
def build_yaml(
    table_name,
    type,
    name,
    entity,
    index,
    time_index,
    target,
    column_config,
    split,
    training_config,
    prediction_config,
    promotion_config,
    excluded_columns,
):
    index_text = ""
    if index is not None:
        index_text = "\nindex: %s" % index

    time_index_text = ""
    if time_index is not None:
        time_index_text = "\ntime_index: %s" % time_index

    entity_text = ""
    if entity is not None:
        entity_text = "\nentity: %s" % entity

    target_text = ""
    if target is not None:
        target_text = "\ntarget: %s" % target

    split_text = ""
    if split is not None:
        split_text = "\nsplit: %s" % split

    training_text = ""
    if training_config is not None:
        training_text = "\ntrain:"
        for t in training_config:
            training_text = (
                training_text
                + """
    %s: %s
    """
                % (t, training_config[t])
            )

    prediction_text = ""
    if prediction_config is not None:
        prediction_text = "\npredict:"
        for p in prediction_config:
            prediction_text = (
                prediction_text
                + """
    %s: %s
    """
                % (p, prediction_config[p])
            )

    promotion_text = ""
    if promotion_config is not None:
        promotion_text = "\npromote:"
        for p in promotion_config:
            promotion_text = (
                promotion_text
                + """
    %s: %s
    """
                % (p, promotion_config[p])
            )

    column_text = ""
    if column_config is not None:
        column_text = "\ncolumns:"
        for col in column_config:
            column_text = (
                column_text
                + """
    - """
            )
            for field in col:
                column_text = (
                    column_text
                    + """%s: %s
      """
                    % (field, col[field])
                )

    excluded_text = ""
    if excluded_columns is not None:
        excluded_text = "\nexclude_columns:"
        for col in excluded_columns:
            excluded_text = (
                excluded_text
                + """
    - %s"""
                % (col)
            )

    source = "table"
    # if type == "Model":
    #    source = "query"
    #    table_name = "select * from %s" % table_name

    # need to properly modify spacing in sql:
    yaml = (
        YAML_TEMPLATE.replace("{{TYPE}}", type)
        .replace("{{NAME}}", name)
        .replace("{{ENTITY}}", entity_text)
        .replace("{{TARGET}}", target_text)
        .replace("{{INDEX}}", index_text)
        .replace("{{TIME_INDEX}}", time_index_text)
        .replace("{{SPLIT}}", split_text)
        .replace("{{TRAINING_CONFIG}}", training_text)
        .replace("{{PREDICTION_CONFIG}}", prediction_text)
        .replace("{{PROMOTION_CONFIG}}", promotion_text)
        .replace("{{COLUMNS}}", column_text)
        .replace("{{EXCLUDED_COLUMNS}}", excluded_text)
        .replace("{{TABLE_OR_QUERY}}", "\n%s: %s" % (source, table_name))
    )
    return yaml


def generate_exposure_yaml(model, table_list, project_slug):
    url = "%s/%s/models/%s" % (utils.get_endpoint(), project_slug, model)

    table_list_text = ""
    for t in table_list:
        table_list_text = (
            table_list_text
            + """
      - ref(\'%s\')"""
            % t
        )

    email = c.config.email

    yaml = (
        EXPOSURE_TEMPLATE.replace("{{NAME}}", model)
        .replace("{{URL}}", url)
        .replace("{{TABLE_LIST}}", table_list_text)
        .replace("{{EMAIL}}", email)
    )
    return yaml


def generate_source_yaml(tables, schema, database):
    table_list_text = ""
    for t in tables:
        table_list_text = (
            table_list_text
            + """
        - name: %s"""
            % t
        )
    yaml = (
        SOURCES_TEMPLATE.replace("{{DATABASE}}", database)
        .replace("{{SCHEMA}}", schema)
        .replace("{{TABLES}}", table_list_text)
    )
    return yaml


def generate_exposures(entity_dict, model_dict, project):
    exposures = []
    for model, entity_list in model_dict.items():
        table_list = []
        if model[-8:] != "__path__":
            for entity in entity_list:
                table_list.extend(entity_dict.get(entity))
            exposure_text = generate_exposure_yaml(model, table_list, project)
            exposures.append((exposure_text, model_dict["%s__path__" % model]))
    return exposures


def generate_sources(sources):
    # we know all model tables in an env have to have the same db and schema
    database = None
    schema = None
    tables = None

    if sources:
        pieces = sources[0].split(".")
        schema = pieces[-2]
        if len(pieces) > 2:  # bigquery doesn't have a db
            database = pieces[0]
        tables = [t.split(".")[-1] for t in sources]

    source_text = generate_source_yaml(tables, schema, database)
    return source_text


# takes continual config and return yaml text. Only used if continual.enabled is not False
def generate_yaml(continual_configs, name, table_name):
    type = get_continual_config(continual_configs, "type")
    name = get_continual_config(
        continual_configs, "name", name
    )  # allow config overwrite of name
    entity = get_continual_config(continual_configs, "entity")
    index = get_continual_config(continual_configs, "index")
    time_index = get_continual_config(continual_configs, "time_index")
    split = get_continual_config(continual_configs, "split")
    target = get_continual_config(continual_configs, "target")
    columns = get_continual_config(continual_configs, "columns")
    excluded_columns = get_continual_config(continual_configs, "exclude_columns")
    training_config = get_continual_config(continual_configs, "training")
    prediction_config = get_continual_config(continual_configs, "prediction")
    promotion_config = get_continual_config(continual_configs, "promotion")
    yaml_text = None
    try:
        if (type is None) or (name is None) or (index is None):
            raise Exception(
                "Insufficient inputs. Required configurations missing: continual_name: %s, continual_type: %s, continual_index: %s"
                % (name, type, index)
            )
        if type.lower() == "model":
            if target is None:
                raise Exception(
                    "Insufficient inputs. Model requires a target but none is provided."
                )
            else:
                yaml_text = build_yaml(
                    table_name,
                    "Model",
                    name,
                    entity,
                    index,
                    time_index,
                    target,
                    columns,
                    split,
                    training_config,
                    prediction_config,
                    promotion_config,
                    excluded_columns,
                )
        elif type.lower() == "featureset":
            yaml_text = build_yaml(
                table_name,
                "FeatureSet",
                name,
                entity,
                index,
                time_index,
                target,
                columns,
                split,
                training_config,
                prediction_config,
                promotion_config,
                excluded_columns,
            )
        else:
            typer.secho(
                "continual_type (%s) unrecognized. Must be Either 'Model' or 'FeatureSet'."
                % type,
                fg="red",
            )
            raise Exception("Unsupported Continual Type.")

    except Exception as e:
        typer.secho(
            "\t Failed to build yaml for dbt model %s: %s" % (name, str(e)), fg="red"
        )

    return yaml_text


# generates model stub
def generate_model_stub(pred_db, create_sources):
    if create_sources:
        pieces = pred_db.split(".")
        table = pieces[-1]
        schema = pieces[-2]
        source_fragment = """{{ source('%s', '%s') }}""" % (schema, table)
        stub_sql = SQL_STUB_TEMPLATE.replace("{{PRED_DB}}", source_fragment)
    else:  # not using sources, so just do a normal query
        stub_sql = SQL_STUB_TEMPLATE.replace("{{PRED_DB}}", pred_db)
    return stub_sql


# stubs are a list of (path, text) tuples
def save_stubs(stubs, print_it=True):
    for (path, text) in stubs:
        with open(path, "w+") as f:
            if print_it:
                typer.secho("Saving stub file %s" % path)
            f.write(text)


# exposures is a list of yaml text. exposures can all live in the same yaml file so we'll add them
def save_exposures(exposures, print_it=True):

    grouped_dict = {}
    for key, val in groupby(
        sorted(exposures, key=lambda ele: ele[1]), key=lambda ele: ele[1]
    ):
        grouped_dict[key] = [ele[0] for ele in val]

    exposure_text = """version: 2
exposures:"""
    for path, text_list in grouped_dict.items():
        for text in text_list:
            exposure_text = "%s\n%s" % (exposure_text, text)
        e_path = "%s/continual_exposures.yml" % path
        with open(e_path, "w+") as f:
            if print_it:
                typer.secho("Saving exposure file %s" % e_path)
            f.write(exposure_text)


def save_sources(sources_text, path, print_it=True):
    s_path = "%s/continual_sources.yml" % path
    with open(s_path, "w+") as f:
        if print_it:
            typer.secho("Saving sources file %s!" % s_path)
        f.write(sources_text)


# processes nodes & generate yaml files
def process_node(
    node, dbt_project_dir, pred_db_prefix, entity_dict, model_dict, sources_list
):
    # if we got to this point, we know we have at least continual.type, so continual_config has to be non-null
    keys = node.get("meta").copy()
    keys.update(
        node.get("config").get("meta")
    )  # model-level config should override project-level config
    continual_config = {k: v for k, v in keys.items() if k.startswith("continual")}
    table_name = node.get("relation_name")
    name = get_continual_config(continual_config, "name", node.get("name"))

    ### do all the yaml processing from dbt-continual plugin
    ### only process node if continual is not disabled
    continual_enabled = get_continual_config(
        continual_config, "enabled", True
    )  # defaults to true
    if continual_enabled:
        # deal with yamls
        try:
            yaml_text = generate_yaml(continual_config, name, table_name)

            # deal with stubs
            stub_path = None
            stub_text = None
            if get_continual_config(continual_config, "type").lower() == "model":
                create_sources = get_continual_config(
                    continual_config, "create_sources"
                )

                pred_db = "%s.model_%s_predictions" % (pred_db_prefix, name)

                if create_sources:
                    sources_list.append(pred_db)

                if get_continual_config(continual_config, "create_stub"):
                    stub_text = generate_model_stub(pred_db, create_sources)
                    stub_path = "%s/%s" % (
                        dbt_project_dir,
                        node.get("original_file_path"),
                    )
                    stub_path = stub_path.replace(".sql", "_predictions.sql")

            # deal with entity + model dicts
            if get_continual_config(continual_config, "create_exposures") == True:
                entity = get_continual_config(continual_config, "entity", name)
                table_list = entity_dict.get(entity, [])
                table_list.append(node.get("name"))
                entity_dict[entity] = table_list
                if get_continual_config(continual_config, "type").lower() == "model":
                    entity_list = [entity]
                    for col in get_continual_config(continual_config, "columns", []):
                        linked_entity = col.get("entity")
                        if linked_entity is not None:
                            entity_list.append(linked_entity)
                    model_dict[name] = entity_list
                    model_dict["%s__path__" % name] = "%s/%s" % (
                        dbt_project_dir,
                        node.get("original_file_path").split("/")[0],
                    )

            return (
                (name, yaml_text),
                (stub_path, stub_text),
                entity_dict,
                model_dict,
                sources_list,
            )

        except Exception as e:
            typer.secho(
                "Failed to generate yaml for model %s: %s" % (name, str(e)), fg="red"
            )
            return None

    else:
        return None


def get_continual_config(config, key, default=None):
    value = None
    if config.get("continual", None):
        value = config.get("continual").get(key, None)
    if value is None:
        value = config.get("continual.%s" % key, None)
    if value is None:
        value = default
    return value


# proceses manifest file, builds yaml files and saves them to target dir
def process_manifest(
    manifest_text, dbt_project_dir, yaml_dir, pred_db_prefix, project, verbose=False
):
    nodes = manifest_text.get("nodes")
    paths = []
    stubs = []
    exposures = []
    sources = []
    entity_dict = {}
    model_dict = {}
    sources_list = []
    if nodes:
        # we only care about model nodes
        model_nodes = {
            k: v for (k, v) in nodes.items() if v.get("resource_type") == "model"
        }
        if model_nodes:
            # must have a continual.type (featureset or model) set or we can't do anything with it
            continual_nodes = {
                k: v
                for (k, v) in model_nodes.items()
                if get_continual_config(v.get("config").get("meta", {}), "type")
                is not None
            }  # this is now safe. dbt version < 0.21 doesn't incldue meta by default, so need to return {} in these instances
            yamls = []
            for k, v in continual_nodes.items():
                # create continual yaml
                (
                    continual_yaml,
                    stub,
                    entity_dict,
                    model_dict,
                    sources_list,
                ) = process_node(
                    v,
                    dbt_project_dir,
                    pred_db_prefix,
                    entity_dict,
                    model_dict,
                    sources_list,
                )
                if continual_yaml:
                    yamls.append(continual_yaml)
                if stub[0] and stub[1]:
                    stubs.append(stub)
            if len(yamls) > 0:
                # save yamls to dbt target dir
                target_dir = "%s/%s" % (dbt_project_dir, yaml_dir)
                paths = utils.save_yamls(yamls, target_dir, verbose)
            if len(model_dict) > 0:
                exposures = generate_exposures(entity_dict, model_dict, project)
            if len(sources_list) > 0:
                sources = generate_sources(sources_list)
    return (paths, stubs, exposures, sources)


def get_datastore(profiles_file, dbt_profile, dbt_target):
    # get profile connetion info
    datastore = None
    try:
        with open(profiles_file, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            target_config = text.get(dbt_profile).get("outputs").get(dbt_target)
            type = target_config.get("type")

            # consider not updating user/pass
            if type.lower() == "snowflake":
                config = {
                    # "host" : target_config.get("account"),
                    # "username" : target_config.get("user"),
                    # "password" : target_config.get("password"),
                    "database": target_config.get("database"),
                    "db_schema": target_config.get("schema"),
                    # "warehouse" : target_config.get("warehouse"),
                    # "role" : target_config.get("role",None),
                }
                datastore = {"type": type, "snowflake": config}
            elif type.lower() == "redshift":
                config = {
                    # "host" : target_config.get("host"),
                    # "username" : target_config.get("user"),
                    # "password" : target_config.get("password"),
                    "database": target_config.get("dbname"),
                    "db_schema": target_config.get("schema"),
                    # "port" : target_config.get("port"),
                }
                datastore = {"type": type, "redshift": config}
            elif type.lower() == "bigquery":
                config = {
                    # "auth_file_name" : target_config.get("project"),
                    "dataset": target_config.get("dataset")
                    or target_config.get("schema"),
                    # "auth_file" : target_config.get("keyfile_json"),
                }
                datastore = {"type": type, "big_query": config}
            else:  # not supported
                typer.secho(
                    "DataStore type %s is not supported by continual at this time."
                    % type,
                    fg="red",
                )
    except:
        pass
    return datastore


def get_default_target(profiles_file, dbt_profile):
    dbt_target = None
    try:
        with open(profiles_file, "r") as file:
            text = yaml.load(file, Loader=yaml.FullLoader)
            dbt_target = text.get(dbt_profile).get("target")
    except:
        typer.secho(
            "No default target found for profile '%s' in profiles file %s. Ensure your profile name is valid and either add a default target for your profile or pass in a target via --target"
            % (dbt_profile, profiles_file),
            fg="red",
        )
        exit(1)

    return dbt_target


# get or create environment
def get_or_create_env(client, profiles_file, dbt_target, dbt_profile):
    # get or create env
    env = None
    if dbt_target is not None:
        try:
            env = client.environments.get(dbt_target)
        # doesn't exist, so we'll create it
        except:
            try:
                data_store = get_datastore(profiles_file, dbt_profile, dbt_target)
                env = client.environments.create(
                    dbt_target, data_store=data_store, source=client.config.project
                )
            except Exception as e:
                typer.secho(
                    "Failed to create environment for dbt target %s: %s"
                    % (dbt_target, str(e)),
                    fg="red",
                )
                exit(1)

    return env.name  # should never be None


def get_environment_datastore_type(env):
    type = env.data_store.type
    if type is None or len(type) == 0:
        type = c.projects.get(env.id.split("@")[0]).data_store.type
    return type


def get_pred_db_prefix(e):
    type = get_environment_datastore_type(e)
    if type.lower() == "snowflake":
        return "%s.%s" % (
            e.data_store.snowflake.database,
            e.data_store.snowflake.db_schema,
        )
    elif type.lower() == "redshift":
        return "%s.%s" % (
            e.data_store.redshift.database,
            e.data_store.redshift.db_schema,
        )
    elif type.lower() == "bigquery":
        return "%s" % (e.data_store.big_query.dataset)
    else:  # not supported
        typer.secho(
            "Datastore type %s is not supported by continual at this time." % type,
            fg="red",
        )
        return None
