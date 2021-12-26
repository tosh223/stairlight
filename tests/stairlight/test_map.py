import src.stairlight.config as config
from src.stairlight.map import Map


class TestSuccess:
    configurator = config.Configurator(dir="./config")
    map_config = configurator.read(prefix=config.MAP_CONFIG_PREFIX)
    strl_config = configurator.read(prefix=config.STRL_CONFIG_PREFIX)
    dependency_map = Map(strl_config=strl_config, map_config=map_config)
    dependency_map.write()

    def test_mapped(self):
        assert len(self.dependency_map.mapped) > 0

    def test_unmapped(self):
        assert len(self.dependency_map.unmapped) > 0