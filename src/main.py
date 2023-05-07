import argparse
import json

import requests
from grobid.client import GrobidClient
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(filename=f'./log.log', encoding='utf-8', format='%(asctime)s %(message)s',
                    level=logging.DEBUG)


def healthcheck(server):
    '''
    Checks if the grobid server is healthy.
    :param server: the grobid server url
    '''

    def request(srv):
        try:
            return bool(requests.get(f"{srv}/api/isalive").content.decode().capitalize())
        except:
            return False

def get_langauge(papers, elem, schema, namespace):
    '''
    Returns the language of a given element in a TEI document, if available.

    :param papers: list. A list of parsed TEI documents.
    :param elem: int. Index of the element in the `papers` list whose language we want to retrieve.
    :param schema: str. The schema used to define the TEI document, e.g. "tei:" or "tei2:".
    :param namespace: str. The namespace used to define the TEI document, e.g. "xml:" or "tei:".

    :returns:language: str or None
        The language of the element, as specified in the TEI header, or None if no language is specified.
    '''
    if papers[elem].getroot().find(f"{schema}teiHeader") is not None:
        if f"{namespace}lang" in papers[elem].getroot().find(f"{schema}teiHeader").attrib.keys():
            return papers[elem].getroot().find(f"{schema}teiHeader").attrib[f"{namespace}lang"]
    return None



def get_abstract(papers, elem, schema):
    '''
    This function gets the abstract of a given paper.
    :param papers: a dictionary of papers
    :param elem: the name of the XML file containing the paper
    :param schema: the schema string
    :return: the abstract string
    '''
    if papers[elem].find(f"{schema}teiHeader") is not None:
        if papers[elem].find(f"{schema}teiHeader").find(f"{schema}profileDesc") is not None:
            if papers[elem].find(f"{schema}teiHeader").find(f"{schema}profileDesc").find(
                    f"{schema}abstract") is not None:
                return ET.tostring(
                    papers[elem].find(f"{schema}teiHeader").find(f"{schema}profileDesc").find(f"{schema}abstract"),
                    encoding='utf-8', method='text').strip().decode("utf-8")
    return ""







if __name__ == '__main__':
    open(f"log.log", "w").close()
    parser = argparse.ArgumentParser(
        prog='PDF Analysis',
        description='Analyse PDFs using GROBID',
    )
    parser.add_argument(
        "--GROBID_PORT",
        default="8070",
        required=False,
        help="Port for the Grobid application",
    )

    args = parser.parse_args()
    grobid_client_config_path = args.GROBID_CLIENT_CONFIG_PATH

    with open(grobid_client_config_path, "r") as fp:
        config = json.load(fp)

    healthcheck(config["grobid_server"])

    client = GrobidClient(host="localhost", port=args.GROBID_PORT)
    # client.process("processFulltextDocument",
    #                input_path=input_dir,
    #                n=20,
    #                output=output_dir,
    #                consolidate_citations=True,
    #                verbose=False
    #                )