FROM python:3.6.9-alpine3.10

RUN mkdir -p /kytea/app
WORKDIR /kytea/app

COPY . .
RUN wget http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz \
    && cd kytea-0.4.7 \
    && ./configure
    && make
    && make install

CMD ["kytea", "--help"]
