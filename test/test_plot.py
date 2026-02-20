"""Tests for Variable.plot() and Block.plot() plotting features."""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(__file__))

import pysmspp
from pysmspp import Block, Variable

pytest.importorskip("matplotlib")
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
    """Test that a 1-D variable produces a line plot."""
    data = np.linspace(0, 10, 24)
    var = Variable("ActivePower", "float", ("TimeHorizon",), data)
    ax = var.plot()
    assert ax is not None
    assert len(ax.lines) == 1
    assert ax.get_title() == "ActivePower"
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "ActivePower"
    plt.close("all")


def test_variable_plot_2d():
    """Test that a 2-D variable produces an image (heatmap) by default."""
    data = np.full((3, 24), 50.0)
    var = Variable(
        "ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), data
    )
    ax = var.plot()
    assert ax is not None
    assert ax.get_title() == "ActivePowerDemand"
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "NumberNodes"
    plt.close("all")


def test_variable_plot_2d_kind_heatmap():
    """Test explicit kind='heatmap' for a 2-D variable."""
    data = np.full((3, 24), 50.0)
    var = Variable(
        "ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), data
    )
    ax = var.plot(kind="heatmap")
    assert ax.get_title() == "ActivePowerDemand"
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "NumberNodes"
    plt.close("all")


def test_variable_plot_2d_kind_line():
    """Test kind='line' for a 2-D variable produces a line plot with legend."""
    data = np.random.rand(3, 24)
    var = Variable(
        "ActivePowerDemand", "float", ("NumberNodes", "TimeHorizon"), data
    )
    ax = var.plot(kind="line")
    # One line per row
    assert len(ax.lines) == 3
    assert ax.get_xlabel() == "TimeHorizon"
    assert ax.get_ylabel() == "ActivePowerDemand"
    assert ax.get_legend() is not None
    plt.close("all")


def test_variable_plot_2d_kind_invalid():
    """Test that an unsupported kind raises ValueError."""
    data = np.full((2, 5), 1.0)
    var = Variable("V", "float", ("a", "b"), data)
    with pytest.raises(ValueError, match="Unsupported kind"):
        var.plot(kind="pie")
    plt.close("all")


def test_variable_plot_uses_provided_axes():
    """Test that plot() draws on the provided axes."""
    _, ax_provided = plt.subplots()
    data = np.arange(10, dtype=float)
    var = Variable("TestVar", "float", ("n",), data)
    ax_returned = var.plot(ax=ax_provided)
    assert ax_returned is ax_provided
    plt.close("all")


def test_variable_plot_raises_for_3d():
    """Test that a 3-D variable raises ValueError."""
    data = np.zeros((2, 3, 4))
    var = Variable("BadVar", "float", ("a", "b", "c"), data)
    with pytest.raises(ValueError, match="3"):
        var.plot()
    plt.close("all")


def test_variable_plot_kwargs_forwarded():
    """Test that extra kwargs are forwarded to the plot function."""
    data = np.arange(5, dtype=float)
    var = Variable("Var1D", "float", ("n",), data)
    ax = var.plot(linewidth=3)
    line = ax.lines[0]
    assert line.get_linewidth() == 3.0
    plt.close("all")


# ---------------------------------------------------------------------------
# Block.plot() tests
# ---------------------------------------------------------------------------


def test_block_plot_returns_figure():
    """Test that Block.plot() returns a matplotlib Figure."""
    block = Block()
    block.add_variable(
        "ActivePower", "float", ("TimeHorizon",), np.linspace(0, 100, 24)
    )
    fig = block.plot()
    assert isinstance(fig, plt.Figure)
    plt.close("all")


def test_block_plot_creates_one_subplot_per_variable():
    """Test that one subplot is created for each variable."""
    block = Block()
    block.add_variable("P1", "float", ("T",), np.arange(10, dtype=float))
    block.add_variable("P2", "float", ("T",), np.arange(10, dtype=float) * 2)
    fig = block.plot()
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


def test_block_plot_skips_scalars_by_default():
    """Scalar variables are excluded when variables=None."""
    block = Block()
    block.add_variable("Scalar", "float", (), 42.0)
    block.add_variable("Array", "float", ("T",), np.arange(5, dtype=float))
    fig = block.plot()
    assert len(fig.axes) == 1
    plt.close("all")


def test_block_plot_includes_scalar_when_explicit():
    """Scalar variables are included when explicitly listed."""
    block = Block()
    block.add_variable("Scalar", "float", (), 42.0)
    block.add_variable("Array", "float", ("T",), np.arange(5, dtype=float))
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


def test_block_plot_2d_variable():
    """Test that Block.plot() handles 2-D variables."""
    block = Block()
    block.add_variable(
        "Demand",
        "float",
        ("NumberNodes", "TimeHorizon"),
        np.full((3, 24), 50.0),
    )
    fig = block.plot()
    assert len(fig.axes) >= 1
    plt.close("all")


def test_block_plot_kwargs_forwarded_to_variable():
    """Test that kwargs passed to Block.plot() are forwarded to Variable.plot()."""
    block = Block()
    block.add_variable(
        "Demand",
        "float",
        ("NumberNodes", "TimeHorizon"),
        np.random.rand(3, 24),
    )
    # kind="line" should produce lines, not an image
    fig = block.plot(kind="line")
    ax = fig.axes[0]
    assert len(ax.lines) == 3
    plt.close("all")
