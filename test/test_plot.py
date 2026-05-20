"""Tests for Variable.plot() and Block.plot() plotting features."""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from pysmspp import Block, Variable
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")  # Use non-interactive backend for testing


# ---------------------------------------------------------------------------
# Variable.plot() tests
# ---------------------------------------------------------------------------


def test_variable_plot_scalar():
    """Test that a scalar variable produces a bar chart axes."""
    var = Variable("MinPower", "float", (), 5.0)
    ax = var.plot()
    assert ax is not None
    # Bar chart should have one bar
    assert len(ax.patches) == 1
    plt.close("all")


def test_variable_plot_1d():
    """Test that a 1-D variable produces a line plot with correct labels."""
    data = np.linspace(0, 10, 24)
    var = Variable("ActivePower", "float", ("TimeHorizon",), data)
    ax = var.plot()
    assert len(ax.lines) == 1
    assert ax.get_title() == "ActivePower"
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "ActivePower"
    plt.close("all")


def test_variable_plot_2d_heatmap():
    """Test that a 2-D variable defaults to a heatmap; explicit kind='heatmap' behaves identically."""
    data = np.full((3, 24), 50.0)
    var = Variable("ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), data)
    for kind_arg in ({}, {"kind": "heatmap"}):
        ax = var.plot(**kind_arg)
        assert ax.get_title() == "ActivePowerDemand"
        assert ax.get_xlabel() == "TimeHorizon"
        assert ax.get_ylabel() == "NumberNodes"
        plt.close("all")


def test_variable_plot_2d_kind_line():
    """Test kind='line' for a 2-D variable produces a line plot with legend."""
    data = np.random.rand(3, 24)
    var = Variable("ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), data)
    ax = var.plot(kind="line")
    assert len(ax.lines) == 3
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "ActivePowerDemand"
    assert ax.get_legend() is not None
    plt.close("all")


def test_variable_plot_raises_for_invalid_kind_and_3d():
    """Test ValueError for unsupported kind and for >2-D data."""
    data_2d = np.full((2, 5), 1.0)
    var_2d = Variable("V", "float", ("a", "b"), data_2d)
    with pytest.raises(ValueError, match="Unsupported kind"):
        var_2d.plot(kind="pie")

    data_3d = np.zeros((2, 3, 4))
    var_3d = Variable("BadVar", "float", ("a", "b", "c"), data_3d)
    with pytest.raises(ValueError, match="3"):
        var_3d.plot()
    plt.close("all")


def test_variable_plot_uses_provided_axes():
    """Test that plot() draws on the provided axes."""
    _, ax_provided = plt.subplots()
    var = Variable("TestVar", "float", ("n",), np.arange(10, dtype=float))
    ax_returned = var.plot(ax=ax_provided)
    assert ax_returned is ax_provided
    plt.close("all")


def test_variable_plot_kwargs_forwarded():
    """Test that extra kwargs are forwarded to the underlying matplotlib function."""
    var = Variable("Var1D", "float", ("n",), np.arange(5, dtype=float))
    ax = var.plot(linewidth=3)
    assert ax.lines[0].get_linewidth() == 3.0
    plt.close("all")


# ---------------------------------------------------------------------------
# Block.plot() tests
# ---------------------------------------------------------------------------


def test_block_plot_subplots_per_variable():
    """Block.plot() returns a Figure with one subplot per non-scalar variable."""
    block = Block()
    block.add_variable("P1", "float", ("T",), np.arange(10, dtype=float))
    block.add_variable("P2", "float", ("T",), np.arange(10, dtype=float) * 2)
    fig = block.plot()
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2
    plt.close("all")


def test_block_plot_variable_selection():
    """Test that only selected variables are plotted."""
    block = Block()
    block.add_variable("P1", "float", ("T",), np.arange(10, dtype=float))
    block.add_variable("P2", "float", ("T",), np.arange(10, dtype=float) * 2)
    block.add_variable("P3", "float", ("T",), np.arange(10, dtype=float) * 3)
    fig = block.plot(variables=["P1", "P3"])
    assert len(fig.axes) == 2
    plt.close("all")


def test_block_plot_scalar_handling():
    """Scalars are excluded by default but included when explicitly listed."""
    block = Block()
    block.add_variable("Scalar", "float", (), 42.0)
    block.add_variable("Array", "float", ("T",), np.arange(5, dtype=float))

    # Default: scalars skipped
    fig = block.plot()
    assert len(fig.axes) == 1
    plt.close("all")

    # Explicit list: scalars included
    fig = block.plot(variables=["Scalar", "Array"])
    assert len(fig.axes) == 2
    plt.close("all")


def test_block_plot_raises_when_no_plottable_variables():
    """Block.plot() raises ValueError when no plottable variables exist."""
    block = Block()
    block.add_variable("Scalar1", "float", (), 1.0)
    block.add_variable("Scalar2", "float", (), 2.0)
    with pytest.raises(ValueError, match="No plottable variables"):
        block.plot()
    plt.close("all")


def test_block_plot_custom_figsize():
    """Test that custom figsize is respected."""
    block = Block()
    block.add_variable("P1", "float", ("T",), np.arange(6, dtype=float))
    fig = block.plot(figsize=(10, 5))
    assert fig.get_size_inches()[0] == pytest.approx(10.0)
    assert fig.get_size_inches()[1] == pytest.approx(5.0)
    plt.close("all")


def test_block_plot_kwargs_forwarded_to_variable():
    """kwargs passed to Block.plot() are forwarded to Variable.plot()."""
    block = Block()
    block.add_variable(
        "Demand",
        "float",
        ("NumberNodes", "TimeHorizon"),
        np.random.rand(3, 24),
    )
    # kind="line" should produce 3 lines (one per row), not an image
    fig = block.plot(kind="line")
    assert len(fig.axes[0].lines) == 3
    plt.close("all")
