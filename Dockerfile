FROM python:3.10

RUN mkdir -p /dataverse
WORKDIR /dataverse

# install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# install deps
COPY Pipfile* ./
RUN pipenv sync --system

COPY ./ /dataverse

ENTRYPOINT ["scripts/entrypoint.sh"]

