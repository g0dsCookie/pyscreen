ARG PYTHON_VERSION=3
FROM python:${PYTHON_VERSION}

COPY requirements.txt ./
COPY requirements_k8s.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir -r requirements_k8s.txt

COPY pyscreen ./pyscreen
COPY example.yml ./pyscreen.yml

CMD ["python", "-m", "pyscreen.cli"]