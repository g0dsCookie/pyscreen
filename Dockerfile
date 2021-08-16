ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION}

COPY requirements.txt requirements_k8s.txt /
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir -r requirements_k8s.txt \
 && rm -f /requirements*.txt

COPY setup.py requirements.txt requirements_k8s.txt /pyscreen/
COPY pyscreen /pyscreen/pyscreen/

RUN cd /pyscreen \
 && ./setup.py install \
 && ./setup.py install_data \
 && cd && rm -rf /pyscreen

COPY example.yml ./pyscreen.yml

CMD ["pyscreen"]