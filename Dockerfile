FROM python:3.6

COPY ./gpxToExif/requirements.txt /requirements.txt
RUN python -m pip install -r /requirements.txt
WORKDIR /gpxmatcher
CMD ["python", "script.py"]