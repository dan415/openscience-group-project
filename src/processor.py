from time import sleep

from grobid.client import GrobidClient
import xml.etree.ElementTree as ET
import os
from ontology_classes import Paper


class PaperProcessor:
    """
    This class is responsible for processing and extracting information from scientific papers using the Grobid library.
    """

    def __init__(self, output_path, grobid_port=8070):
        self.output_path = output_path
        self.grobid = GrobidClient(host="localhost", port=grobid_port)

    def write(self, paper, content):
        """
        Writes the processed content of a paper to a file.

        Parameters:
            paper (str): The name of the paper file.
            content (str): The processed content of the paper.
        """
        with open(self.output_path + paper, "w") as f:
            f.write(content)

    def parse(self, paper):
        """
        Parses an XML file and returns the parsed ElementTree object.

        Parameters:
            paper (str): The name of the XML file.

        Returns:
            ElementTree: The parsed XML as an ElementTree object.
        """
        return ET.parse(self.output_path + paper)

    def process(self, paper):
        """
        Processes a PDF paper using the Grobid server.

        Parameters:
            paper (str): The name of the PDF paper file.

        Returns:
            tuple: A tuple containing the status and the processed Paper object.
            (status, paper_obj): The status can be either "Error" or "Success". If an error occurs during processing,
            the status will be "Error" and paper_obj will be None. If processing is successful, the status will be
            "Success" and paper_obj will be a Paper object initialized with the parsed XML data.
        """
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
        """
        Processes a paper from an XML file.

        Parameters:
            paper_name (str): The name of the XML file.
            input_path (str, optional): The path of the corresponding PDF file. Defaults to None.

        Returns:
            Paper: A Paper object initialized with the parsed XML data.
        """
        res = self.parse(paper_name)
        return Paper(tree=res, filename=paper_name, pdf_path=input_path, xml_path=self.output_path)

    def process_folder(self, folder):
        """
        Processes all PDF papers in a given folder.

        Parameters:
            folder (str): The path to the folder containing the PDF papers.

        Returns:
            list: A list of Paper objects representing the processed papers.
        """
        papers = []
        for i in range(0, 3):
            if not self.grobid.test_alive():
                print("INITIALIZE GROBID FIRST")
                sleep(10)
                if i == 2:
                    print("GROBID NOT AVAILABLE")
                    exit(-1)
            else:
                break
        for paper in os.listdir(folder):
            if paper.endswith(".pdf"):
                paper_obj = self.process(folder + paper)
                papers.append(paper_obj)
        return papers

    def process_folder_from_xml(self, pdf_path=None):
        """
        Processes all XML papers in the output path directory.

        Parameters:
            pdf_path (str, optional): The path to the corresponding PDF files. Defaults to None.

        Returns:
            list: A list of Paper objects representing the processed papers.
        """
        papers = []
        for paper in os.listdir(self.output_path):
            if paper.endswith(".xml"):
                paper_obj = self.process_from_xml(paper, input_path=pdf_path)
                papers.append(paper_obj)
        return papers
