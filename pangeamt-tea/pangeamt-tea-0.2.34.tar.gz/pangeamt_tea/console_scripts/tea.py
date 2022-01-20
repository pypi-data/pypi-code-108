import os
import pathlib
import asyncclick as click
from asyncclick.core import Context
from pangeamt_tea.project.config import Config
from pangeamt_tea.project.project import (
    Project,
    ProjectAlreadyExistsException,
    ProjectNotFoundException,
)
from pangeamt_tea.project.workflow.workflow import Workflow
from pangeamt_tea.project.workflow.workflow import WorkflowAlreadyExists
from pangeamt_nlp.processor.processor_factory import ProcessorFactory
from pangeamt_nlp.processor.base.normalizer_base import NormalizerBase
from pangeamt_nlp.translation_model.translation_model_factory import (
    TranslationModelFactory,
)
from pangeamt_tea.project.workflow.stage.train_stage import TrainStage
from pangeamt_tea.project.workflow.stage.eval_stage import EvalStage


@click.group(invoke_without_command=True)
@click.pass_context
async def tea(ctx: Context):
    pass


# New Project
@tea.command()
@click.option("--customer", "-c", help="Customer name")
@click.option("--src_lang", "-s", help="Source language")
@click.option("--tgt_lang", "-t", help="Target language")
@click.option("--flavor", "-f", default=None, help="Flavor")
@click.option("--version", "-v", default=1, type=click.INT, help="Version")
@click.option(
    "--dir",
    "-d",
    "parent_dir",
    default=None,
    help="Directory where the project is created",
)
async def new(
    customer: str,
    src_lang: str,
    tgt_lang: str,
    flavor: str,
    version: int,
    parent_dir: str,
):

    parent_dir = parent_dir if parent_dir is not None else os.getcwd()
    parent_dir = pathlib.Path(os.path.abspath(parent_dir))

    try:
        Project.new(
            customer,
            src_lang,
            tgt_lang,
            parent_dir,
            version=version,
            flavor=flavor,
        )
    except (ProjectAlreadyExistsException, ProjectNotFoundException) as e:
        raise Exception("Command failed") from e


@tea.group()
@click.pass_context
async def config(ctx: Context):
    pass


# Add processors
@config.command()
@click.option("--project", "-p", "project_dir")
@click.pass_context
def show(ctx: Context, project_dir: str):
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        Config.show(project_dir)

    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Add tokenizer
@config.command()
@click.option(
    "--src",
    "-s",
    help="Source tokenizer",
    type=click.Choice(
        ["moses", "mecab", "thai", "jieba", "none"],
        case_sensitive=False
    ),
)
@click.option(
    "--tgt",
    "-t",
    help="Target tokenizer",
    type=click.Choice(
        ["moses", "mecab", "thai", "jieba", "none"],
        case_sensitive=False
    ),
)
@click.option("--project", "-p", "project_dir")
@click.pass_context
def tokenizer(ctx: Context, src: str, tgt: str, project_dir: str):
    ctx.ensure_object(dict)

    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        Config.add_tokenizer(src, tgt, project_dir)

    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Add truecaser
@config.command()
@click.option("--src", "-s", help="Source truecaser", is_flag=True)
@click.option("--tgt", "-t", help="Target truecaser", is_flag=True)
@click.option("--pretrained", "-ptr", help="Model pretrained")
@click.option("--project", "-p", "project_dir")
@click.pass_context
def truecaser(
    ctx: Context, src: bool, tgt: bool, pretrained: str, project_dir: str
):
    ctx.ensure_object(dict)
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        if pretrained:
            pretrained = os.path.abspath(pretrained)
        Config.add_truecaser(src, tgt, pretrained, project_dir)

    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


@config.command()
@click.option("--shard_size", help="Shard size to use when batch")
@click.option("--src_seq_length", help="Src seq length to use when batch")
@click.option("--tgt_seq_length", help="Tgt seq length to use when batch")
@click.option("--project", "-p", "project_dir")
@click.pass_context
def prepare(
    ctx: Context,
    shard_size: str,
    src_seq_length: str,
    tgt_seq_length: str,
    project_dir: str
):
    ctx.ensure_object(dict)
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    Config.config_prepare(
        str(shard_size), str(src_seq_length), str(tgt_seq_length), project_dir
    )


# Add processors
@config.command()
@click.option(
    "--set",
    "-s",
    help="List of processors separated by semicolons with arguments separated"
    'by commas.\n i.e. "processor1, arg1, arg2; processor2;"',
)
@click.option("--list", "-l", help="List available processors", is_flag=True)
@click.option("--project", "-p", "project_dir")
@click.pass_context
def processors(ctx: Context, set: str, list: bool, project_dir: str):
    if list:
        print()
        print("### List of available processors:\n")
        all_processors = ProcessorFactory.get_available()
        validators = []
        for name in all_processors.keys():
            if issubclass(all_processors[name], NormalizerBase):
                print(" -  ", name)
                print(
                    "     -  Description training:"
                    f"{all_processors[name].DESCRIPTION_TRAINING}"
                )
                print(
                    "     -  Description decoding:"
                    f"{all_processors[name].DESCRIPTION_DECODING}"
                )
            else:
                validators.append(name)
        print()
        for name in validators:
            print(" -  ", name)
            print(
                "     -  Description:"
                f"{all_processors[name].DESCRIPTION_TRAINING}"
            )
        print()
        return

    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        Config.add_processors(set, project_dir)
    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Add bpe
@config.command()
@click.option("--joint", "-j", help="Joint bpe process", is_flag=True)
@click.option(
    "--num_iterations", "-n", help="Number of iterations", type=click.INT
)
@click.option("--threshold", "-t", help="Threshold bpe", type=click.INT)
@click.option("--pretrained", "-ptr", help="Model pretrained")
@click.option(
    "--sentencepiece", help="Use sentencepiece backend", is_flag=True
)
@click.option("--model_type", help="Model type for sentencepiece")
@click.option(
    "--vocab_size", help="Vocabulary size for sentencepiece", type=click.INT
)
@click.option("--project", "-p", "project_dir")
@click.pass_context
def bpe(
    ctx: Context,
    joint: bool,
    num_iterations: int,
    threshold: int,
    pretrained: str,
    sentencepiece: bool,
    model_type: str,
    vocab_size: int,
    project_dir: str
):

    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    if threshold is None:
        threshold = 50

    if num_iterations is None:
        num_iterations = 32000

    if pretrained:
        pretrained = os.path.abspath(pretrained)

    try:
        Config.add_bpe(
            joint,
            num_iterations,
            threshold,
            pretrained,
            sentencepiece,
            model_type,
            vocab_size,
            project_dir
        )
    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Add translation_model
@config.command()
@click.option("--name", "-n", help="Trainer name")
@click.option("--args", "-a", help="Arguments for the trainer")
@click.option("--list", "-l", help="List all available trainers", is_flag=True)
@click.option("--project", "-p", "project_dir")
@click.pass_context
def translation_model(
    ctx: Context, name: str, args: str, list: bool, project_dir: str,
):
    if list:
        print()
        print("### List of available trainers:\n")
        for name in TranslationModelFactory.get_available().keys():
            print(" -  ", name)
        print()
        return

    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    translation_model = TranslationModelFactory.get_class(name)
    args_decoding = translation_model.DEFAULT_DECODING
    if args is None:
        args = translation_model.DEFAULT

    try:
        Config.add_translation_model(name, args, args_decoding, project_dir)
    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Modify decoding args
@config.command()
@click.option("--arg", "-a", help="Argument to modify")
@click.option("--value", "-v", help="New value")
@click.option("--project", "-p", "project_dir")
@click.pass_context
def decoding_args(
    ctx: Context, arg: str, value: str, project_dir: str,
):
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        config = Config.load(project_dir)
        if config.translation_model is None:
            err = "Need to add a translation model before modifying its args"
            raise Exception(err)
        else:
            args_decode = config.translation_model["args_decoding"]
            old_value = args_decode[arg]
            args_decode[arg] = type(old_value)(value)
            Config.add_translation_model(
                config.translation_model["name"],
                config.translation_model["args"],
                args_decode,
                project_dir
            )
    except ProjectNotFoundException as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Error: {e}")


# Add reset command
@tea.command()
@click.option("--section", "-s", help="Name of the section to reset")
@click.option("--project", "-p", "project_dir")
@click.pass_context
def reset(ctx: Context, section: str, project_dir: str):
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = pathlib.Path(project_dir)

    try:
        Config.reset_section(section, project_dir)
    except ProjectNotFoundException as e:
        raise Exception("Command failed") from e


# Workflow group
@tea.group(invoke_without_command=True)
@click.option("--project", "-p", "project_dir")
@click.pass_context
async def workflow(ctx, project_dir):
    ctx.ensure_object(dict)
    if project_dir is None:
        project_dir = os.getcwd()
    project_dir = os.path.abspath(project_dir)
    project_dir = pathlib.Path(project_dir)
    ctx.obj["project"] = Project.load(project_dir)


# New workflow
@workflow.command()
@click.option("--force", "-f", default=False)
@click.pass_context
async def new(ctx: Context, force):
    """
    Init the workflow.
    """
    project = ctx.obj["project"]
    try:
        workflow = await Workflow.new(project, force)
        workflow.show()
    except (WorkflowAlreadyExists, Exception) as e:
        raise Exception("Command failed") from e


# Status workflow
@workflow.command()
@click.pass_context
async def status(ctx: Context):
    workflow = Workflow.load(ctx.obj["project"])
    workflow.show()


# Clean
@workflow.command()
@click.option(
    "--num_workers",
    "-n",
    type=click.INT,
    help="Max number of workers to be spawned.",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Debug mode."
)
@click.pass_context
async def clean(ctx: Context, num_workers: int = 1, debug: bool = False):
    if num_workers is None:
        raise ValueError(
            "Maximum number of workers not defined. i.e. clean -n 4"
        )
    try:
        workflow = Workflow.load(ctx.obj["project"])
        await workflow.run_stage("clean", num_workers, debug)
        click.echo("---> Done")
    except Exception as e:
        raise Exception("Command failed") from e


# Prepare
@workflow.command()
@click.option(
    "--num_workers",
    "-n",
    type=click.INT,
    help="Max number of workers to be spawned.",
)
@click.option(
    "--seed",
    "-s",
    type=click.INT,
    help="Seed for shuffling"
)
@click.pass_context
async def prepare(ctx: Context, seed: int, num_workers: int = 1):
    try:
        workflow = Workflow.load(ctx.obj["project"])
        await workflow.run_stage("prepare", num_workers, seed)
        click.echo("---> Done")
    except Exception as e:
        raise Exception("Command failed") from e


# Train
@workflow.command()
@click.option(
    "--gpu",
    "-g",
    type=click.INT,
    help="The GPU where the model will be trained",
)
@click.option(
    "--continue_train",
    "-c",
    help="Name of the model from which to resume training",
)
@click.pass_context
async def train(ctx: Context, gpu: int, continue_train: str):
    try:
        workflow = Workflow.load(ctx.obj["project"])
        if continue_train is None:
            await workflow.run_stage("train", gpu)
            click.echo("---> Done")
        else:
            train_stage = TrainStage(workflow)
            await train_stage.run(gpu, continue_train)
    except Exception as e:
        raise Exception("Command failed") from e


# Eval
@workflow.command()
@click.option(
    "--gpu",
    "-g",
    type=click.INT,
    help="The GPU where the model will be evaluated",
)
@click.option(
    "--step",
    "-s",
    type=click.INT,
    help="The steps of the desired model to evaluate",
)
@click.option(
    "--src", help="Source file for evaluation",
)
@click.option(
    "--ref", help="Reference file path"
)
@click.option(
    "--out", help="Output file name"
)
@click.option(
    "--log", help="Log file name"
)
@click.option(
    "--debug", help="Debugging flag", is_flag=True
)
@click.pass_context
async def eval(
    ctx: Context,
    gpu: int,
    step: int,
    src: str,
    ref: str,
    out: str,
    log: str,
    debug: bool
):
    try:
        workflow = Workflow.load(ctx.obj["project"])
        if src is not None:
            if ref is not None:
                eval_stage = EvalStage(workflow)
                await eval_stage.eval_files(
                    gpu, step, src, ref, out, log, debug
                )
            else:
                print("Reference path missing")
        else:
            await workflow.run_stage("eval", gpu, step)
        click.echo("---> Done")
    except Exception as e:
        raise Exception("Command failed") from e


# Reset workflow
@workflow.command()
@click.option(
    "--stage", "-s", help="Stage to reset",
)
@click.pass_context
async def reset(ctx: Context, stage: str):
    try:
        project = ctx.obj["project"]
        workflow = Workflow.load(project)
        if stage is None:
            workflow.reset(project.config.project_dir)
        else:
            workflow.reset_stage(stage, project.config.project_dir)
    except Exception as e:
        raise Exception("Command failed") from e


def main():
    tea(_anyio_backend="asyncio")  # or asyncio, or curio


class RequireOptionExpcetion(Exception):
    def __init__(self, command: str, variable: str):
        super().__init__(f"Error: {command} {variable} is required")


if __name__ == "__main__":
    main()
