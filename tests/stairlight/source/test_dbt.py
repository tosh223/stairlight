import pytest

from src.stairlight import config_key
from src.stairlight.source.dbt import (
    DbtTemplate,
    DbtTemplateSource,
    TemplateSourceType,
)


@pytest.mark.parametrize(
    "project_dir, project_name, profiles_dir, profile, target, vars",
    [
        (
            "tests/dbt/project_01",
            "project_01",
            "tests/dbt",
            "profile_01",
            "prod",
            {
                "key_a": "value_a",
                "key_b": "value_b",
            },
        ),
        (
            "tests/dbt/project_02",
            "project_02",
            "tests/dbt",
            "profile_02",
            "dev",
            {},
        ),
    ],
)
class TestDbtTemplateSource:
    @pytest.fixture(scope="function")
    def dbt_template_source(
        self,
        stairlight_config: dict,
        mapping_config: dict,
        project_dir: str,
        profiles_dir: str,
        profile: str,
        target: str,
        vars: dict,
    ) -> DbtTemplateSource:
        source_attributes = {
            config_key.TEMPLATE_SOURCE_TYPE: TemplateSourceType.DBT.value,
            config_key.DBT_PROJECT_DIR: project_dir,
            config_key.DBT_PROFILES_DIR: profiles_dir,
            config_key.DBT_PROFILE: profile,
            config_key.DBT_TARGET : target,
            config_key.DBT_VARS : vars,
        }
        return DbtTemplateSource(
            stairlight_config=stairlight_config,
            mapping_config=mapping_config,
            source_attributes=source_attributes,
        )

    def test_search_templates_iter(
        self,
        dbt_template_source: DbtTemplateSource,
        project_name: str,
    ):
        result = []
        for template in dbt_template_source.search_templates_iter():
            result.append(template)
        assert len(result) > 0

    def test_execute_dbt_compile(
        self,
        dbt_template_source: DbtTemplateSource,
        project_dir: str,
        project_name: str,
        profiles_dir: str,
        profile: str,
        target: str,
        vars: dict,
    ):
        actual = dbt_template_source.execute_dbt_compile(
            project_dir=project_dir,
            profiles_dir=profiles_dir,
            profile=profile,
            target=target,
            vars=vars,
        )
        assert actual == 0

    def test_read_dbt_project_yml(
        self,
        dbt_template_source: DbtTemplateSource,
        project_dir: str,
        project_name: str,
    ):
        actual = dbt_template_source.read_dbt_project_yml(
            project_dir=project_dir
        )
        assert actual['name'] == project_name