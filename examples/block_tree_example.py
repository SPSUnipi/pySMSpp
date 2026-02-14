"""
Example demonstrating the print_block_tree utility function and Block.print_tree() method.

This script shows how to visualize the hierarchical structure of blocks
in a SMS++ network using both the standalone function and the instance method.
"""

import pysmspp

# Example 1: Using the Block.print_tree() method
print("=" * 70)
print("Example 1: Using Block.print_tree() method")
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

# Display the basic tree structure using the method
print("\nBasic tree (blocks only) - using method:")
print("-" * 70)
network.print_tree("ExampleNetwork")

# Example 2: Using the standalone function
print("\n" + "=" * 70)
print("Example 2: Using standalone print_block_tree() function")
print("=" * 70)
pysmspp.print_block_tree(network, "ExampleNetwork")

# Example 3: Show dimensions using method
print("\n" + "=" * 70)
print("Example 3: Tree with dimensions (using method)")
print("=" * 70)
network.print_tree("ExampleNetwork", show_dimensions=True)

# Example 4: Show variables
print("\n" + "=" * 70)
print("Example 4: Tree with variables (using method)")
print("=" * 70)
network.print_tree("ExampleNetwork", show_variables=True)

# Example 5: Show all details using method
print("\n" + "=" * 70)
print("Example 5: Full tree with all details (using method)")
print("=" * 70)
network.print_tree(
    "ExampleNetwork",
    show_dimensions=True,
    show_variables=True,
    show_attributes=True,
)

# Example 6: Load from a file (if test data is available)
print("\n" + "=" * 70)
print("Example 6: Tree from a NetCDF file")
print("=" * 70)
try:
    # Try to load a sample network from test data
    fp = "test/test_data/microgrid_ALLbutStore_1N.nc4"
    net = pysmspp.SMSNetwork(fp)
    # Using the method
    net.print_tree(
        "MicrogridNetwork", show_dimensions=True, show_variables=True
    )
except FileNotFoundError:
    print("Sample network file not found. Skipping this example.")
    print("To use this example, run it from the repository root directory.")

print("\n" + "=" * 70)
print("Examples complete!")
print("=" * 70)
print("\nNote: Both block.print_tree() method and print_block_tree(block)")
print("      function are available and produce the same output.")
