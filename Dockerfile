FROM registry.blitzhub.io/conda_miniconda3

WORKDIR /usr/src/digest/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install -y supervisor nginx
RUN apt-get install -y libgtk-3-dev
RUN apt-get install wget

RUN conda install conda python=3.8
RUN conda install -c conda-forge -y django=4.0.2 graph-tool==2.45

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/digest/requirements.txt
RUN pip install -r /usr/src/digest/requirements.txt

RUN pip install biodigest==0.2.1
RUN #pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple biodigest==0.1.11
COPY . /usr/src/digest/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

#ENTRYPOINT ["sh", "/entrypoint.sh"]
