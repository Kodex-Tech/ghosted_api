FROM python:3.8
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 2500
CMD ["python" , "main.py"]