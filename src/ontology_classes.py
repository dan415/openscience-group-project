import re
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from pyalex import Authors
from wikidataintegrator import wdi_core, wdi_login
from wikidataintegrator.wdi_helpers import try_write


class Paper:

    def __init__(self, tree=None, filename=None, pdf_path=None, xml_path=None, physical=True, authors=None, title=None,
                 journal=None, cited_by=None):

        self.input_path = pdf_path
        self.output_path = xml_path
        self.filename = filename
        self.tree = tree
        self.physical = physical
        self.cluster = None
        self.topic = None
        self.acknowledgements = None
        self.references = []
        self.journal = None
        self.cited_by = []
        self.keywords = []
        self.title = None
        self.abstract = None
        self.authors = []
        self.journal = None
        self.schema = None
        if self.physical:
            self.schema = self.get_schema()
            self.authors = self.get_authors()
            self.abstract = self.get_abstract()
            self.acknowledgements = self.get_acknowledgements()
            self.references = self.get_references()
            self.keywords = self.get_keywords()
            self.title = self.get_title()
            self.title = self.title.lower() if self.title else "unknown"
        else:
            self.authors = authors
            self.title = title.lower() if title else "unknown"
            self.journal = Journal(name=journal, publishes=[self]) if journal else None
            self.cited_by = [cited_by]

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

    def get_author(self, author, add_as_writer=False):
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
        if add_as_writer:
            author_dict["writes"] = [self]
        return Author(**author_dict)

    def get_authors(self):
        if not self.tree:
            return []
        try:
            authors = []
            for author in self.tree.findall(
                    f"{self.schema}teiHeader/{self.schema}fileDesc/{self.schema}sourceDesc//{self.schema}biblStruct/{self.schema}analytic/{self.schema}author"):
                authors.append(self.get_author(author, add_as_writer=True))
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
            return Aknowledgement(
                text=list(map(lambda x: [y.text for y in x], map(lambda x: [y for y in x.iter()], filter(
                    lambda elem: "acknowledgement" in list(elem.attrib.values()), [elem for elem in
                                                                                   self.tree.find(
                                                                                       f"{self.schema}text").find(
                                                                                       f"{self.schema}back").findall(
                                                                                       rf"{self.schema}div")]))))[-1][
                    -1], source=self)
        except:
            return Aknowledgement(text="", source=self)

    def get_references(self):
        refs = []
        if not self.tree:
            return refs
        for ref in self.tree.findall(
                f"{self.schema}text/{self.schema}back/{self.schema}div/{self.schema}listBibl/{self.schema}biblStruct"):
            ref_dict = {}
            ref_dict["source"] = self
            if ref.find(f"{self.schema}analytic") is not None:
                if ref.find(f"{self.schema}analytic/{self.schema}title") is not None:
                    ref_dict["title"] = ref.find(f"{self.schema}analytic/{self.schema}title").text
                if ref.find(f"{self.schema}analytic/{self.schema}author") is not None:
                    aux_authors = [author for author in ref.findall(f"{self.schema}analytic/{self.schema}author")]
                    authors_class = []
                    for author in aux_authors:
                        authors_class.append(self.get_author(author, add_as_writer=False))
                    ref_dict["authors"] = authors_class

            if ref.find(f"{self.schema}monogr") is not None:
                if ref.find(f"{self.schema}monogr/{self.schema}title") is not None:
                    if "title" in ref_dict.keys():
                        ref_dict["journal"] = ref.find(f"{self.schema}monogr/{self.schema}title").text
                    else:
                        ref_dict["title"] = ref.find(f"{self.schema}monogr/{self.schema}title").text
                if ref.find(f"{self.schema}monogr/{self.schema}imprint") is not None:
                    if ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date") is not None:
                        ref_dict["date"] = ref.find(f"{self.schema}monogr/{self.schema}imprint/{self.schema}date").text

                if "authors" not in ref_dict.keys():
                    aux_authors = [author for author in ref.findall(f"{self.schema}monogr/{self.schema}author")]
                    authors_class = []
                    for author in aux_authors:
                        authors_class.append(self.get_author(author, add_as_writer=False))
                    ref_dict["authors"] = authors_class
            if "title" in ref_dict.keys() and ref_dict["title"] is not None:
                refs.append(ref_dict)
        refs_class = [Citation(**ref_dict) for ref_dict in refs]
        return refs_class


class Citation:

    def __init__(self, date=None, authors=None, title=None, journal=None, source=None):
        self.cites = Paper(authors=authors, title=title, journal=journal, physical=False, cited_by=self)
        self.date = date
        self.source = source


class Author:
    OPENALEX_API_URL = "https://openalex.org/api/v1/authors"

    def __init__(self, forename=None, surname=None, affiliation_name=None, affiliation_country=None,
                 works_count=None, cited_by_count=None, writes=None, acknowledged_by=None, email=None):
        if acknowledged_by is None:
            acknowledged_by = []
        if writes is None:
            writes = []
        self.forename = re.sub(r'[^a-zA-Z]', '', forename) if forename is not None else "unknown"
        self.surname = re.sub(r'[^a-zA-Z]', '', surname) if surname is not None else "unknown"
        self.works_count = works_count
        self.cited_by_count = cited_by_count
        self.writes = writes
        self.email = email
        self.affiliation = Affiliation(affiliation_name, affiliation_country)
        self.ackowledged_by = acknowledged_by

    def enrich(self):
        if self.forename != "unknown" and self.surname != "unknown":
            info = self.get_openalex_info(f"{self.forename} {self.surname}")
            if info:
                self.works_count = info.get("works_count", self.works_count)
                self.cited_by_count = info.get("cited_by_count", self.cited_by_count)

    def get_openalex_info(self, author):
        res = Authors().search_filter(display_name=author).get()
        if res and len(res) > 0:
            res = res[0]
            return {"works_count": res.get("works_count", self.works_count),
                    "cited_by_count": res.get("cited_by_count", self.cited_by_count)}

        return None

    def __eq__(self, other):
        return self.forename == other.forename and self.surname == other.surname

    def __hash__(self):
        return hash((self.forename, self.surname))


class Affiliation:

    def __init__(self, name=None, country=None, established=None, website=None, ackowledged_by=None):
        if ackowledged_by is None:
            ackowledged_by = []
        self.name = name if name is not None else "unknown"
        self.country = country
        self.website = website
        self.established = established
        self.acknowledged_by = ackowledged_by

    def enrich(self):
        if self.name and self.name != "unknown":
            wd_item_id = self.get_wikidata_item_id(self.name)
            if wd_item_id:
                affiliation_info = self.get_wikidata_info(wd_item_id)
                self.website = affiliation_info.get("website")
                established = affiliation_info.get("established")
                if established:
                    try:
                        self.established = datetime.fromisoformat(established)
                    except:
                        self.established = established

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def get_wikidata_item_id(name):
        name = re.sub(r'[^a-zA-Z0-9]\s', '', name)
        query = f'SELECT ?item WHERE {{ ?item rdfs:label "{name}"@en }}'
        results = wdi_core.WDItemEngine.execute_sparql_query(query, max_retries=3, retry_after=5)
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["item"]["value"].split("/")[-1]
        else:
            return None

    @staticmethod
    def get_wikidata_info(wd_item_id):
        query = f'SELECT ?website ?established WHERE {{ wd:{wd_item_id} wdt:P856 ?website . OPTIONAL {{ wd:{wd_item_id} wdt:P571 ?established }} }}'
        results = wdi_core.WDItemEngine.execute_sparql_query(query, max_retries=3)
        try:
            website = results["results"]["bindings"][0]["website"]["value"] if results["results"]["bindings"][0][
                "website"] else None
        except:
            website = None
        try:
            established = results["results"]["bindings"][0]["established"]["value"] if results["results"]["bindings"][
                0].get("established") else None
        except:
            established = None
        return {"website": website, "established": established}


from wikidataintegrator import wdi_core, wdi_login
from wikidataintegrator.wdi_helpers import try_write


class Journal:

    def __init__(self, name=None, country=None, established=None, description=None, publishes=None):
        if publishes is None:
            publishes = []
        self.name = name if name is not None else "unknown"
        self.country = country
        self.description = description
        self.established = established
        self.publishes = publishes

    def enrich(self):
        if self.name and self.name != "unknown":
            wd_item_id = self.get_wikidata_item_id(self.name)
            if wd_item_id:
                journal_info = self.get_wikidata_info(wd_item_id)
                self.country = journal_info.get("country_of_origin")
                self.description = journal_info.get("description")
                established = journal_info.get("established")
                if established:
                    try:
                        self.established = datetime.fromisoformat(established)
                    except:
                        self.established = established

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def get_wikidata_item_id(name):
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        query = f'SELECT ?item WHERE {{ ?item rdfs:label "{name}"@en }}'
        results = wdi_core.WDItemEngine.execute_sparql_query(query, max_retries=3)
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["item"]["value"].split("/")[-1]
        else:
            return None

    @staticmethod
    def get_wikidata_info(wd_item_id):
        query = f'SELECT ?description ?established ?country_of_origin WHERE {{ wd:{wd_item_id} wdt:P31 wd:Q5633421 . OPTIONAL {{ wd:{wd_item_id} wdt:P17 ?country . ?country rdfs:label ?country_of_origin filter(lang(?country_of_origin) = "en") }} . OPTIONAL {{ wd:{wd_item_id} schema:description ?description filter(lang(?description) = "en") }} . OPTIONAL {{ wd:{wd_item_id} wdt:P571 ?established }} }}'
        results = wdi_core.WDItemEngine.execute_sparql_query(query, max_retries=3)
        try:
            country_of_origin = results["results"]["bindings"][0]["country_of_origin"]["value"] if \
                results["results"]["bindings"][0]["country_of_origin"] else None
        except:
            country_of_origin = None
        try:
            description = results["results"]["bindings"][0]["description"]["value"] if results["results"]["bindings"][
                0].get("description") else None
        except:
            description = None
        try:
            established = results["results"]["bindings"][0]["established"]["value"] if results["results"]["bindings"][
                0].get("established") else None
        except:
            established = None
        return {"country_of_origin": country_of_origin, "description": description, "established": established}


class Aknowledgement:

    def __init__(self, text=None, source=None):
        self.text = text
        self.source = source
        self.acknowledges_org = []
        self.acknowledges_people = []
