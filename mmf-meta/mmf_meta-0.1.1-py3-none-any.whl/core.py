import dataclasses
import enum
import inspect
import os
import typing
from pathlib import Path
from dataclasses import asdict
from .descriptors import DescriptorBase

MMF_RUN = os.environ.get("MMF_RUN", "N") == "Y"
MAX_FILE_SIZE = 1024 * 1024 * 10
TARGETS = "__mmf_targets"
ARTIFACTS = "__mmf_artifacts"


class DescriptorError(ValueError):
    pass


@dataclasses.dataclass
class Target:
    foo: typing.Callable
    name: str = None
    description: str = None
    returns: DescriptorBase = None
    signature: typing.Dict[str, DescriptorBase] = None


def _check_foo(foo):
    sig = inspect.signature(foo)
    err = []
    has_files = False
    only_files = True
    signature = {}
    for p in sig.parameters.values():
        if not isinstance(p.default, DescriptorBase):
            err.append(p.name)
        if p.default.is_file:
            has_files = True
        else:
            only_files = False
        signature[p.name] = p.default
    if has_files and not only_files:
        raise DescriptorError(
            f"if has any file input, must have only file inputs (DataFrame, Image, JsonFile)"
        )
    if err:
        raise DescriptorError(
            f"All fields of {foo} must be described, but these fields does not: {err}"
        )
    return signature


def target(
    _foo=None,
    *,
    description: str = None,
    returns: DescriptorBase = None,
    name: str = None,
):
    """
    Декоратор. Отмечает функцию как таргет

    ``` python
    app = MMF()
    @app.target(returns=app.DataFrame(), description='Основной скоринг')
    def score(data = app.DataFrame()):
        return data
    ```

    :param description: описание, будет использоваться в веб-интерфейсе
    :param returns: дескриптор, описывает тип данных, который возвращает функция
    :param name: имя, если не будет указано, будет использоваться имя самой функции.
    :return:
    """

    targets = globals().get(TARGETS)
    if targets is None:
        globals()[TARGETS] = targets = []

    def deco(foo):
        signature = _check_foo(foo)
        target = Target(
            foo=foo,
            description=description or foo.__doc__,
            returns=returns,
            name=name or foo.__name__,
            signature=signature,
        )

        targets.append(target)

        return foo

    return deco(_foo) if _foo else deco


@dataclasses.dataclass
class Artifact:
    file: os.PathLike
    name: str = None
    description: str = None
    args: tuple = None
    kwargs: dict = None
    _file = None
    _loader: typing.Callable = None

    def __post_init__(self):
        if Path(self.file).exists():
            if Path(self.file).stat().st_size > MAX_FILE_SIZE and not MMF_RUN:
                raise ValueError(
                    f"{self.file} is bigger than MAX_FILE_SIZE={MAX_FILE_SIZE}"
                )

    def __call__(self, foo):
        self._loader = foo
        if MMF_RUN:
            return foo()
        return foo

    def __enter__(self):
        self._file = open(self.file, *self.args, **self.kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()


def artifact(
    file: typing.Union[os.PathLike, str],
    *args,
    name: str = None,
    description: str = None,
    **kwargs,
):
    """

    :param file: имя файла, будет так же использовано как id объекта на s3, соответсвенно в одном проекте не доспускается
        использование нескольких артефактов с одинаковым именем
    :param name: читаемое имя для веб-интерфейса, если не указано, буднт использовано имя файла
    :param description: описание
    :return:
    """
    art = Artifact(
        file=file, name=name, description=description, args=args, kwargs=kwargs
    )
    artifacts = globals().get(ARTIFACTS)
    if artifacts is None:
        globals()[ARTIFACTS] = artifacts = []
    artifacts.append(art)
    return art


def scan() -> typing.Tuple[typing.List[Target], typing.List[Artifact]]:
    targets = globals().get(TARGETS)
    artifacts = globals().get(ARTIFACTS)
    return targets, artifacts


def _wrap_value(n, v):
    if isinstance(v, enum.Enum):
        return v.value
    elif n in ("schema", "default"):
        return str(v)


def _factory(d):

    return dict(((n, _wrap_value(n, v)) for n, v in d))


def get_signature(t: typing.Union[Target, Artifact]):
    ret = asdict(t, dict_factory=_factory)
    if isinstance(t, Target):
        ret.pop("foo")
    else:
        ret.pop("args")
        ret.pop("kwargs")
        ret.pop("_loader")
    return ret
