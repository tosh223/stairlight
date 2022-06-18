import os
from collections import OrderedDict

import pytest

from src.stairlight.configurator import (
    MAPPING_CONFIG_PREFIX_DEFAULT,
    STAIRLIGHT_CONFIG_PREFIX_DEFAULT,
    Configurator,
)
from src.stairlight.source.config_key import (
    MapKey,
    MappingConfigKey,
    StairlightConfigKey,
)
from src.stairlight.source.file.template import FileTemplate


class TestSuccess:
    def test_read_mapping(self, configurator: Configurator):
        assert configurator.read_mapping(prefix=MAPPING_CONFIG_PREFIX_DEFAULT)

    def test_read_stairlight(self, configurator: Configurator):
        assert configurator.read_stairlight(prefix=STAIRLIGHT_CONFIG_PREFIX_DEFAULT)

    def test_create_stairlight_file(
        self, configurator: Configurator, stairlight_template_prefix: str
    ):
        file_name = configurator.create_stairlight_file(
            prefix=stairlight_template_prefix
        )
        assert os.path.exists(file_name)

    def test_create_mapping_file(
        self, configurator: Configurator, mapping_template_prefix: str
    ):
        file_name = configurator.create_mapping_file(
            unmapped=[], prefix=mapping_template_prefix
        )
        assert os.path.exists(file_name)

    def test_build_stairlight_config(self, configurator: Configurator):
        stairlight_template = configurator.build_stairlight_config()
        assert list(stairlight_template.keys()) == [
            StairlightConfigKey.INCLUDE_SECTION,
            StairlightConfigKey.EXCLUDE_SECTION,
            StairlightConfigKey.SETTING_SECTION,
        ]

    @pytest.fixture(scope="class")
    def file_template(self, configurator: Configurator) -> FileTemplate:
        return FileTemplate(
            mapping_config=configurator.read_mapping(
                prefix=MAPPING_CONFIG_PREFIX_DEFAULT
            ),
            key="tests/sql/main/test_undefined.sql",
        )

    def test_build_mapping_config(
        self, configurator: Configurator, file_template: FileTemplate
    ):
        unmapped_templates = [
            {
                MapKey.TEMPLATE: file_template,
                MapKey.PARAMETERS: [
                    "params.main_table",
                    "params.sub_table_01",
                    "params.sub_table_02",
                ],
            }
        ]

        global_value: OrderedDict = OrderedDict({MappingConfigKey.PARAMETERS: {}})
        mapping_value = OrderedDict(
            {
                MappingConfigKey.TEMPLATE_SOURCE_TYPE: file_template.source_type.value,
                MappingConfigKey.TABLES: [
                    OrderedDict(
                        {
                            MappingConfigKey.TABLE_NAME: "test_undefined",
                            MappingConfigKey.IGNORE_PARAMETERS: [],
                            MappingConfigKey.PARAMETERS: OrderedDict(
                                {
                                    "params": {
                                        "main_table": None,
                                        "sub_table_01": None,
                                        "sub_table_02": None,
                                    }
                                }
                            ),
                            MappingConfigKey.LABELS: OrderedDict(),
                        }
                    )
                ],
                MappingConfigKey.File.FILE_SUFFIX: file_template.key,
            }
        )

        metadata_value: OrderedDict = OrderedDict(
            {
                MappingConfigKey.TABLE_NAME: None,
                MappingConfigKey.LABELS: OrderedDict(),
            }
        )

        expected = OrderedDict(
            {
                MappingConfigKey.GLOBAL_SECTION: global_value,
                MappingConfigKey.MAPPING_SECTION: [mapping_value],
                MappingConfigKey.METADATA_SECTION: [metadata_value],
            }
        )
        actual = configurator.build_mapping_config(
            unmapped_templates=unmapped_templates
        )
        assert actual == expected
