#FROM registry.blitzhub.io/conda_miniconda3
FROM andimajore/miniconda3_lunar
WORKDIR /usr/src/digest/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y supervisor nginx
RUN apt-get install -y libgtk-3-dev
RUN apt-get install wget

RUN pip install --upgrade pip

RUN conda install conda python=3.9
RUN conda install -c conda-forge -y django=4.1.7 graph-tool==2.48

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/digest/requirements.txt
RUN pip install -r /usr/src/digest/requirements.txt

RUN pip install biodigest==0.2.8
RUN #pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple biodigest==0.1.11
COPY . /usr/src/digest/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

#ENTRYPOINT ["sh", "/entrypoint.sh"]
