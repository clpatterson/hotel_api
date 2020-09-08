# Use the slimmer version of python 3.7
FROM python:3.7

COPY . /hotel_api

WORKDIR /hotel_api

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python"]

CMD ["api.py"]