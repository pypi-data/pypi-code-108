import glob
import os
import re
import shutil
import subprocess  # nosec
from os.path import basename
from pathlib import Path

from fhir_cli import (
    CDM_LIST,
    DBT_INCREMENTAL_MODEL_TEMPLATE,
    DBT_MODELS_DIR,
    JINJA_ENV,
    MAPPING_DIR_NAME,
    log,
)


class UnknownDbtReferenceError(ValueError):
    pass


class EmptyDbtReferenceWarning(UserWarning):
    pass


def resolve_references(line: str) -> str:
    """resolve_references takes a line of a sql statement and looks for dbt references

    It looks for a comment such as `-- dbt-ref(reference_1, reference_2)` and replaces
    on the same line `reference_1` and `reference_2` by the jinja dbt references
    `{{ref('reference_1')}}` and `{{ref('reference_2')}}`

    Args:
        line (str): a line in the processed sql statement

    Returns:
        str: a new line with the references resolved or the input `line` if no reference
        have been found

    Raises:
        UnknownDbtReferenceError: if a reference is specified but not found in the line
        EmptyDbtReferenceWarning: if dbt-ref doesn't specify at least one reference
    """
    dbt_ref_pattern = r"(.*\b)(\s*--[ \t]*dbt-ref\((.*)\).*)"
    result = re.search(dbt_ref_pattern, line)
    if not result:
        return line
    stmt = result.group(1)
    references = [
        reference.strip() for reference in result.group(3).split(",") if reference.strip()
    ]
    if not references:
        raise EmptyDbtReferenceWarning("no reference has been specified")
    for reference in references:
        stmt, match = re.subn(fr"(\s+|^){reference}\b", f"\\1{{{{ref('{reference}')}}}}", stmt)
        if not match:
            raise UnknownDbtReferenceError(f"{reference} is unknown")
    return stmt


class Dbt:
    """The dbt command manages your DBT project"""

    @staticmethod
    def transpile(incremental: bool = False):
        """Create the DBT models folder including all files in
        the schemas folder. It then compiles the sql files into DBT models by resolving
        DBT references and adding model configurations if needed.

        Args:
            incremental (bool): when True, the DBT models are configured to be incremental
        """
        if os.path.exists(DBT_MODELS_DIR):
            shutil.rmtree(DBT_MODELS_DIR)
        shutil.copytree(MAPPING_DIR_NAME, DBT_MODELS_DIR)

        for file_path in glob.iglob(f"{MAPPING_DIR_NAME}/**/*.sql", recursive=True):
            with open(file_path, "r") as f:
                with open(
                    f"{DBT_MODELS_DIR}{file_path.removeprefix(MAPPING_DIR_NAME)}", "w"
                ) as model_file:
                    output = []
                    for index, line in enumerate(f):
                        try:
                            new_line = resolve_references(line)
                        except UnknownDbtReferenceError as e:
                            log.error(f"model {file_path} line {index + 1}:\n{line}\nError: {e}")
                            shutil.rmtree(DBT_MODELS_DIR)
                            return
                        except EmptyDbtReferenceWarning as e:
                            log.warning(
                                f"model {file_path} line {index + 1}:\n{line}\nWarning: {e}"
                            )
                            new_line = line
                        parent_folder = basename(Path(file_path).parent)
                        output = [*output, new_line]
                    stmt = "\n".join(output)
                    if incremental and parent_folder in CDM_LIST:
                        stmt = JINJA_ENV.get_template(DBT_INCREMENTAL_MODEL_TEMPLATE).render(
                            stmt=stmt, target_schema=parent_folder
                        )
                    model_file.write(stmt)

    def run(self, select: str = "", exclude: str = "", incremental: bool = False):
        """Compile the sql files then runs DBT

        Args:
            select (str): use it the same way you would use the select flag with the dbt CLI
            exclude (str): use it the same way you would use the exclude flag with the dbt CLI
            incremental (bool): when True, make the DBT models incremental
        """
        self.transpile(incremental)
        cmd = ["dbt", "run", "--fail-fast"]
        if select:
            cmd.append("--select")
            cmd.append(select)
        if exclude:
            cmd.append("--exclude")
            cmd.append(exclude)
        subprocess.run(cmd, env=os.environ.copy())  # nosec

    def refresh(self):
        """Refresh DBT incremental models"""
        self.transpile(incremental=True)
        subprocess.run(["dbt", "run", "--fail-fast --full-refresh"], env=os.environ.copy())  # nosec
