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

# Set up logging
logging.basicConfig(filename=f'./log.log', encoding='utf-8', format='%(asctime)s %(message)s',
                    level=logging.DEBUG)


def healthcheck(server):
    '''
    Checks if the grobid server is healthy.
    :param server: the grobid server url
    '''
    def request(srv):
        try:
            # Send a GET request to the server and check the response
            return bool(requests.get(f"{srv}/api/isalive").content.decode().capitalize())
        except:
            return False


if __name__ == '__main__':
    # Clear the log file
    open(f"log.log", "w").close()

    # Set up argument parsing
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

    # Parse the arguments
    args = parser.parse_args()

    # Define the input and output paths
    input_path = f"{args.RES_FOLDER}/datasets/space/raw/"
    output_path = f"{args.RES_FOLDER}/datasets/space/grobid/"

    # Initialize the paper processor
    processor = PaperProcessor(output_path=output_path)

    # Process the PDFs or XMLs
    if len(os.listdir(output_path)) == 0:
        logging.info('Processing PDFs')
        print('Processing PDFs')
        papers = processor.process_folder(input_path)
    else:
        logging.info('Processing XMLs')
        print('Processing XMLs')
        papers = processor.process_folder_from_xml(pdf_path=input_path)

    # Create the paper space
    logging.info('Creating paper space')
    print('Creating paper space')
    paper_space = PaperSet(papers)

    # Serialize the paper space
    logging.info('Serializing paper space')
    print('Serializing paper space')
    kg = RDFParser(paper_space)
    json_ld = kg.g.serialize(format='json-ld', indent=4)

    # Write the serialized data to a file
    with open(f'{args.RES_FOLDER}/datasets/json-ld/kg.jsonld', 'w') as outfile:
        json.dump(json.loads(json_ld), outfile)

    logging.info('Done!')
    print('Done!')
