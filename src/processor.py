from grobid.client import GrobidClient
import xml.etree.ElementTree as ET
import os
from ontology_classes import Paper


class PaperProcessor:

    def __init__(self, output_path, grobid_port=8070):
        self.output_path = output_path
        self.grobid = GrobidClient(host="localhost", port=grobid_port)

    def write(self, paper, content):
        with open(self.output_path + paper, "w") as f:
            f.write(content)

    def parse(self, paper):
        return ET.parse(self.output_path + paper)

    def process(self, paper):
        abs_paper = os.path.abspath(paper)
        resp = self.grobid.serve("processFulltextDocument", abs_paper, consolidate_header=True,
                                 consolidate_citations=True)
        if resp[1] != 200:
            print(f"Error processing file {paper}!")
            return "Error", None
        else:
            input_path = "/".join(paper.split("/")[:-1])
            paper_name = paper.split("/")[-1]
            input_path = "./" if input_path == paper_name else input_path
            paper_name = paper_name.replace(".pdf", ".xml")
            self.write(paper_name, resp[0].text)
            return self.process_from_xml(paper_name, input_path=input_path)

    def process_from_xml(self, paper_name, input_path=None):
        res = self.parse(paper_name)
        return Paper(tree=res, filename=paper_name, pdf_path=input_path, xml_path=self.output_path)
    def process_folder(self, folder):
        papers = []
        if not self.grobid.test_alive():
            print("INITIALIZE GROBID FIRST")
        for paper in os.listdir(folder):
            if paper.endswith(".pdf"):
                paper_obj = self.process(folder + paper)
                papers.append(paper_obj)
        return papers

    def process_folder_from_xml(self, pdf_path=None):
        papers = []
        for paper in os.listdir(self.output_path):
            if paper.endswith(".xml"):
                paper_obj = self.process_from_xml(paper, input_path=pdf_path)
                papers.append(paper_obj)
        return papers
