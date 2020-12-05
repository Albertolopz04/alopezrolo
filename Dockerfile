FROM python:3.7
LABEL maintainer="Alberto Lopez @albertolopz04"

EXPOSE 8501

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install xlrd
RUN pip install -r requirements.txt


ENTRYPOINT [ "streamlit", "run"]
CMD ["wecscomparator.py"]
