from enum import Enum
from logging import getLogger
from multiprocessing import Pool, cpu_count
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict, List, Optional

from attr import attrs

from deckz.compiling import CompileResult
from deckz.compiling import compile as compiling_compile
from deckz.exceptions import DeckzException
from deckz.paths import Paths
from deckz.rendering import Renderer
from deckz.settings import Settings
from deckz.targets import Target, Targets
from deckz.utils import copy_file_if_newer


class CompileType(Enum):
    Handout = "handout"
    Presentation = "presentation"
    PrintHandout = "print-handout"


@attrs(auto_attribs=True, frozen=True)
class CompileItem:
    target: Target
    compile_type: CompileType
    toc: bool


class Builder:
    def __init__(
        self,
        latex_config: Dict[str, Any],
        settings: Settings,
        paths: Paths,
        targets: Targets,
        build_presentation: bool,
        build_handout: bool,
        build_print: bool,
    ):
        self._latex_config = latex_config
        self._settings = settings
        self._paths = paths
        self._targets = targets
        self._presentation = build_presentation
        self._handout = build_handout
        self._print = build_print
        self._logger = getLogger(__name__)
        self._renderer = Renderer(paths, settings)

    def _list_items(self) -> List[CompileItem]:
        to_compile = []
        all_target = Target.from_targets(self._targets, "all")
        if self._handout:
            to_compile.append(CompileItem(all_target, CompileType.Handout, True))
        if self._print:
            to_compile.append(CompileItem(all_target, CompileType.PrintHandout, True))
        for target in self._targets:
            if self._presentation:
                to_compile.append(CompileItem(target, CompileType.Presentation, False))
            if self._handout:
                to_compile.append(CompileItem(target, CompileType.Handout, False))
        to_compile.sort(key=lambda item: (item.target.name, item.compile_type.value))
        return to_compile

    def build(self) -> bool:
        items = self._list_items()
        n_outputs = (
            int(self._handout) * (len(self._targets) + 1)
            + int(self._presentation) * len(self._targets)
            + int(self._print)
        )
        self._logger.info(f"Building {len(items)} PDFs used in {n_outputs} outputs")
        with Pool(min(cpu_count(), len(items))) as pool:
            results = pool.map(self._build_item, items)
        for item, result in zip(items, results):
            if item.target is not None:
                compilation = f"{item.target.name}/{item.compile_type.value}"
            else:
                compilation = item.compile_type.value
            if not result.ok:
                self._logger.warning("Compilation %s errored", compilation)
                self._logger.warning(
                    "Captured %s stderr\n%s", compilation, result.stderr
                )
                self._logger.warning(
                    "Captured %s stdout\n%s", compilation, result.stdout
                )
        return all(result.ok for result in results)

    def _get_filename(self, target: Optional[Target], compile_type: CompileType) -> str:
        name = self._latex_config["deck_acronym"]
        if target is not None:
            name += f"-{target.name}"
        name += f"-{compile_type.value}"
        return name.lower()

    def _build_item(self, item: CompileItem) -> CompileResult:
        build_dir = self._setup_build_dir(item.target, item.compile_type)
        filename = self._get_filename(item.target, item.compile_type)
        latex_path = build_dir / f"{filename}.tex"
        build_pdf_path = latex_path.with_suffix(".pdf")
        output_pdf_path = self._paths.pdf_dir / f"{filename}.pdf"
        self._render_latex(item, latex_path)
        copied = self._copy_dependencies(item.target, build_dir)
        self._render_dependencies(copied, build_dir)
        result = compiling_compile(latex_path, self._settings)
        if result.ok:
            self._paths.pdf_dir.mkdir(parents=True, exist_ok=True)
            copyfile(build_pdf_path, output_pdf_path)
        return result

    def _setup_build_dir(
        self, target: Optional[Target], compile_type: CompileType
    ) -> Path:
        target_build_dir = self._paths.build_dir
        if target is not None:
            target_build_dir /= target.name
        target_build_dir /= compile_type.value
        target_build_dir.mkdir(parents=True, exist_ok=True)
        for item in [
            self._paths.shared_img_dir,
            self._paths.shared_tikz_pdf_dir,
            self._paths.shared_plt_pdf_dir,
            self._paths.shared_code_dir,
        ]:
            self._setup_link(target_build_dir / item.name, item)
        return target_build_dir

    def _render_latex(self, item: CompileItem, output_path: Path) -> None:
        self._renderer.render(
            template_path=self._paths.jinja2_main_template,
            output_path=output_path,
            config=self._latex_config,
            target=item.target,
            handout=item.compile_type
            in [CompileType.Handout, CompileType.PrintHandout],
            toc=item.toc,
            print=item.compile_type is CompileType.PrintHandout,
        )

    def _copy_dependencies(self, target: Target, target_build_dir: Path) -> List[Path]:
        copied = []
        for dependency in target.dependencies.used:
            try:
                link_dir = (
                    target_build_dir
                    / dependency.relative_to(self._paths.shared_dir).parent
                )
            except ValueError:
                link_dir = (
                    target_build_dir
                    / dependency.relative_to(self._paths.current_dir).parent
                )
            link_dir.mkdir(parents=True, exist_ok=True)
            destination = (link_dir / dependency.name).with_suffix(".tex.j2")
            if (
                not destination.exists()
                or destination.stat().st_mtime < dependency.stat().st_mtime
            ):
                copy_file_if_newer(dependency, destination)
                copied.append(destination)
        return copied

    def _render_dependencies(
        self, to_render: List[Path], target_build_dir: Path
    ) -> None:
        for item in to_render:
            self._renderer.render(template_path=item, output_path=item.with_suffix(""))

    def _setup_link(self, source: Path, target: Path) -> None:
        if not target.exists():
            raise DeckzException(
                f"{target} could not be found. Please make sure it exists before "
                "proceeding."
            )
        target = target.resolve()
        if source.is_symlink():
            if source.resolve().samefile(target):
                return
            raise DeckzException(
                f"{source} already exists in the build directory and does not point to "
                f"{target}. Please clean the build directory."
            )
        elif source.exists():
            raise DeckzException(
                f"{source} already exists in the build directory. Please clean the "
                "build directory."
            )
        source.parent.mkdir(parents=True, exist_ok=True)
        source.symlink_to(target)
