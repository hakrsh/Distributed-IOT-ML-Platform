if [ ! "$(docker ps -q -f name=mongo)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=mongo)" ]; then
        # cleanup
        docker rm mongo
    else
        docker volume create mongodbdata
    fi
    # run your container
    docker run --rm -d -p 27017:27017 -v mongodbdata:/data/db -h $(hostname) --name mongo mongo:5.0.3 --replSet=test && sleep 4 && docker exec mongo mongo --eval "rs.initiate();"
fi