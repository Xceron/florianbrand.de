FROM python:3.12

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

WORKDIR /app

COPY requirements.txt .
RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

COPY . .

CMD ["python", "main.py"]