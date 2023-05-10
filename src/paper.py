import xml.etree.ElementTree as ET


class Paper:

    def __init__(self, tree, filename, pdf_path=None, xml_path=None, mode="xml"):

        self.input_path = pdf_path
        self.output_path = xml_path
        self.filename = filename
        self.tree = tree
        if mode == "xml":
            self.schema = self.get_schema()
            self.authors = self.get_authors()
            self.abstract = self.get_abstract()
            self.acknowledgements = self.get_acknowledgements()
            self.references = self.get_references()
            self.keywords = None
            self.title = None
        elif mode == "kg": # knowledge graph
            raise NotImplementedError("Knowledge graph mode not implemented yet")
        else:
            raise ValueError("Mode must be either xml or kg")

    def get_schema(self):
        if not self.tree:
            return ""
        res = self.tree.getroot().tag.split("}")
        return res[0] + "}" if len(res) > 0 else ""

    def get_authors(self):
        if not self.tree:
            return []
        try:
            authors = []
            for author in self.tree.findall(
                    f"{self.schema}teiHeader/{self.schema}fileDesc/{self.schema}titleStmt/{self.schema}author"):
                author_dict = {}
                if author.find(f"{self.schema}persName") is not None:
                    author_dict["name"] = author.find(f"{self.schema}persName").text
                if author.find(f"{self.schema}email") is not None:
                    author_dict["email"] = author.find(f"{self.schema}email").text
                if author.find(f"{self.schema}affiliation") is not None:
                    author_dict["affiliation"] = author.find(f"{self.schema}affiliation").text
                authors.append(author_dict)
            return authors
        except:
            return ""

    def get_abstract(self):
        '''
        This function gets the abstract of a given paper.
        :param papers: a dictionary of papers
        :param elem: the name of the XML file containing the paper
        :param schema: the schema string
        :return: the abstract string
        '''
        if not self.tree:
            return ""
        try:
            if self.tree.find(f"{self.schema}teiHeader") is not None:
                if self.tree.find(f"{self.schema}teiHeader").find(f"{self.schema}profileDesc") is not None:
                    if self.tree.find(f"{self.schema}teiHeader").find(f"{self.schema}profileDesc").find(
                            f"{self.schema}abstract") is not None:
                        return ET.tostring(
                            self.tree.find(f"{self.schema}teiHeader").find(f"{self.schema}profileDesc").find(
                                f"{self.schema}abstract"),
                            encoding='utf-8', method='text').strip().decode("utf-8")
            return ""
        except:
            return ""

    def get_acknowledgements(self):
        try:
            return list(map(lambda x: [y.text for y in x], map(lambda x: [y for y in x.iter()], filter(
                lambda elem: "acknowledgement" in list(elem.attrib.values()), [elem for elem in
                                                                               self.tree.find(
                                                                                   f"{self.schema}text").find(
                                                                                   f"{self.schema}back").findall(
                                                                                   rf"{self.schema}div")]))))[-1][-1]
        except:
            return ""

    def _get_name_parts(self, authors):
        ret_authors = []
        for author in authors:
            ret_author = []
            for name_part in author.iter():
                if name_part.text is not None:
                    ret_author.append(name_part.text)
            ret_authors.append(" ".join(ret_author[1:]).strip().replace("  ", " "))
        return ret_authors

    def get_references(self):
        refs = []
        if not self.tree:
            return refs
        for ref in self.tree.findall(
                f"{self.schema}text/{self.schema}back/{self.schema}div/{self.schema}listBibl/{self.schema}biblStruct"):
            ref_dict = {}
            if ref.find(f"{self.schema}analytic") is not None:
                if ref.find(f"{self.schema}analytic/{self.schema}title") is not None:
                    ref_dict["title"] = ref.find(f"{self.schema}analytic/{self.schema}title").text
                if ref.find(f"{self.schema}analytic/{self.schema}author") is not None:
                    aux_authors = [author for author in ref.findall(f"{self.schema}analytic/{self.schema}author")]
                    authors = self._get_name_parts(aux_authors)
                    ref_dict["authors"] = authors
            if ref.find(f"{self.schema}monogr") is not None:
                if ref.find(f"{self.schema}monogr/{self.schema}title") is not None:
                    ref_dict["journal"] = ref.find(f"{self.schema}monogr/{self.schema}title").text
                if ref.find(f"{self.schema}monogr/{self.schema}imprint") is not None:
                    if ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date") is not None:
                        ref_dict["date"] = ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date").text
            refs.append(ref_dict)
        return refs
