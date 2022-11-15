FROM python:3.10.7-bullseye

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN curl -fsSL https://deb.nodesource.com/setup_19.x | bash - &&\
apt-get install -y nodejs


RUN npm install -g dbdocs

RUN git clone https://github.com/giasmith/contrans

WORKDIR /contrans

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root"]