import os

import pytest

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


def _named_files(path):
    """The files a template names, i.e., the .txt words out of its comments."""
    names = set()
    with open(path) as f:
        for line in f:
            for word in line.split("#")[0].split():
                if word.endswith(".txt"):
                    names.add(word.lstrip("*"))
    return names


@pytest.mark.parametrize(
    "template",
    [
        "TSSBlock/TSSBSCfg-IP.txt",
        "TSSBlock/TSSBSCfg-LD-IP.txt",
        "TSSBlock/TSSBSCfg-LDLD.txt",
        "TSSBlock/TSSBSCfg-LDrec.txt",
        "TSSBlock/TSSBSCfg-BDS.txt",
        "TSSBlock/TSSBSCfg-PPH.txt",
        "TSSBlock/InnerBCfg.txt",
        "TSSBlock/TSSBSCfg-IB.txt",
        "TSSBlock/InnerBCfg-LD.txt",
        "InvestmentBlock/BSPar.txt",
        "InvestmentBlock/BSPar-int.txt",
        "InvestmentBlock/InnerBCfg.txt",
    ],
)
def test_template_names_files_of_its_folder(template):
    c = SMSConfig(template=template)
    folder = os.path.dirname(c.config)
    to_check = [os.path.basename(c.config)]
    seen = set()
    while to_check:
        name = to_check.pop()
        if name in seen:
            continue
        seen.add(name)
        path = os.path.join(folder, name)
        assert os.path.isfile(path), f"{template} names {name}, which is missing"
        to_check.extend(_named_files(path))


def _map_entries(path):
    """The classname -> file entries of a map template."""
    entries = {}
    with open(path) as f:
        for line in f:
            words = line.split("#")[0].split()
            if len(words) == 2 and words[1].startswith("*"):
                entries[words[0]] = words[1].lstrip("*")
    return entries


@pytest.mark.parametrize(
    "template", ["TSSBlock/InnerBCfg.txt", "TSSBlock/InnerBCfg-LD.txt"]
)
def test_inner_block_config_of_the_split_components(template):
    # an InvestmentBlock splits a TwoStageStochasticBlock or a
    # MultiStageStochasticBlock inner Block into AbstractBlock components,
    # one per scenario, which need the same configuration as the
    # InvestmentBlock, else its InvestmentFunction has no Solver
    entries = _map_entries(SMSConfig(template=template).config)
    assert entries.get("AbstractBlock") == entries["InvestmentBlock"]
