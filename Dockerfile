FROM python:3.9

WORKDIR /NEO4J_GRAPHDB

COPY  . /NEO4J_GRAPHDB/

RUN pip install neo4j-driver py2neo matplotlib pandas neo4j tabulate streamlit altair

CMD [ "streamlit","run" ,"./app/neo4j_app.py"] 