FROM python:3.11

WORKDIR /e-doctor

COPY requirements.txt /e-doctor/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /e-doctor/
