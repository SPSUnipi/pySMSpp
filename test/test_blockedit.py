from smspy import SMSNetwork, Block, Variable


def test_attribute():
    b = SMSNetwork()

    b.add("Attribute", "test_attr", "test_value")
    assert b.attributes["test_attr"] == "test_value"
    b.add("Attribute", "test_attr_num", 1)
    assert b.attributes["test_attr_num"] == 1

    b.remove("Attribute", "test_attr")
    assert "test_attr" not in b.attributes


def test_dimension():
    b = SMSNetwork()
    b.add("Dimension", "test_dim", 1)
    assert b.dimensions["test_dim"] == 1

    b.remove("Dimension", "test_dim")
    assert "test_dim" not in b.dimensions


def test_variable():
    b = SMSNetwork()
    b.add(
        "Variable",
        "test_var",
        var_type="int",
        dimensions=tuple(),
        data=1,
    )
    assert b.variables["test_var"].data == 1

    b.remove("Variable", "test_var")
    assert "test_var" not in b.variables


def test_fromkwargs():
    tb = Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", None, 0.0),
        MaxPower=Variable("MaxPower", "float", None, 100.0),
        LinearTerm=Variable("LinearTerm", "float", None, 0.3),
    )
    assert tb.block_type == "ThermalUnitBlock"
    assert tb.variables["MinPower"].data == 0


def test_add_block():
    b = SMSNetwork()
    b.add(
        "UCBlock",
        "UCBlock_0",
        TimeHorizon=24,
        NumberUnits=1,
        NumberElectricalGenerators=0,
        NumberNodes=3,
        NumberLines=2,
        GeneratorNode=Variable(
            "GeneratorNode", "int", ("NumberElectricalGenerators",), [0, 0, 0]
        ),
        StartLine=Variable("StartLine", "int", ("NumberNodes",), [0, 1]),
        EndLine=Variable("EndLine", "int", ("NumberNodes",), [1, 2]),
        MinPowerFlow=Variable("MinPowerFlow", "float", ("NumberNodes",), [0.0, 0.0]),
        MaxPowerFlow=Variable(
            "MaxPowerFlow", "float", ("NumberNodes",), [100.0, 100.0]
        ),
    )


def test_add_block_with_subblocks():
    tb = Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", None, 0.0),
        MaxPower=Variable("MaxPower", "float", None, 100.0),
        LinearTerm=Variable("LinearTerm", "float", None, 0.3),
    )
    b = SMSNetwork()
    b.add(
        "UCBlock",
        "UCBlock_0",
        TimeHorizon=24,
        NumberUnits=1,
        NumberElectricalGenerators=0,
        NumberNodes=3,
        NumberLines=2,
        GeneratorNode=Variable(
            "GeneratorNode", "int", ("NumberElectricalGenerators",), [0, 0, 0]
        ),
        StartLine=Variable("StartLine", "int", ("NumberNodes",), [0, 1]),
        EndLine=Variable("EndLine", "int", ("NumberNodes",), [1, 2]),
        MinPowerFlow=Variable("MinPowerFlow", "float", ("NumberNodes",), [0.0, 0.0]),
        MaxPowerFlow=Variable(
            "MaxPowerFlow", "float", ("NumberNodes",), [100.0, 100.0]
        ),
        UnitBlock_0=tb,
    )
