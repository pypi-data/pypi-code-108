"""Parameter tests."""

import pytest
from finesse.components import Beamsplitter, Laser, Mirror, Variable
from finesse.frequency import Fsig


@pytest.mark.parametrize(
    "component_type,args,parameter_default_status",
    (
        # Components without default parameters.
        (Laser, ["l1"], {k: False for k in ("P", "phase", "f")}),
        (Mirror, ["m1"], {k: False for k in ("R", "T", "L", "phi")}),
        # Components with default parameters.
        (Variable, ["var1", 1], {"value": True}),
        (Fsig, ["signal", 1e6], {"f": True}),
    ),
)
def test_default_model_parameters(component_type, args, parameter_default_status):
    """Model parameters listed as the default in their owner should know."""
    component = component_type(*args)

    for name, status in parameter_default_status.items():
        param = getattr(component, name)
        assert param.is_default_for_owner == status

@pytest.mark.parametrize(
    "component_type,args,params",
    (
        (Laser, ["l1"], ("P", "phase", "f", "signals_only")),
        (Mirror, ["m1"], ("R", "T", "L", "phi")),
        (Beamsplitter, ["bs"], ("R", "T", "L", "phi"))
    )
    ,
)
def test_specific_parameter_help(component_type, args, params):
    """Check that the docstring for parameters gets replaced."""
    component = component_type(*args)
    for param in params:
        attr = getattr(component, param)
        assert attr.__doc__ != type(attr).__doc__
