import pytest
import tempfile

from calliope.utils import AttrDict

from calliope import analysis

from . import common
from .common import assert_almost_equal, solver


class TestModel:
    @pytest.fixture(scope='module')
    def model(self):
        locations = """
            locations:
                1:
                    level: 1
                    within:
                    techs: ['ccgt', 'demand_electricity']
                    override:
                        ccgt:
                            constraints:
                                e_cap_max: 100
                        demand_electricity:
                            constraints:
                                r: -50
            links:
        """
        config_run = """
            mode: plan
            input:
                model: [{techs}, {locations}]
                data_path: '{path}'
            output:
                save: false
            subset_t: ['2005-01-01', '2005-01-02']
        """
        with tempfile.NamedTemporaryFile() as f:
            f.write(locations.encode('utf-8'))
            f.read()
            model = common.simple_model(config_run=config_run,
                                        config_locations=f.name,
                                        override=AttrDict({'solver': solver}))
        model.run()
        return model

    def test_recompute_levelized_costs(self, model):
        # Cost in solution
        df = model.solution.levelized_cost
        assert_almost_equal(df.at['monetary', 'power', 'total', 'ccgt'], 0.1)
        # Recomputed cost must be the same
        dm = analysis.DummyModel(model.solution)
        recomputed = dm.recompute_levelized_costs('ccgt')
        assert_almost_equal(recomputed['total'], 0.1)