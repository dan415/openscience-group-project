# syntax=docker/dockerfile:1

FROM conda/miniconda3


#RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
#RUN apt-get update && apt-get install -y python3.9 python3.9-dev
RUN conda install python=3.9
WORKDIR /app
COPY . .
#RUN apt-get install python3-pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "src/main.py", "--RES_FOLDER", "./res"]

