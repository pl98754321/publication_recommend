FROM python:3.10-slim-bullseye
RUN apt-get update
RUN apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
RUN apt -y remove mailutils
RUN apt -y autoremove

RUN apt-get update && \
    apt-get install -y libaio1 unzip wget
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && \
    rm -f instantclient-basiclite-linuxx64.zip && \
    cd instantclient* && \
    rm -f *jdbc* *occi* *mysql* *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

RUN python -m pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD . .
# RUN ["python", "print_loop.py"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]