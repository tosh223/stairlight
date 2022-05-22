import glob
import pathlib
import re
import shlex
import subprocess
from typing import Iterator

import yaml

from .. import config_key
from .base import Template, TemplateSource, TemplateSourceType


class DbtTemplate(Template):
    def __init__(
        self,
        mapping_config: dict,
        key: str,
        source_type: TemplateSourceType,
        project_name: str,
    ):
        super().__init__(
            mapping_config=mapping_config,
            key=key,
            source_type=source_type,
        )
        self.uri = self.get_uri()
        self.project_name = project_name

    def get_uri(self) -> str:
        """Get uri from file path

        Returns:
            str: uri
        """
        return str(pathlib.Path(self.key).resolve())

    def get_template_str(self) -> str:
        """Get template string that read from a file

        Returns:
            str: Template string
        """
        with open(self.key) as f:
            return f.read()

    def render(self, params: dict = None) -> str:
        return self.get_template_str()


class DbtTemplateSource(TemplateSource):
    def __init__(
        self,
        stairlight_config: dict,
        mapping_config: dict,
        source_attributes: dict,
    ) -> None:
        super().__init__(
            stairlight_config=stairlight_config,
            mapping_config=mapping_config,
        )
        self.source_attributes = source_attributes
        self.source_type = TemplateSourceType.DBT

    def search_templates_iter(self) -> Iterator[Template]:
        project_dir = self.source_attributes[config_key.DBT_PROJECT_DIR]
        _ = self.execute_dbt_compile(
            project_dir=project_dir,
            profiles_dir=self.source_attributes[config_key.DBT_PROFILES_DIR],
            profile=self.source_attributes[config_key.DBT_PROFILE],
            target=self.source_attributes[config_key.DBT_TARGET],
            vars=self.source_attributes[config_key.DBT_VARS],
        )

        dbt_project_config = self.read_dbt_project_yml(
            project_dir=project_dir
        )
        for model_path in dbt_project_config[config_key.DBT_MODEL_PATHS]:
            path = (
                f"{project_dir}/"
                f"{dbt_project_config[config_key.DBT_TARGET_PATH]}/"
                "compiled/"
                f"{dbt_project_config[config_key.DBT_PROJECT_NAME]}/"
                f"{model_path}/"
            )
            path_obj = pathlib.Path(path)
            for p in path_obj.glob("**/*"):
                if (
                    re.fullmatch(r"schema.yml/.*\.sql$", str(p))
                ) or self.is_excluded(source_type=self.source_type, key=str(p)):
                    self.logger.debug(f"{str(p)} is skipped.")
                    continue

                yield DbtTemplate(
                    mapping_config=self._mapping_config,
                    key=str(p),
                    source_type=self.source_type,
                    project_name=dbt_project_config[config_key.DBT_PROJECT_NAME],
                )

    @staticmethod
    def execute_dbt_compile(
        project_dir: str,
        profiles_dir: str,
        profile: str = None,
        target: str = None,
        vars: dict = None,
    ) -> int:
        command = (
            "dbt compile "
            f"--project-dir {project_dir} "
            f"--profiles-dir {profiles_dir} "
        )
        if profile:
            command += f"--profile {profile} "
        if target:
            command += f"--target {target} "
        if vars:
            command += f"--vars '{vars}' "
        proc = subprocess.run(
            args=shlex.split(command),
            shell=False,
        )
        if proc.returncode != 0:
            raise Exception(proc.stderr)
        return proc.returncode

    @staticmethod
    def read_dbt_project_yml(project_dir: str) -> dict:
        """Read dbt_project.yml

        Args:
            project_dir (str): dbt project directory

        Returns:
            dict: dbt project settings
        """
        project: dict = None
        pattern = f"^{project_dir}/dbt_project.yml$"
        project_files = [
            p
            for p in glob.glob(f"{project_dir}/**", recursive=False)
            if re.fullmatch(pattern, p)
        ]
        if project_files:
            with open(project_files[0]) as file:
                project = yaml.safe_load(file)
        else:
            raise Exception
        return project