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
