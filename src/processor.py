from grobid.client import GrobidClient
import xml.etree.ElementTree as ET
import os
from src.paper import Paper


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
        resp = self.grobid.serve("processFulltextDocument", paper, consolidate_header=True,
                                 consolidate_citations=True)
        if resp[1] != 200:
            print(f"Error processing file {paper}!")
            return "Error", None
        else:
            input_path = "/".join(paper.split("/")[:-1])
            paper_name = paper.split("/")[-1]
            input_path = "./" if input_path == paper_name else input_path
            paper = paper.replace(".pdf", ".xml")
            self.write(paper, resp[0])
            res = self.parse(paper)
        return Paper(res, paper.replace(".xml", ""), pdf_path=input_path, xml_path=self.output_path)

    def process_folder(self, folder):
        papers = []
        for paper in os.listdir(folder):
            if paper.endswith(".pdf"):
                paper_obj = self.process(folder + paper)
                papers.append(paper_obj)
        return papers
