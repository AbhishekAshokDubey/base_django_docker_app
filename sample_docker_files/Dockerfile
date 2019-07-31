FROM google/cloud-sdk
RUN apt-get update
RUN apt-get install tesseract-ocr -y \
	curl \
    python3 \
	poppler-utils \
	python-poppler \
    python3-pip \
	git

RUN apt-get clean && apt-get autoremove
RUN pip3 install pytesseract django pdf2image
RUN git clone https://github.com/AbhishekAshokDubey/base_django_docker_app.git
WORKDIR "/base_django_docker_app"
CMD ["python3", "pull_script/pull_pdfs_ocr.py"]