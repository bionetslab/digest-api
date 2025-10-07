FROM ubuntu:noble as base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y supervisor libgtk-3-dev wget apt-utils
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common cron unzip
RUN apt-get autoclean -y && apt-get autoremove -y && apt-get clean -y

ENV CONDA_DIR /opt/conda
RUN wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
RUN bash Miniforge3-$(uname)-$(uname -m).sh -b -p "${CONDA_DIR}"
ENV PATH=$CONDA_DIR/bin:$PATH
RUN chmod +x "${CONDA_DIR}/etc/profile.d/conda.sh"
RUN "${CONDA_DIR}/etc/profile.d/conda.sh"
RUN chmod +x "${CONDA_DIR}/etc/profile.d/mamba.sh"
RUN "${CONDA_DIR}/etc/profile.d/mamba.sh"

RUN conda init bash

RUN mamba update -n base -c defaults mamba conda
RUN mamba install -y python=3.10
RUN mamba update -y --all
RUN pip install pip==23
RUN pip install --upgrade pip requests cryptography pyopenssl
RUN chmod 777 -R /opt/conda

FROM base
WORKDIR /usr/src/digest/

RUN apt-get update && apt-get install -y nginx build-essential

RUN mamba install conda python=3.10
RUN mamba install -c conda-forge -y graph-tool==2.98
RUN mamba install -c conda-forge seaborn==0.12.2

RUN pip install psycopg2-binary
COPY ./requirements.txt /usr/src/digest/requirements.txt
RUN pip install -r /usr/src/digest/requirements.txt

RUN mamba install biodigest
COPY . /usr/src/digest/

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
