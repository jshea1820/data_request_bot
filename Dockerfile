FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y make
RUN apt install -y build-essential
RUN apt install -y libssl-dev
RUN apt install -y zlib1g-dev

RUN apt install -y libbz2-dev 
RUN apt install -y libreadline-dev
RUN apt install -y libsqlite3-dev 
RUN apt install -y wget
RUN apt install -y curl 
RUN apt install -y llvm 

RUN apt install -y libncurses5-dev
RUN apt install -y libncursesw5-dev
RUN apt install -y xz-utils
RUN apt install -y tk-dev
RUN apt install -y libffi-dev
RUN apt install -y liblzma-dev
RUN apt install -y git

RUN rm -rf /var/lib/apt/lists/*

RUN curl https://pyenv.run | bash

ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:${PYENV_ROOT}/shims:$PATH"

RUN pyenv install 3.11.10
RUN pyenv global 3.11.10
RUN pip install pipenv

RUN apt update

RUN echo hello

RUN apt install -y postgresql postgresql-contrib sudo

RUN mkdir /workdir
WORKDIR /workdir
ENV PYTHONPATH=.

COPY Pipfile /workdir
COPY Pipfile.lock /workdir
RUN pipenv install

RUN mkdir /app
COPY app/* /workdir/app/


CMD ["pipenv", "run", "shiny", "run", "./app/app.py", "--host", "0.0.0.0", "--port", "8000"]

