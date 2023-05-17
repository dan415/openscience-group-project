# openscience-grupo

[![DOI](https://zenodo.org/badge/637350948.svg)](https://zenodo.org/badge/latestdoi/637350948)

<h1>Description</h1>
This Github repository serves the purpose of containing the group project delivery for the subject of Artificial Intelligence and Open Science (Degree of Computer Engineering, Universidad Politécnica de Madrid).


Upon execution, the program will take as input a folder containing pdf files, and will output a folder containing kf.json, which is the Knowledge graph built with said papers.

In order to query the knowledge graph, you can load the graph using the process.ipynb notebook.


Another option is to use Fuseki, which is a SPARQL endpoint. You can load the graph into Fuseki and query it using the SPARQL endpoint.


<h1>Tasks</h1>

  -  1: Papers selection. There are papers from 2 distinct research fields, and the main reason for selecting them is their complete metadata: Acknowledgments, authors, affiliations, etc.
  -  2: Leveraging GROBID for Knowledge Graph Construction: Extracting Relevant Information from Selected Papers
  -  3: Ontology. Diagram of the ontology that was defined for the project
  -  4: Transform the classes and properties from the xml already processed (by GROBID) to the \"Paper Space\" for a more useful representation
  -  5: Enriching with wikidata (affiliation, website and Journal) and OpenAlex (author's count of citations and publications)
  -  6: Obtain Knowledge Graph from Paper Space -> JSON-LD
  -  7: Clustering
  -  8: "Subtask 8: Topic Modeling
  -  9: "Subtask 9: Entity Recognition

<h1>Run with docker-compose</h1>

sudo docker-compose up

<h1>Run From Source</h1>

<h2>Installation and Requirements</h2>
<h3>Grobid</h3>
docker pull lfoppiano/grobid:0.7.2
docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2 &

<h3>Fuseki</h3>
sudo docker run -e ADMIN_PASSWORD=D=1234 -it --rm -p 3030:3030 stain/jena-fuseki

<h3>Environment</h3>
conda create --name openenv python=3.9 rdflib=6.3.2 dash=2.9.3 findspark=2.0.1 pyspark=3.4.0 sentence-transformers=2.2.2 scikit-learn=1.0.2 transformers=4.28.1  gensim=4.3.0 -c conda-forge
conda activate openenv
pip install pygrobid==0.1.6
pip install wikidataintegrator==0.9.27
pip install pyalex==0.9
pip install pytest==6.2.5
pip install analyzer==0.1.0
cd src

<h3>Run command</h2>

python main.py --RES_FOLDER  ../res

<h1>Author</h1>

Daniel Cabrera Rodríguez

Github: @dan415

Sebastián Bayona

Github: @sbayonag

Alejandro Ayuso

Github: @AlexAyuso01

Alejandro Morán

Github: @Alejandro9998

<h1>License</h1>
MIT License

Copyright (c) 2023 Daniel Cabrera Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.




