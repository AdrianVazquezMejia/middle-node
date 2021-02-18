#
# Dockerfile
#
FROM python:3.8 
WORKDIR /middle-node
COPY middle-node .
RUN pip install -r requirements.txt
CMD ["python","src/main.py"]
