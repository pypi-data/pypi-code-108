from dbsamizdat import SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger


fruittable_SQL = """
    CREATE TABLE "Fruit" (
        id integer PRIMARY KEY,
        name varchar(100)
    );

    INSERT INTO "Fruit"
    SELECT
        *
    FROM (
        VALUES
            (1, 'banana'),
            (2, 'pear'),
            (3, 'apple'),
            (4, 'rambutan')
    ) AS thefruits;

    CREATE TABLE "Pet" (
        id integer PRIMARY KEY,
        name varchar(100)
    );

    INSERT INTO "Pet"
    SELECT
        *
    FROM (
        VALUES
            (1, 'ocelot'),
            (2, 'khoi carp'),
            (3, 'rolypoly'),
            (4, 'drosophila')
    ) AS thepets;
"""


class DealFruitView(SamizdatView):
    deps_on_unmanaged = {('public', 'Fruit')}
    sql_template = """
        ${preamble}
        SELECT name FROM "public"."Fruit" ORDER BY random() LIMIT 1;
        ${postamble}
    """


class DealFruitFun(SamizdatFunction):
    deps_on = {DealFruitView}
    sql_template = f"""
        ${{preamble}}
        RETURNS text AS
        $BODY$
        SELECT format('Have a piece of %s !', name) FROM {DealFruitView.db_object_identity}
        $BODY$
        LANGUAGE SQL
        IMMUTABLE
    """


class DealFruitFunWithName(SamizdatFunction):
    deps_on = {DealFruitFun}
    function_name = 'DealFruitFun'
    function_arguments_signature = 'name text'
    sql_template = f"""
        ${{preamble}}
        RETURNS text AS
        $BODY$
        SELECT format('Hey %s! %s', name, "{DealFruitFun.name}"())
        $BODY$
        LANGUAGE SQL
        IMMUTABLE
    """


class Treat(SamizdatMaterializedView):
    deps_on_unmanaged = {('public', 'Pet')}
    deps_on = {DealFruitFunWithName}
    refresh_triggers = {('public', 'Pet'), ('public', 'Fruit')}
    sql_template = f"""
        ${{preamble}}
        SELECT "{DealFruitFunWithName.name}"(name) AS treat FROM "public"."Pet"
        ${{postamble}};
    """


class PetUppercase(SamizdatMaterializedView):
    refresh_concurrently = True
    deps_on_unmanaged = {('public', 'Pet')}
    sql_template = """
        ${preamble}
        SELECT id, upper(name) FROM "public"."Pet"
        ${postamble};
        CREATE UNIQUE INDEX ON ${samizdatname} (id);
    """


class Raise(SamizdatFunction):
    sql_template = """
        ${preamble}
        RETURNS trigger AS
        $BODY$
        DECLARE arg_message text;
        BEGIN
            arg_message := TG_ARGV[0];
            RAISE EXCEPTION '%', arg_message;
        END;
        $BODY$
        LANGUAGE plpgsql IMMUTABLE;
    """


class FruitCensor(SamizdatTrigger):
    deps_on = {Raise}
    on_table = "Fruit"
    condition = "BEFORE INSERT OR UPDATE OF name"
    sql_template = """
        ${preamble}
        FOR EACH ROW
        WHEN (NEW.name ilike '%durian%')
        EXECUTE PROCEDURE "Raise"('Too delicious.')
    """
