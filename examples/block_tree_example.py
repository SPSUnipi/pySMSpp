"""
Example demonstrating the Block.print_tree() method.

This script shows how to visualize the hierarchical structure of blocks
in a SMS++ network using the instance method.
"""

import pysmspp

# Example 1: Using the Block.print_tree() method without arguments
print("=" * 70)
print("Example 1: Using Block.print_tree() without arguments")
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

# Display the basic tree structure using the method - uses block_type as name
print("\nBasic tree (blocks only) - uses block_type as default name:")
print("-" * 70)
network.print_tree()

# Example 2: Using method with custom name
print("\n" + "=" * 70)
print("Example 2: Tree with custom name")
print("=" * 70)
network.print_tree("ExampleNetwork")

# Example 3: Show dimensions using method
print("\n" + "=" * 70)
print("Example 3: Tree with dimensions")
print("=" * 70)
network.print_tree(show_dimensions=True)

# Example 4: Show variables
print("\n" + "=" * 70)
print("Example 4: Tree with variables")
print("=" * 70)
network.print_tree(show_variables=True)

# Example 5: Show all details using method
print("\n" + "=" * 70)
print("Example 5: Full tree with all details")
print("=" * 70)
network.print_tree(
    show_dimensions=True,
    show_variables=True,
    show_attributes=True,
)

# Example 6: Load from a file and test SMSNetwork default name
print("\n" + "=" * 70)
print("Example 6: SMSNetwork from file - uses 'SMSNetwork' as default")
print("=" * 70)
try:
    # Try to load a sample network from test data
    fp = "test/test_data/microgrid_ALLbutStore_1N.nc4"
    net = pysmspp.SMSNetwork(fp)
    # Using the method without name parameter - defaults to "SMSNetwork"
    net.print_tree(show_dimensions=True, show_variables=True)
except FileNotFoundError:
    print("Sample network file not found. Skipping this example.")
    print("To use this example, run it from the repository root directory.")

print("\n" + "=" * 70)
print("Examples complete!")
print("=" * 70)
print("\nNote: The block.print_tree() method can be called in multiple ways:")
print("      - block.print_tree() - Uses block_type as name (or 'Block' if no type)")
print("      - block.print_tree('CustomName') - Uses custom name")
print("      - block.print_tree(show_dimensions=True) - With options")
print("      - For SMSNetwork: net.print_tree() defaults to 'SMSNetwork'")
