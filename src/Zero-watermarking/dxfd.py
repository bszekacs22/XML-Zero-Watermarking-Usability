import lxml.etree as ET








parser = ET.XMLParser(load_dtd=True, dtd_validation=True)
tree = ET.parse('../../data/test.xml', parser)
root = tree.getroot()
