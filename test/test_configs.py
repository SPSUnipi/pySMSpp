from pysmspp import SMSConfig


def test_get_configs():
    list_configs = SMSConfig.get_templates()

    assert len(list_configs) >= 3

    print(list_configs)


def test_get_ucsolverconfig():
    c = SMSConfig(template="UCBlock/uc_solverconfig")

    assert c.config.endswith("uc_solverconfig.txt")
    assert str(c).endswith("uc_solverconfig.txt")


def test_get_ucsolverconfig_txt():
    c = SMSConfig(template="UCBlock/uc_solverconfig.txt")

    assert c.config.endswith("uc_solverconfig.txt")
    assert str(c).endswith("uc_solverconfig.txt")


def test_ucblock_folder_linearizes_polyhedral_function_block():
    """smspp_ucblock_solver reads InnerBCfg.txt from the -c folder when no -B
    is given, so the UCBlock templates ship one that linearizes the
    PolyhedralFunctionBlock (PFBCfg.txt), and nothing else."""
    import os

    c = SMSConfig(template="UCBlock/uc_solverconfig.txt")
    folder = os.path.dirname(c.config)
    with open(os.path.join(folder, "InnerBCfg.txt")) as f:
        entries = [line.split("#")[0].split() for line in f]
    entries = [e for e in entries if len(e) == 2 and e[1].startswith("*")]
    assert entries == [["PolyhedralFunctionBlock", "*PFBCfg.txt"]]
    assert os.path.isfile(os.path.join(folder, "PFBCfg.txt"))
