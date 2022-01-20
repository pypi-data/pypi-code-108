import json
import pytest
import click
from click.testing import CliRunner
import yaml
from spell.cli.utils.command import command, group
from spell.cli.exceptions import CLICK_CLI_USAGE_ERROR


def run_command(cmd, args, cmd_yaml=None, cmd_path=None, parse_json=True):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open(cmd_path or ".dummy", "w") as f:
            yaml.dump(cmd_yaml or {}, f)
        result = runner.invoke(cmd, args, catch_exceptions=False)
        if parse_json:
            return json.loads(result.output), result.exit_code
        else:
            return result.output, result.exit_code


def test_no_file(full_params_cmd):
    expected = {
        "arg1": "arg1",
        "args": ["opt1", "opt2", "opt3"],
        "flag1": True,
        "multiple": ["m1", "m2", "m3"],
        "nargs": ["n1", "n2"],
        "opt": "1",
        "required": "a",
        "thing": True,
        "verbose": 4,
    }

    cmd = " ".join(
        [
            "--nargs n1 n2",
            "--required=a",
            "-f1",
            "--multiple=m1",
            "-m m2",
            "--thing",
            "--opt 1",
            "-m m3",
            "--verbose",
            "-vvv",
            "arg1 opt1 opt2 opt3",
        ]
    )
    result, _ = run_command(
        full_params_cmd,
        cmd,
        expected,
    )
    assert result == expected


@pytest.mark.parametrize(
    "list_type",
    ["string", "list", "string list"],
    ids=["MultipleArgsAsString", "MultipleArgsAsList", "MultipleArgsAsStringList"],
)
def test_file_only(full_params_cmd, list_type):
    yaml_dict = {
        "arg1": "arg1",
        "flag1": True,
        "opt": "something",
        "r": "a",
        "verbose": 3,
    }
    if list_type == "string":
        yaml_dict.update({"nargs": "n1 n2", "multiple": "m1 m2 m3", "args": "a1 a2 a3"})
    elif list_type == "list":
        yaml_dict.update({"nargs": ["n1", "n2"], "multiple": ["m1", "m2", "m3"], "args": ["a1", "a2", "a3"]})
    else:
        yaml_dict.update({"nargs": ["n1 n2"], "multiple": ["m1 m2", "m3"], "args": ["a1 a2", "a3"]})
    expected = {
        "arg1": "arg1",
        "args": ["a1", "a2", "a3"],
        "flag1": True,
        "thing": False,
        "multiple": ["m1", "m2", "m3"],
        "nargs": ["n1", "n2"],
        "opt": "something",
        "required": "a",
        "verbose": 3,
    }
    result, _ = run_command(
        full_params_cmd,
        "--from-file ./cmd.yaml",
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
    )
    assert result == expected


@pytest.mark.parametrize(
    "default,value,result",
    [(True, True, False), (True, False, True), (False, True, True), (False, False, False)],
    ids=[
        "Default:True,Value:True",
        "Default:True,Value:False",
        "Default:False,Value:True",
        "Default:False,Value:False",
    ],
)
def test_simple_flag_file_parsing(default, value, result):
    @command()
    @click.option("--flag", default=default, is_flag=True)
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    yaml_dict = {"flag": value}
    expected = {"flag": result}
    result, _ = run_command(
        cmd,
        "--from-file ./cmd.yaml",
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
    )
    assert result == expected


@pytest.mark.parametrize(
    "default,flag,value,result",
    [
        (True, "on", True, True),
        (True, "on", False, False),
        (True, "off", True, False),
        (True, "off", False, True),
        (False, "on", True, True),
        (False, "on", False, False),
        (False, "off", True, False),
        (False, "off", False, True),
    ],
    ids=[
        "Default:True,--on,Value:True",
        "Default:True,--on,Value:False",
        "Default:True,--off,Value:True",
        "Default:True,--off,Value:False",
        "Default:False,--on,Value:True",
        "Default:False,--on,Value:False",
        "Default:False,--off,Value:True",
        "Default:False,--off,Value:False",
    ],
)
def test_switch_flag_file_parsing(default, flag, value, result):
    @command()
    @click.option("--on/--off", default=default)
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    yaml_dict = {flag: value}
    expected = {"on": result}
    result, _ = run_command(
        cmd,
        "--from-file ./cmd2.yaml",
        cmd_yaml=yaml_dict,
        cmd_path="./cmd2.yaml",
    )
    assert result == expected


def test_mixed_file_and_args_full_overwrite(full_params_cmd):
    yaml_dict = {
        "flag1": False,
        "multiple": ["m1", "m2", "m3"],
        "nargs": ["n1", "n2"],
        "opt": "something",
        "verbose": 1,
    }
    expected = {
        "arg1": "cmd",
        "args": ["a", "b"],
        "flag1": True,
        "multiple": ["1", "2", "3"],
        "nargs": ["1", "2"],
        "opt": "1",
        "required": "b",
        "thing": False,
        "verbose": 4,
    }
    cmd = " ".join(
        [
            "--nargs 1 2",
            "--required=b",
            "-f1",
            "--multiple=1",
            "-m 2",
            "--no-thing",
            "--opt 1",
            "-m 3",
            "--verbose",
            "-vvv",
            "--from-file ./cmd.yaml",
            "cmd a b",
        ]
    )
    result, _ = run_command(
        full_params_cmd,
        cmd,
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
    )
    assert result == expected


def test_mixed_file_and_args_partial_overwrite(full_params_cmd):
    yaml_dict = {
        "flag1": False,
        "nargs": ["n1", "n2"],
        "opt": "something",
        "multiple": ["m1", "m2", "m3"],
        "verbose": 1,
    }
    cmd = " ".join(
        [
            "--no-thing",
            "--opt 1",
            "-m 3",
            "-r a",
            "--verbose",
            "-vvv",
            "--from-file ./cmd.yaml",
            "arg1 a1 a2",
        ]
    )
    expected = {
        "arg1": "arg1",
        "args": ["a1", "a2"],
        "flag1": False,
        "multiple": ["3"],
        "nargs": ["n1", "n2"],
        "opt": "1",
        "required": "a",
        "thing": False,
        "verbose": 4,
    }
    result, _ = run_command(
        full_params_cmd,
        cmd,
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
    )
    assert result == expected


def test_args_in_file_and_cmd_raises():
    @command()
    @click.argument("cmd")
    @click.argument("args", nargs=-1)
    @click.option("-opt")
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    yaml_dict = {"cmd": "python", "args": ["run_my_file.py", "someopt"]}
    _, exit_code = run_command(
        cmd,
        "--from-file ./cmd.yaml ruby myruby.rb opt1",
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
        parse_json=False,
    )
    assert exit_code == CLICK_CLI_USAGE_ERROR


def test_bad_param_in_file_raises():
    @command()
    @click.option("--opt")
    @click.option("--flag", is_flag=True)
    def cmd(opt, flag):
        click.echo(opt)

    yaml_dict = {"flah": True}
    _, exit_code = run_command(
        cmd,
        "--from-file ./cmd.yaml --opt 3 --flah",
        cmd_yaml=yaml_dict,
        cmd_path="./cmd.yaml",
        parse_json=False,
    )
    assert exit_code == CLICK_CLI_USAGE_ERROR


@pytest.mark.parametrize("arg", ["my-arg", "MY-ARG"], ids=["lowercase", "uppercase"])
def test_hyphenated_arg_reads(arg):
    @command()
    @click.argument("my-arg", type=int, metavar="MY-ARG")
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    cmd_yaml = {arg: 1}
    expected_invoke = {"my_arg": 1}
    result, _ = run_command(cmd, "--from-file cmd.yaml", cmd_yaml=cmd_yaml, cmd_path="cmd.yaml")
    assert result == expected_invoke


@pytest.mark.parametrize("arg", ["my-arg", "MY-ARG"], ids=["lowercase", "uppercase"])
def test_hyphenated_arg_writes(arg):
    @command()
    @click.argument("my-arg", type=int, metavar="MY-ARG")
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    cmd_yaml = {arg: 1}
    expected_invoke = {"my_arg": 1}
    expected_yaml = {"my-arg": 1}
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./cmd.yaml", "w") as f:
            yaml.dump(cmd_yaml, f)
        result = runner.invoke(
            cmd,
            "--from-file ./cmd.yaml --save-command ./out.yaml",
            catch_exceptions=False,
        )
        assert json.loads(result.output) == expected_invoke
        with open("./out.yaml") as f:
            assert yaml.safe_load(f) == expected_yaml


def test_underscore_in_arg():
    @command()
    @click.argument("underscore_delimited_arg")
    def cmd(**kwargs):
        pass

    assert cmd.params[0].human_readable_name == "UNDERSCORE-DELIMITED-ARG"


def test_arg_with_metavar():
    @command()
    @click.argument("arg", metavar="alt")
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    cmd_yaml = {"alt": 12}
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./cmd.yaml", "w") as f:
            yaml.dump(cmd_yaml, f)
        result = runner.invoke(
            cmd,
            "--from-file ./cmd.yaml --save-command ./out.yaml",
            catch_exceptions=False,
        )
        assert json.loads(result.output) == {"arg": "12"}
        with open("./out.yaml") as f:
            assert yaml.safe_load(f) == {"alt": "12"}


def test_group():
    @group()
    @click.option("--foo")
    def cli(foo):
        click.echo(foo)

    @cli.group()
    def cmd():
        pass

    @cmd.command()
    @click.option("-o")
    @click.argument("arg")
    def cmd2(**kwargs):
        click.echo(json.dumps(kwargs))

    yaml_dict = {"o": "a"}
    expected = {"o": "a", "arg": "arg"}
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./cmd.yaml", "w") as f:
            yaml.dump(yaml_dict, f)
        with open("./group.yaml", "w") as f:
            yaml.dump({"foo": "bar"}, f)
        result = runner.invoke(
            cli,
            "--from-file ./group.yaml cmd cmd2 --from-file ./cmd.yaml arg",
            catch_exceptions=False,
        )
        result = result.output.split("\n")
        assert result[0] == "bar"
        assert json.loads(result[1]) == expected


def test_save_command(full_params_cmd):
    yaml_dict = {
        "args": "a1 a2",
        "arg1": "arg1",
        "flag1": True,
        "multiple": "m1 m2 m3",
        "nargs": ["n1", "n2"],
        "opt": "something",
        "r": "a",
        "verbose": 3,
    }
    expected_cmd = {
        "arg1": "arg1",
        "args": ["a1", "a2"],
        "flag1": True,
        "multiple": ["m1", "m2", "m3"],
        "nargs": ["n1", "n2"],
        "opt": "something",
        "required": "a",
        "thing": False,
        "verbose": 3,
    }
    expected_yaml = dict(expected_cmd)
    expected_yaml.pop("thing")
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("./cmd.yaml", "w") as f:
            yaml.dump(yaml_dict, f)
        result = runner.invoke(
            full_params_cmd,
            "--from-file ./cmd.yaml --save-command ./out.yaml",
            catch_exceptions=False,
        )
        assert json.loads(result.output) == expected_cmd
        with open("./out.yaml") as f:
            assert yaml.safe_load(f) == expected_yaml


def test_invoke():
    @click.command()
    @click.option("--bar")
    def other(**kwargs):
        click.echo(json.dumps(kwargs))

    @command()
    @click.option("--foo")
    @click.pass_context
    def cmd(ctx, foo):
        ctx.invoke(other, bar=foo)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cmd, "--foo bar", catch_exceptions=False)
        assert json.loads(result.output) == {"bar": "bar"}
