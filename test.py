from pysmspp import SMSNetwork, Variable, Block, SMSFileType
import numpy as np

b = SMSNetwork(file_type=SMSFileType.eBlockFile)


thermal_unit_block = Block().from_kwargs(
    block_type="ThermalUnitBlock",
    MinPower=Variable("MinPower", "float", (), 0.0),
    MaxPower=Variable("MaxPower", "float", (), 100.0),
    LinearTerm=Variable("LinearTerm", "float", (), 0.3),
    InitUpDownTime=Variable("InitUpDownTime", "int", (), 1),
)

b.add(
    "UCBlock",
    "Block_0",
    id="0",
    TimeHorizon=24,
    NumberUnits=1,
    NumberElectricalGenerators=1,
    NumberNodes=1,
    ActivePowerDemand=Variable(
        "ActivePowerDemand",
        "float",
        ("NumberNodes", "TimeHorizon"),
        np.full((1, 24), 50.0),
    ),
)

b.blocks["Block_0"].add_block("UnitBlock_0", block=thermal_unit_block)

configfile = "test/test_data/configs/UCBlockSolver/uc_solverconfig.txt"
temporary_smspp_file = "./smspp_temp_file.nc"
output_file = "./smspp_output.txt"

result = b.optimize(
    configfile,
    temporary_smspp_file,
    output_file,
)


# b = SMSNetwork(file_type=SMSFileType.eBlockFile)


# thermal_unit_block = Block().from_kwargs(
#     block_type="ThermalUnitBlock",
#     MinPower=Variable("MinPower", "float", (), 0.0),
#     MaxPower=Variable("MaxPower", "float", (), 100.),
#     LinearTerm=Variable("LinearTerm", "float", (), 0.3),
#     InitUpDownTime=Variable("InitUpDownTime", "int", (), 1),
# )

# b.add(
#     "UCBlock",
#     "Block_0",
#     id="0",
#     TimeHorizon=24,
#     NumberUnits=1,
#     NumberElectricalGenerators=1,
#     NumberNodes=1,
#     ActivePowerDemand=Variable(
#         "ActivePowerDemand",
#         "float",
#         ("NumberNodes", "TimeHorizon"),
#         np.full((1, 24), 50.),
#     ),
#     UnitBlock_0=thermal_unit_block,
# )
