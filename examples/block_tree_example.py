"""
Example demonstrating the print_block_tree utility function.

This script shows how to visualize the hierarchical structure of blocks
in a SMS++ network using the print_block_tree function.
"""

import pysmspp

# Example 1: Load and visualize a sample network
print("=" * 70)
print("Example 1: Basic block tree visualization")
print("=" * 70)

# Create a simple network with nested blocks
network = pysmspp.Block()
network.block_type = "SMSNetwork"

# Add a UCBlock
ucblock = pysmspp.Block()
ucblock.block_type = "UCBlock"
ucblock.add_dimension("TimeHorizon", 24)
ucblock.add_dimension("NumberUnits", 3)
ucblock.add_variable("ActivePowerDemand", "float", ("TimeHorizon",), [10.0] * 24)

# Add some unit blocks
thermal = pysmspp.Block()
thermal.block_type = "ThermalUnitBlock"
thermal.add_variable("MinPower", "float", (), 0.0)
thermal.add_variable("MaxPower", "float", (), 100.0)
thermal.add_attribute("id", 0)

battery = pysmspp.Block()
battery.block_type = "BatteryUnitBlock"
battery.add_variable("MinPower", "float", (), -50.0)
battery.add_variable("MaxPower", "float", (), 50.0)
battery.add_variable("MaxStorage", "float", (), 200.0)
battery.add_attribute("id", 1)

ucblock.blocks["UnitBlock_0"] = thermal
ucblock.blocks["UnitBlock_1"] = battery

network.blocks["Block_0"] = ucblock

# Display the basic tree structure
print("\nBasic tree (blocks only):")
print("-" * 70)
pysmspp.print_block_tree(network, "ExampleNetwork")

# Example 2: Show dimensions
print("\n" + "=" * 70)
print("Example 2: Tree with dimensions")
print("=" * 70)
pysmspp.print_block_tree(network, "ExampleNetwork", show_dimensions=True)

# Example 3: Show variables
print("\n" + "=" * 70)
print("Example 3: Tree with variables")
print("=" * 70)
pysmspp.print_block_tree(network, "ExampleNetwork", show_variables=True)

# Example 4: Show all details
print("\n" + "=" * 70)
print("Example 4: Full tree with all details")
print("=" * 70)
pysmspp.print_block_tree(
    network,
    "ExampleNetwork",
    show_dimensions=True,
    show_variables=True,
    show_attributes=True,
)

# Example 5: Load from a file (if test data is available)
print("\n" + "=" * 70)
print("Example 5: Tree from a NetCDF file")
print("=" * 70)
try:
    # Try to load a sample network from test data
    fp = "test/test_data/microgrid_ALLbutStore_1N.nc4"
    net = pysmspp.SMSNetwork(fp)
    pysmspp.print_block_tree(
        net, "MicrogridNetwork", show_dimensions=True, show_variables=True
    )
except FileNotFoundError:
    print("Sample network file not found. Skipping this example.")
    print("To use this example, run it from the repository root directory.")

print("\n" + "=" * 70)
print("Examples complete!")
print("=" * 70)
