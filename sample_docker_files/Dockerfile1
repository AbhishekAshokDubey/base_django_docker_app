FROM ubuntu:18.04
MAINTAINER adubey4@slb.com 

RUN apt-get update

RUN apt-get install tesseract-ocr -y \
    python3 \
	poppler-utils \
	python-poppler \
    #python-setuptools \
    python3-pip \
	git

RUN apt-get clean \
    && apt-get autoremove

RUN pip3 install pytesseract django pdf2image
RUN git clone https://github.com/AbhishekAshokDubey/base_django_docker_app.git
WORKDIR "/base_django_docker_app"
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

#docker run -it -p 8000:8000 adubey4/ocr