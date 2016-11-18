FROM tileo/py-faster-rcnn

WORKDIR /root
RUN git clone https://github.com/splashblot/ml-py-inferer.git
WORKDIR /root/ml-py-inferer

RUN ln -s /root/py-faster-rcnn py-faster-rcnn

RUN run-on-env conda install -y --file requirements.txt -c conda-forge

COPY files/run-ml-py-inferer.sh /root/run-ml-py-inferer.sh
RUN chmod +x /root/run-ml-py-inferer.sh

EXPOSE 5000

CMD ["/root/run-ml-py-inferer.sh"]
