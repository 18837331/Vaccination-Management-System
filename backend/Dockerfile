FROM python:3.8
COPY requirements.txt /
WORKDIR /
RUN pip install -r ./requirements.txt --no-cache-dir
COPY app/ /app/
WORKDIR /app 
CMD ["python","backend.py"]