from lxml import etree

dblp_record_types_for_publications = ('article', 'inproceedings', 'proceedings', 'book', 'incollection',
    'phdthesis', 'masterthesis', 'www')

dtd = etree.DTD("../../data/test.dtd")
context = iter(etree.iterparse("../../data/test.xml", events=('start', 'end'), load_dtd=True))

event, root = next(context)
print(root)

n_records_parsed = 0
for event, elem in context:
    if event == 'end' and elem.tag in dblp_record_types_for_publications:
        pub_year = None
        for year in elem.findall('year'):
            pub_year = year.text
        if pub_year is None:
            continue

        pub_title = None
        for title in elem.findall('title'):
            pub_title = title.text
        if pub_title is None:
            continue

        pub_authors = []
        for author in elem.findall('author'):
            if author.text is not None:
                pub_authors.append(author.text)

        # print(pub_year)
        # print(pub_title)
        # print(pub_authors)
        # insert the publication, authors in sql tables
        pub_title_sql_str = pub_title.replace("'", "''")
        pub_author_sql_strs = []
        for author in pub_authors:
            pub_author_sql_strs.append(author.replace("'", "''"))
        print(elem.tag)
        elem.clear()
        root.clear()

        n_records_parsed += 1

print("No. of records parsed: {}".format(n_records_parsed))