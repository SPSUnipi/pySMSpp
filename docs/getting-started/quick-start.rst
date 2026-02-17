###########
Quick Start
###########

To install the package, please refer to :doc:`/getting-started/installation`.

In the following, we provide a quick example on how to add a simple optimization model with SMS++.
The problem that follows optimizes the dispatch of a single thermal generator of 100kW to meet the demand of a constant load over 24 hours in one bus.

A sample SMS++ network can be created with the following code. After python imports, the code creates a new SMS++ network `sn` with the block file format. The block file format is a text file that contains only the model data in a structured way, with no solver information. The solver information is provided in a separate configuration file.

.. code:: python

    from pysmspp import SMSNetwork, Variable, Block, SMSFileType, SMSConfig
    import numpy as np

    sn = SMSNetwork(file_type=SMSFileType.eBlockFile)

After an empty network is created, we can populate it with blocks. In particular, it is critical to add a first inner block that describes
the type of model to be optimized. In this case, we are adding a ``UCBlock`` suitable for unit commitment problems, see the `UCBlock SMS documentation <https://gitlab.com/smspp/ucblock>`__ for details. A ``UCBlock`` is a block that describes unit commitment problems. In particular, we specify 24 time steps (one day) and a constant demand of 50kW for each time step. The block is added to the network with the following code:

.. code:: python

    sn.add(
        "UCBlock",  # block type
        "Block_0",  # block name
        id="0",  # block id
        TimeHorizon=24,  # number of time steps
        NumberUnits=1,  # number of units
        NumberElectricalGenerators=1,  # number of electrical generators
        NumberNodes=1,  # number of nodes
        ActivePowerDemand=Variable(  # active power demand
            "ActivePowerDemand",
            "float",
            ("NumberNodes", "TimeHorizon"),
            np.full((1, 24), 50.),  # constant demand of 50kW
        ),
    )

In the unit commitment block stated above, no generator is yet added. To add a generator, we first create a ``ThermalUnitBlock`` block using the code below and we add it to the network. The following code adds a thermal unit block to the network. The block is added to the network with the following code:

.. code:: python

    thermal_unit_block = Block().from_kwargs(
        block_type="ThermalUnitBlock",
        MinPower=Variable("MinPower", "float", (), 0.0),
        MaxPower=Variable("MaxPower", "float", (), 100.),
        LinearTerm=Variable("LinearTerm", "float", (), 0.3),
        InitUpDownTime=Variable("InitUpDownTime", "int", (), 1),
    )

    sn.blocks["Block_0"].add("ThermalUnitBlock", "UnitBlock_0", block=thermal_unit_block)


Finally, the network is optimized with the following code:

.. code:: python
    
    configfile = SMSConfig(template="uc_solverconfig")  # path to the template solver config file "uc_solverconfig"
    temporary_smspp_file = "./smspp_temp_file.nc"  # path to the temporary SMS++ file used as intermediate file to launch SMS++
    output_file = "./smspp_output.txt"  # path to the output file (optional)

    result = sn.optimize(
        configfile,
        temporary_smspp_file,
        output_file,
    )

Finally, basic information are stored in the result object, see:

.. code:: python

    print("Status: ", result.status)
    print("Objective value: ", result.objective_value)