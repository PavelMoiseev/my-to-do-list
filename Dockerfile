FROM python:3.10.4
COPY . /my_organizer
WORKDIR /my_organizer
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]