# openscience-grupo

<h1>Installation</h1>

<h2>Grobid</h2>
docker pull lfoppiano/grobid:0.7.2
docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2 &

<h2>Environment</h2>
conda create --name openenv python=3.9 rdflib=6.3.2 dash=2.9.3 findspark=2.0.1 pyspark=3.4.0 sentence-transformers=2.2.2 scikit-learn=1.0.2 transformers=4.28.1 -c conda-forge
conda activate openenv
pip install pygrobid
pip install pytest
pip install analyzer