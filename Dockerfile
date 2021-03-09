#
# Dockerfile
#
FROM python:3.8 
WORKDIR /middle-node
COPY src src
COPY json json
COPY output output
COPY requirements.txt .
COPY .git .git
RUN pip install -r requirements.txt
CMD ["python","src/main.py"]
