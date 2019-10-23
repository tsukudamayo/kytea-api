FROM python:3.6.9-buster

RUN mkdir -p /kytea/app
WORKDIR /kytea/app

COPY . .
RUN apt-get update \
    && apt-get -y install emacs \
    && git clone https://github.com/tsukudamayo/dotfiles.git \
    && cp -r ~/dotfiles/linux/.emacs.d ~/ \
    && cp -r ~/dotfiles/.fonts ~/

RUN wget http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz \
    && cd kytea-0.4.7 \
    && ./configure \
    && make \
    && make install

CMD ["/bin/bash"]
