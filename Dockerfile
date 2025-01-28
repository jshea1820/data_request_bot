FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

# Start with all the needed app installs
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

# Install and configure pyenv
RUN curl https://pyenv.run | bash

ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:${PYENV_ROOT}/shims:$PATH"


# Use pyenv to install python and pipenv
RUN pyenv install 3.11.10
RUN pyenv global 3.11.10
RUN pip install pipenv


# Set up the working directory
RUN mkdir /workdir
WORKDIR /workdir
ENV PYTHONPATH=.

# Move pipfiles over and install python packages
COPY Pipfile /workdir
COPY Pipfile.lock /workdir
RUN pipenv install

# Move the app over
COPY web_server/ /workdir/web_server/
COPY graph_api/ /workdir/graph_api/

COPY run_app.sh /workdir

RUN chmod +x ./run_app.sh

CMD ["./run_app.sh"]
