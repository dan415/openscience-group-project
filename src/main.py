import argparse
import json
import os

import requests
from grobid.client import GrobidClient
import xml.etree.ElementTree as ET
import logging

from processor import PaperProcessor
from src.paper_space import PaperSet
from src.rdfparser import RDFParser

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
    parser.add_argument(
        "--FUSEKI_PORT",
        default="3030",
        required=False,
        help="Port for the Fuseki application",
    )
    parser.add_argument(
        "--RES_FOLDER",
        required=True,
        help="Folder where the inputs and results will be stored",
    )

    args = parser.parse_args()

    input_path = f"{args.RES_FOLDER}/datasets/space/raw/"
    output_path = f"{args.RES_FOLDER}/datasets/space/grobid/"


    processor = PaperProcessor(output_path=output_path)
    if len(os.listdir(output_path)) == 0:
        logging.info('Processing PDFs')
        print('Processing PDFs')
        papers = processor.process_folder(input_path)
    else:
        logging.info('Processing XMLs')
        print('Processing XMLs')
        papers = processor.process_folder_from_xml(pdf_path=input_path)
    logging.info('Creating paper space')
    print('Creating paper space')
    paper_space = PaperSet(papers)
    logging.info('Serializing paper space')
    print('Serializing paper space')
    kg = RDFParser(paper_space)
    json_ld = kg.g.serialize(format='json-ld', indent=4)
    with open(f'{args.RES_FOLDER}/datasets/json-ld/kg.jsonld', 'w') as outfile:
        json.dump(json.loads(json_ld), outfile)

    logging.info('Done!')
    print('Done!')
