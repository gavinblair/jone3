FROM python:3.10-slim

# set the working directory
WORKDIR /code

# install dependencies
COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy the src to the folder
COPY ./ /code

# start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "11435", "--reload"]