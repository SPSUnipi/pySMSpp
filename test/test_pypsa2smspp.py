"""Tests for pypsa2smspp package integration."""


def test_pypsa2smspp_import():
    """Test that pypsa2smspp can be imported."""
    import pypsa2smspp

    assert hasattr(pypsa2smspp, "Transformation")
    assert hasattr(pypsa2smspp, "TransformationConfig")


def test_pypsa2smspp_basic_functionality():
    """Test basic pypsa2smspp functionality with a simple network."""
    import pypsa
    import pypsa2smspp

    # Create a simple PyPSA network
    n = pypsa.Network()
    n.add("Bus", "bus0")
    n.add("Generator", "gen0", bus="bus0", p_nom=100, marginal_cost=50)
    n.add("Load", "load0", bus="bus0", p_set=80)

    # Verify the network was created
    assert len(n.buses) == 1
    assert len(n.generators) == 1
    assert len(n.loads) == 1

    # Test that we can instantiate TransformationConfig
    config = pypsa2smspp.TransformationConfig()
    assert config is not None


def test_pypsa2smspp_config_loading():
    """Test that pypsa2smspp can load its default configuration."""
    import pypsa2smspp
    import yaml
    import os

    # Find the config file
    pypsa2smspp_path = pypsa2smspp.__file__
    config_path = os.path.join(
        os.path.dirname(pypsa2smspp_path), "data", "config_default.yaml"
    )

    assert os.path.exists(config_path), f"Config file not found at {config_path}"

    # Load and verify config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    assert config is not None
    assert isinstance(config, dict)
