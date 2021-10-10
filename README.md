# Short introduction to MongoDB-FastAPI-Docker

This application can be used as a short introduction to FastAPI, Docker and MongoDB. 
Just set up your free [MongoDB account](https://www.mongodb.com/), 
create a free Cluster, refactor the config_template.json file to config.json and adjust the mongoURL respectively.

## Usage as Docker image
If you use this docker image, you have to declare an environment variable in the container called "mongoURL", 
which includes your whole mongodb connection string.