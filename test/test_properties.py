import smspy


def test_block_type():
    block = smspy.Block()
    block.block_type = "block"
    assert block.block_type == "block"


def test_SMSNetwork_file_type():
    net = smspy.SMSNetwork(file_type=smspy.SMSFileType.eConfigFile)
    assert net.file_type == smspy.SMSFileType.eConfigFile
    net.file_type = smspy.SMSFileType.eConfigFile
    assert net.file_type == smspy.SMSFileType.eConfigFile


def test_static():
    block = smspy.Block()
    block.block_type = "block"

    for c in block.components.keys():
        obj = block.static(c)
        if c == "Attribute":
            assert len(obj) == 1
            assert obj["type"] == "block"
        else:
            assert len(obj) == 0
