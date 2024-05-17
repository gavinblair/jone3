docker build -t fastapi-image .
docker run -d --name jone3-server -p 11435:11435 -v $(pwd):/code fastapi-image