"""Tests for the block tree visualization utility."""

from io import StringIO
import sys
from conftest import (
    get_network,
    add_base_ucblock,
    build_base_tub,
    build_base_bub,
)
import pysmspp


def capture_print_output(func, *args, **kwargs):
    """Capture printed output from a function."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        func(*args, **kwargs)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return output


def test_print_block_tree_basic():
    """Test basic tree printing with a simple block."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"

    output = capture_print_output(pysmspp.print_block_tree, block, "MyBlock")

    assert "MyBlock" in output
    assert "[TestBlock]" in output


def test_print_block_tree_with_nested_blocks():
    """Test tree printing with nested blocks."""
    parent = pysmspp.Block()
    parent.block_type = "ParentBlock"

    child1 = pysmspp.Block()
    child1.block_type = "ChildBlock1"

    child2 = pysmspp.Block()
    child2.block_type = "ChildBlock2"

    parent.blocks["Child1"] = child1
    parent.blocks["Child2"] = child2

    output = capture_print_output(pysmspp.print_block_tree, parent, "Parent")

    # Check structure
    assert "Parent [ParentBlock]" in output
    assert "Child1 [ChildBlock1]" in output
    assert "Child2 [ChildBlock2]" in output

    # Check tree connectors
    assert "└── " in output or "├── " in output


def test_print_block_tree_with_dimensions():
    """Test tree printing with dimensions displayed."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    block.add_dimension("n", 10)
    block.add_dimension("m", 5)

    output = capture_print_output(
        pysmspp.print_block_tree, block, "MyBlock", show_dimensions=True
    )

    assert "MyBlock [TestBlock]" in output
    assert "Dimensions:" in output
    assert "n=10" in output
    assert "m=5" in output


def test_print_block_tree_with_variables():
    """Test tree printing with variables displayed."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    block.add_variable("var1", "float", (), 1.0)
    block.add_variable("var2", "int", (), 2)

    output = capture_print_output(
        pysmspp.print_block_tree, block, "MyBlock", show_variables=True
    )

    assert "MyBlock [TestBlock]" in output
    assert "Variables:" in output
    assert "var1" in output
    assert "var2" in output


def test_print_block_tree_with_attributes():
    """Test tree printing with attributes displayed."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    block.add_attribute("attr1", "value1")
    block.add_attribute("attr2", 42)

    output = capture_print_output(
        pysmspp.print_block_tree, block, "MyBlock", show_attributes=True
    )

    assert "MyBlock [TestBlock]" in output
    assert "Attributes:" in output
    assert "attr1=value1" in output
    assert "attr2=42" in output


def test_print_block_tree_with_all_options():
    """Test tree printing with all options enabled."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    block.add_dimension("n", 10)
    block.add_variable("var1", "float", (), 1.0)
    block.add_attribute("attr1", "value1")

    child = pysmspp.Block()
    child.block_type = "ChildBlock"
    child.add_dimension("m", 5)

    block.blocks["Child"] = child

    output = capture_print_output(
        pysmspp.print_block_tree,
        block,
        "MyBlock",
        show_dimensions=True,
        show_variables=True,
        show_attributes=True,
    )

    # Parent block
    assert "MyBlock [TestBlock]" in output
    assert "Dimensions:" in output
    assert "n=10" in output
    assert "Variables:" in output
    assert "var1" in output
    assert "Attributes:" in output
    assert "attr1=value1" in output

    # Child block
    assert "Child [ChildBlock]" in output
    assert "m=5" in output


def test_print_block_tree_sample_network():
    """Test tree printing with a real sample network."""
    fp = get_network()
    net = pysmspp.SMSNetwork(fp)

    output = capture_print_output(pysmspp.print_block_tree, net, "TestNetwork")

    # Check that the network structure is printed
    assert "TestNetwork" in output
    assert "Block_0" in output
    assert "UnitBlock" in output


def test_print_block_tree_ucblock():
    """Test tree printing with a UCBlock structure."""
    b = pysmspp.Block()
    add_base_ucblock(b, n_nodes=2, n_lines=1, n_units=2, n_elec_generators=2)

    # Add thermal and battery unit blocks
    tb = build_base_tub()
    b.blocks["Block_0"].add("ThermalUnitBlock", "UnitBlock_0", block=tb)

    bub = build_base_bub()
    b.blocks["Block_0"].add("BatteryUnitBlock", "UnitBlock_1", block=bub)

    output = capture_print_output(
        pysmspp.print_block_tree, b, "UCNetwork", show_dimensions=True
    )

    # Check structure
    assert "UCNetwork" in output
    assert "Block_0 [UCBlock]" in output
    assert "UnitBlock_0 [ThermalUnitBlock]" in output
    assert "UnitBlock_1 [BatteryUnitBlock]" in output

    # Check dimensions
    assert "Dimensions:" in output
    assert "NumberUnits=2" in output


def test_print_block_tree_many_variables():
    """Test that many variables are truncated properly."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"

    # Add more than 5 variables
    for i in range(10):
        block.add_variable(f"var{i}", "float", (), float(i))

    output = capture_print_output(
        pysmspp.print_block_tree, block, "MyBlock", show_variables=True
    )

    assert "Variables:" in output
    assert "var0" in output
    assert "10 total" in output
    assert "..." in output


def test_print_block_tree_many_attributes():
    """Test that many attributes are truncated properly."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"

    # Add more than 5 attributes
    for i in range(10):
        block.add_attribute(f"attr{i}", i)

    output = capture_print_output(
        pysmspp.print_block_tree, block, "MyBlock", show_attributes=True
    )

    assert "Attributes:" in output
    assert "attr0" in output
    assert "10 total" in output
    assert "..." in output


def test_print_block_tree_empty_block():
    """Test tree printing with an empty block."""
    block = pysmspp.Block()

    output = capture_print_output(pysmspp.print_block_tree, block, "EmptyBlock")

    assert "EmptyBlock" in output
    assert "[Unknown]" in output  # No type set


def test_print_block_tree_deeply_nested():
    """Test tree printing with deeply nested blocks."""
    root = pysmspp.Block()
    root.block_type = "Level0"

    level1 = pysmspp.Block()
    level1.block_type = "Level1"

    level2 = pysmspp.Block()
    level2.block_type = "Level2"

    level3 = pysmspp.Block()
    level3.block_type = "Level3"

    level2.blocks["L3"] = level3
    level1.blocks["L2"] = level2
    root.blocks["L1"] = level1

    output = capture_print_output(pysmspp.print_block_tree, root, "Root")

    # Check all levels are present
    assert "Root [Level0]" in output
    assert "L1 [Level1]" in output
    assert "L2 [Level2]" in output
    assert "L3 [Level3]" in output

    # Check proper nesting (indentation)
    lines = output.split("\n")
    # Level 3 should have more indentation than level 2
    assert any("L3" in line and "    " in line for line in lines)
