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