# deliverable1

[![DOI](https://zenodo.org/badge/601755994.svg)](https://zenodo.org/badge/latestdoi/601755994)

<h1>Description</h1>
First deliverable project for the Artificial Intelligence and Open Science course

The purpose of this program is to convert and extract data from input PDF files in order to obtain 
the following:


- Draw a keyword cloud based on the words found in the abstract of your papers.
- Create a visualization showing the number of ﬁgures per article.
- Create a list of the links found in each paper.


<h1>Requirements</h1>

wordcloud==1.8.2.2

matplotlib==3.4.3

grobid-client==0.8.3

nltk==3.8.1

**Running on**

Docker version 20.10.17, build 100c70180f

conda 4.12.0 

Ubuntu 22.04

<h1>Install</h1>

<h2>From source</h2>
                

    git clone https://github.com/dan415/deliverables_ai_open_science.git
    cd deliverable1
    conda env create -f environment.yml
    conda activate openscience
    docker pull lfoppiano/grobid:0.7.2

<h2>Using docker</h2>

    docker pull lfoppiano/grobid:0.7.2
    docker pull danicabrera/delivery1:latest

<h1>Usage</h1>

Move files to be analyzed to the input_files folder.

If using docker:
    ./input_files and ./output_files are expected to be used as the folders
    for the input and output files, respectively.

<h2>From source</h2>

    docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2 &
    python src/pdf_analysis.py

Alternatively, you can specify the folder for the input pdf files and the desired output folder:

    python src/pdf_analysis.py --INPUT_PATH [input path] --OUTPUT_PATH [output path]

You can also set the configuration file for the grobid client, needed to process the documents:

    python src/pdf_analysis.py --INPUT_PATH [input path] --OUTPUT_PATH [output path] --GROBID_CLIENT_CONFIG_PATH [grobid config path]

None of them are required arguments. By default, these are set as ./input_files, ./output_files, ./config.json, respectively

<h2>Using Docker</h2>

Note: if you want to build the docker image from source, uncomment on the docker-compose file this line
   
    # build: . # if you want to build the image locally (line 13)

and comment this one: 

    image: danicabrera/delivery1:latest (line 14)

Then:

    cd deliverable1
    sudo docker-compose up

<h1>Author</h1>

Daniel Cabrera Rodríguez

Github: @dan415

<h1>License</h1>
Copyright (C) 1989, 1991 Free Software Foundation, Inc., Daniel Cabrera Rodríguez






