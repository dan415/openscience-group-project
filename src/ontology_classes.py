import xml.etree.ElementTree as ET



class Paper:

    def __init__(self, tree=None, filename=None, pdf_path=None, xml_path=None, mode="xml", authors=None, title=None, journal=None):

        self.input_path = pdf_path
        self.output_path = xml_path
        self.filename = filename
        self.tree = tree
        if mode == "xml":
            self.schema = self.get_schema()
            self.authors = self.get_authors() #  falla
            self.abstract = self.get_abstract()
            self.acknowledgements = self.get_acknowledgements()
            self.references = self.get_references()
            self.keywords = self.get_keywords()
            self.title = self.get_title()
        elif mode == "kg":  # knowledge graph
            raise NotImplementedError("Knowledge graph mode not implemented yet")
        elif mode == "citation":
            self.authors = authors
            self.title = title
            self.journal = journal
        else:
            raise ValueError("Mode must be either xml or kg")

    def get_schema(self):
        if not self.tree:
            return ""
        res = self.tree.getroot().tag.split("}")
        return res[0] + "}" if len(res) > 0 else ""


    def get_institution(self):
        if not self.tree:
            return ""
        try:
            return self.tree.find(
                f"{self.schema}teiHeader/{self.schema}fileDesc/{self.schema}titleStmt/{self.schema}affiliation").text
        except:
            return ""

    def get_keywords(self):
        if not self.tree:
            return []
        try:
            keywords = []
            for keyword in self.tree.findall(
                    f"{self.schema}teiHeader/{self.schema}profileDesc/{self.schema}textClass/{self.schema}keywords/{self.schema}term"):
                keywords.append(keyword.text)
            return keywords
        except:
            return []

    def get_title(self):
        if not self.tree:
            return ""
        try:
            return self.tree.find(
                f"{self.schema}teiHeader/{self.schema}fileDesc/{self.schema}titleStmt/{self.schema}title").text
        except:
            return ""


    def get_author(self, author):
        author_dict = {}
        if author.find(f"{self.schema}persName") is not None:
            if author.find(f"{self.schema}persName").find(f"{self.schema}forename") is not None:
                author_dict["forename"] = author.find(f"{self.schema}persName").find(
                    f"{self.schema}forename").text
            if author.find(f"{self.schema}persName").find(f"{self.schema}surname") is not None:
                author_dict["surname"] = author.find(f"{self.schema}persName").find(
                    f"{self.schema}surname").text
        if author.find(f"{self.schema}email") is not None:
            author_dict["email"] = author.find(f"{self.schema}email").text
        if author.find(f"{self.schema}affiliation") is not None:
            if author.find(f"{self.schema}affiliation").find(f"{self.schema}orgName") is not None:
                author_dict["affiliation_name"] = author.find(f"{self.schema}affiliation").find(
                    f"{self.schema}orgName").text
            if author.find(f"{self.schema}affiliation").find(f'{self.schema}address') is not None:
                if author.find(f"{self.schema}affiliation").find(f'{self.schema}address').find(
                        f"{self.schema}country") is not None:
                    author_dict["affiliation_country"] = author.find(f"{self.schema}affiliation") \
                        .find(f'{self.schema}address').find(f"{self.schema}country").text
        return Author(**author_dict)
    def get_authors(self):
        if not self.tree:
            return []
        try:
            authors = []
            for author in self.tree.findall(
                    f"{self.schema}teiHeader/{self.schema}fileDesc/{self.schema}sourceDesc//{self.schema}biblStruct/{self.schema}analytic/{self.schema}author"):
                authors.append(self.get_author(author))
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
            return Aknowledgement(text=list(map(lambda x: [y.text for y in x], map(lambda x: [y for y in x.iter()], filter(
                lambda elem: "acknowledgement" in list(elem.attrib.values()), [elem for elem in
                                                                               self.tree.find(
                                                                                   f"{self.schema}text").find(
                                                                                   f"{self.schema}back").findall(
                                                                                   rf"{self.schema}div")]))))[-1][-1])
        except:
            return Aknowledgement(text="")

    def get_references(self):
        refs = []
        refs_class = []
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
                    authors_class = []
                    for author in aux_authors:
                        authors_class.append(self.get_author(author))
                    ref_dict["authors"] = authors_class

            if ref.find(f"{self.schema}monogr") is not None:
                if ref.find(f"{self.schema}monogr/{self.schema}title") is not None:
                    ref_dict["journal"] = ref.find(f"{self.schema}monogr/{self.schema}title").text
                if ref.find(f"{self.schema}monogr/{self.schema}imprint") is not None:
                    if ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date") is not None:
                        ref_dict["date"] = ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date").text
            refs.append(ref_dict)
            refs_class = [Citation(**ref_dict) for ref_dict in refs]
        return refs_class


class Citation:

    def __init__(self, date=None, authors=None, title=None, journal=None):
        self.cites = Paper(authors=authors, title=title, journal=journal, mode="citation")
        self.date = date


class Author:

    def __init__(self, forename=None, surname=None, email=None, affiliation_name=None, affiliation_country=None, twitter=None, orcid=None):
        self.forename = forename
        self.surname = surname
        self.email = email
        self.twitter = twitter
        self.orcid = orcid
        self.affiliation = Affiliation(affiliation_name, affiliation_country)




class Affiliation:

    def __init__(self, name=None, country=None, established=None, website=None):
        self.name = name
        self.country = country
        self.website = website
        self.established = established


class Aknowledgement:

    def __init__(self, text=None):
        self.text = text
