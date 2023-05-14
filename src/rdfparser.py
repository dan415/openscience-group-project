import re

from rdflib.parser import PythonInputSource

from rdflib import Graph, Namespace, URIRef, Literal, RDF

from src.ontology_classes import Paper, Author, Journal, Affiliation, Citation, Aknowledgement


# Create a new RDF graph


class RDFParser:

    def __init__(self, paper_space):
        self.paper_space = paper_space
        self.g = Graph()
        self.schema = Namespace('http://schema.org/')
        self.instances = Namespace('http://instances.com/')
        self.defined_instances = set()
        self.build()

    def build(self):
        for paper in self.paper_space.papers.values():
            self.add_paper(paper)

    def add_paper(self, paper: Paper):
        paper_id = paper.title.replace(' ', '_').lower()
        paper_id = re.sub(r'[^a-zA-Z0-9]', '', paper_id)
        self.defined_instances.add(paper_id)
        namespace = URIRef(self.instances[paper_id])
        self.g.add((namespace, RDF.type, self.schema["paper"]))
        self.g.add((namespace, self.schema["title"], Literal(paper.title)))
        self.g.add((namespace, self.schema["abstract"], Literal(paper.abstract)))
        self.g.add((namespace, self.schema["keywords"], Literal(paper.keywords)))
        self.g.add((namespace, self.schema["cluster"], Literal(paper.cluster)))
        self.g.add((namespace, self.schema["topic"], Literal(paper.topic)))
        self.g.add((namespace, self.schema["physical"], Literal(paper.physical)))

        for author in paper.authors:
            author_id = f"{author.forename.replace(' ', '_').lower()}_{author.surname.replace(' ', '_').lower()}"
            author_id = re.sub(r'[^a-zA-Z0-9]', '', author_id)
            if author_id not in self.defined_instances:
                self.add_author(author)
            self.g.add((namespace, self.schema["author"], URIRef(self.instances[author_id])))

        for citation in paper.references:
            citation_id = f'{paper_id}_{citation.cites.title.replace(" ", "_").lower()}'
            citation_id = re.sub(r'[^a-zA-Z0-9]', '', citation_id)
            if id not in self.defined_instances:
                self.add_citation(citation)
            self.g.add((namespace, self.schema["citation"], URIRef(self.instances[citation_id])))

        ack_id = f'{paper_id}_acknowledgement'
        ack_id = re.sub(r'[^a-zA-Z0-9]', '', ack_id)
        if ack_id not in self.defined_instances:
            if paper.acknowledgements:
                self.add_acknowledgement(paper.acknowledgements)
        self.g.add((namespace, self.schema["acknowledgement"], URIRef(self.instances[ack_id])))

        journal_id = f'{paper.journal.name.replace(" ", "_").lower()}' if paper.journal else "no_journal"
        journal_id = re.sub(r'[^a-zA-Z0-9]', '', journal_id)
        if journal_id not in self.defined_instances:
            if paper.journal:
                self.add_journal(paper.journal)
        self.g.add((namespace, self.schema["journal"], URIRef(self.instances[journal_id])))

        for cited_by in paper.cited_by:
            cited_by_id = f'{cited_by.source.title.replace(" ", "_").lower()}_{cited_by.cites.title.replace(" ", "_").lower()}'
            cited_by_id = re.sub(r'[^a-zA-Z0-9]', '', cited_by_id)
            if cited_by_id not in self.defined_instances:
                self.add_citation(cited_by)
            self.g.add((namespace, self.schema["cited_by"], URIRef(self.instances[cited_by_id])))

    def add_author(self, author: Author):
        author_id = re.sub(r'[^a-zA-Z0-9]', '',
                           f"{author.forename.replace(' ', '_').lower()}_{author.surname.replace(' ', '_').lower()}")
        self.defined_instances.add(author_id)
        namespace = URIRef(self.instances[author_id])
        self.g.add((namespace, RDF.type, self.schema["author"]))
        self.g.add((namespace, self.schema["forename"], Literal(author.forename)))
        self.g.add((namespace, self.schema["surname"], Literal(author.surname)))
        self.g.add((namespace, self.schema["cited_by_count"], Literal(author.cited_by_count)))
        self.g.add((namespace, self.schema["works_count"], Literal(author.works_count)))
        self.g.add((namespace, self.schema["email"], Literal(author.email)))

        affiliation_id = f'{author.affiliation.name.replace(" ", "_").lower()}' if author.affiliation else "no_affiliation"
        affiliation_id = re.sub(r'[^a-zA-Z0-9]', '', affiliation_id)
        if affiliation_id not in self.defined_instances:
            self.add_affiliation(author.affiliation)
        self.g.add((namespace, self.schema["affiliation"], URIRef(self.instances[affiliation_id])))

        for paper in author.writes:
            paper_id = f'{paper.title.replace(" ", "_").lower()}'
            paper_id = re.sub(r'[^a-zA-Z0-9]', '', paper_id)
            if paper_id not in self.defined_instances:
                self.add_paper(paper)
            self.g.add((namespace, self.schema["writes"], URIRef(self.instances[paper_id])))

        for ack in author.ackowledged_by:
            ack_id = f'{ack.source.title.replace(" ", "_").lower()}_acknowledgement'
            ack_id = re.sub(r'[^a-zA-Z0-9]', '', ack_id)
            if ack_id not in self.defined_instances:
                self.add_acknowledgement(ack)
            self.g.add((namespace, self.schema["acknowledged_by"], URIRef(self.instances[ack_id])))

    def add_journal(self, journal: Journal):
        journal_id = f'{journal.name.replace(" ", "_").lower()}' if journal.name else "no_journal"
        journal_id = re.sub(r'[^a-zA-Z0-9]', '', journal_id)
        self.defined_instances.add(journal_id)
        namespace = URIRef(self.instances[journal_id])
        self.g.add((namespace, RDF.type, self.schema["journal"]))
        self.g.add((namespace, self.schema["name"], Literal(journal.name)))
        self.g.add((namespace, self.schema["country"], Literal(journal.country)))
        self.g.add((namespace, self.schema["description"], Literal(journal.description)))
        self.g.add((namespace, self.schema["established"], Literal(journal.established)))

        for paper in journal.publishes:
            paper_id = f'{paper.title.replace(" ", "_").lower()}'
            paper_id = re.sub(r'[^a-zA-Z0-9]', '', paper_id)
            if paper_id not in self.defined_instances:
                self.add_paper(paper)
            self.g.add((namespace, self.schema["publishes"], URIRef(self.instances[paper_id])))

    def add_affiliation(self, affiliation: Affiliation):
        affiliation_id = f'{affiliation.name.replace(" ", "_").lower()}' if affiliation.name else "no_affiliation"
        affiliation_id = re.sub(r'[^a-zA-Z0-9]', '', affiliation_id)
        self.defined_instances.add(affiliation_id)
        namespace = URIRef(self.instances[affiliation_id])
        self.g.add((namespace, RDF.type, self.schema["affiliation"]))
        self.g.add((namespace, self.schema["name"], Literal(affiliation.name)))
        self.g.add((namespace, self.schema["country"], Literal(affiliation.country)))
        self.g.add((namespace, self.schema["website"], Literal(affiliation.website)))
        self.g.add((namespace, self.schema["established"], Literal(affiliation.established)))

        for ack in affiliation.acknowledged_by:
            ack_id = f'{ack.source.title.replace(" ", "_").lower()}_acknowledgement'
            ack_id = re.sub(r'[^a-zA-Z0-9]', '', ack_id)
            if ack_id not in self.defined_instances:
                self.add_acknowledgement(ack)
            self.g.add((namespace, self.schema["acknowledged_by"], URIRef(self.instances[ack_id])))

    def add_citation(self, citation: Citation):
        citation_id = f'{citation.source.title.replace(" ", "_").lower()}_{citation.cites.title.replace(" ", "_").lower()}'
        citation_id = re.sub(r'[^a-zA-Z0-9]', '', citation_id)
        self.defined_instances.add(citation_id)
        namespace = URIRef(self.instances[citation_id])
        self.g.add((namespace, RDF.type, self.schema["citation"]))
        self.g.add((namespace, self.schema["date"], Literal(citation.date)))

        source_id = f'{citation.source.title.replace(" ", "_").lower()}'
        source_id = re.sub(r'[^a-zA-Z0-9]', '', source_id)
        if source_id not in self.defined_instances:
            self.add_paper(citation.source)
        self.g.add((namespace, self.schema["source"], URIRef(self.instances[source_id])))

        cites_id = f'{citation.cites.title.replace(" ", "_").lower()}'
        cites_id = re.sub(r'[^a-zA-Z0-9]', '', cites_id)
        if cites_id not in self.defined_instances:
            self.add_paper(citation.cites)
        self.g.add((namespace, self.schema["cites"], URIRef(self.instances[cites_id])))

    def add_acknowledgement(self, acknowledgement: Aknowledgement):
        ack_id = f'{acknowledgement.source.title.replace(" ", "_").lower()}_acknowledgement'
        ack_id = re.sub(r'[^a-zA-Z0-9]', '', ack_id)
        self.defined_instances.add(ack_id)
        namespace = URIRef(self.instances[ack_id])
        self.g.add((namespace, RDF.type, self.schema["acknowledgement"]))
        self.g.add((namespace, self.schema["text"], Literal(acknowledgement.text)))

        source_id = f'{acknowledgement.source.title.replace(" ", "_").lower()}'
        source_id = re.sub(r'[^a-zA-Z0-9]', '', source_id)
        if source_id not in self.defined_instances:
            self.add_paper(acknowledgement.source)
        self.g.add((namespace, self.schema["source"], URIRef(self.instances[source_id])))

        for author in acknowledgement.acknowledges_people:
            author_id = f"{author.forename.replace(' ', '_').lower()}_{author.surname.replace(' ', '_').lower()}"
            author_id = re.sub(r'[^a-zA-Z0-9]', '', author_id)
            if author_id not in self.defined_instances:
                self.add_author(author)
            self.g.add((namespace, self.schema["acknowledges_people"], URIRef(self.instances[author_id])))

        for affiliation in acknowledgement.acknowledges_org:
            affiliation_id = f'{affiliation.name.replace(" ", "_").lower()}' if affiliation.name else "no_affiliation"
            affiliation_id = re.sub(r'[^a-zA-Z0-9]', '', affiliation_id)
            if affiliation_id not in self.defined_instances:
                self.add_affiliation(affiliation)
            self.g.add((namespace, self.schema["acknowledges_org"], URIRef(self.instances[affiliation_id])))

    def get_paper_by_title(self, title: str):
        paper_id = f'{title.replace(" ", "_").lower()}'
        paper_id = re.sub(r'[^a-zA-Z0-9]', '', paper_id)
        return self.g.value(URIRef(self.instances[paper_id]), self.schema["paper"])
