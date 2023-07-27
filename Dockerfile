FROM andimajore/miniconda3_mantic
WORKDIR /usr/src/digest/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y supervisor nginx build-essential
RUN apt-get install -y libgtk-3-dev
RUN apt-get install wget

RUN pip install --upgrade pip

RUN conda install conda python=3.9
RUN conda install -c conda-forge -y graph-tool==2.48
RUN conda install -c conda-forge seaborn==0.12.2

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/digest/requirements.txt
RUN pip install -r /usr/src/digest/requirements.txt

RUN pip install biodigest==0.2.14
COPY . /usr/src/digest/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000