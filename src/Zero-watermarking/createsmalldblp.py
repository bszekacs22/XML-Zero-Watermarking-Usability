import lxml.etree as ET

def extract_inproceedings(input_file, output_file, max_elements=100000):
    context = ET.iterparse(input_file, events=("start", "end"), load_dtd=True, dtd_validation=True)
    _, root = next(context)  # get the root element

    count = 0
    inproceedings = []

    for event, elem in context:
        if event == "end" and elem.tag == "inproceedings":
            inproceedings.append(ET.tostring(elem, pretty_print=True).decode('utf-8'))
            count += 1
            root.clear()  # clear the element to free memory
            if count >= max_elements:
                break

    root = ET.Element("dblp")
    tree = ET.ElementTree(root)

    for inproc in inproceedings:
        root.append(ET.fromstring(inproc))

    tree.write(output_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')

# Example usage
input_file = "..\..\data\dblp.xml"
output_file = "..\..\data\dblp_smal.xml"
extract_inproceedings(input_file, output_file, max_elements=20000)
