"""Tests for the block tree visualization utility."""

from io import StringIO
import sys
from conftest import get_network, add_base_ucblock, build_base_tub, build_base_bub
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


def test_print_tree_structure_and_nesting():
    """Test tree structure with nested blocks and tree connectors."""
    parent = pysmspp.Block()
    parent.block_type = "ParentBlock"

    child1 = pysmspp.Block()
    child1.block_type = "ChildBlock1"
    child2 = pysmspp.Block()
    child2.block_type = "ChildBlock2"

    parent.blocks["Child1"] = child1
    parent.blocks["Child2"] = child2

    output = capture_print_output(parent.print_tree, "Parent")

    assert "Parent [ParentBlock]" in output
    assert "Child1 [ChildBlock1]" in output
    assert "Child2 [ChildBlock2]" in output
    assert "└── " in output or "├── " in output


def test_print_tree_display_options():
    """Test displaying dimensions, variables, and attributes."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    block.add_dimension("n", 10)
    block.add_variable("var1", "float", (), 1.0)
    block.add_attribute("attr1", "value1")

    # Test with all options
    output = capture_print_output(
        block.print_tree,
        "MyBlock",
        show_dimensions=True,
        show_variables=True,
        show_attributes=True,
    )

    assert "MyBlock [TestBlock]" in output
    assert "Dimensions (1):" in output and "n=10" in output
    assert "Variables (1):" in output and "var1" in output
    assert "Attributes (1):" in output and "attr1=value1" in output


def test_print_tree_truncation():
    """Test that long lists are truncated properly."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"

    # Add more than 5 items
    for i in range(10):
        block.add_variable(f"var{i}", "float", (), float(i))
        block.add_attribute(f"attr{i}", i)

    output = capture_print_output(
        block.print_tree, "MyBlock", show_variables=True, show_attributes=True
    )

    assert "10 total" in output
    assert "..." in output


def test_print_tree_default_naming():
    """Test default name behavior for Block and SMSNetwork."""
    block = pysmspp.Block()
    block.block_type = "TestBlock"
    output = capture_print_output(block.print_tree)
    assert "TestBlock [TestBlock]" in output

    net = pysmspp.SMSNetwork(get_network())
    output = capture_print_output(net.print_tree)

    lines = output.splitlines()
    assert len(lines) > 0 and lines[0] == "SMSNetwork"


def test_print_tree_real_network():
    """Test with real SMS++ network structure."""
    b = pysmspp.Block()
    add_base_ucblock(b, n_nodes=2, n_lines=1, n_units=2, n_elec_generators=2)

    tb = build_base_tub()
    b.blocks["Block_0"].add("ThermalUnitBlock", "UnitBlock_0", block=tb)

    bub = build_base_bub()
    b.blocks["Block_0"].add("BatteryUnitBlock", "UnitBlock_1", block=bub)

    output = capture_print_output(b.print_tree, show_dimensions=True)

    assert "Block_0 [UCBlock]" in output
    assert "UnitBlock_0 [ThermalUnitBlock]" in output
    assert "UnitBlock_1 [BatteryUnitBlock]" in output
    assert "Dimensions (5):" in output
