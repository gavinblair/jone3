docker stop jone3-server; docker rm jone3-server; docker run -d --name jone3-server -p 11435:11435 -v $(pwd):/code fastapi-image; docker logs -f jone3-server
