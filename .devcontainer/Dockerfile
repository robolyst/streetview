FROM python:3.13.6-slim-bookworm

RUN apt update

RUN pip3 install --upgrade pip

# Install dependencies
RUN pip3 install uv
ADD pyproject.toml /tmp/pyproject.toml
ADD uv.lock /tmp/uv.lock
RUN (cd /tmp && uv pip install -r pyproject.toml --system --group dev)

# Prevent creating a virtual environment every time you run a uv command:
ENV UV_PROJECT_ENVIRONMENT=/usr/local/

ADD .devcontainer/jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

# Install oh my zsh
RUN apt install -y git zsh wget
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true
ENV SHELL /usr/bin/zsh

ENV PYTHONPATH="${PYTHONPATH}:/workspaces/streetview/src"