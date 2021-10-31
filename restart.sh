# need adjustments once testing
git pull
sudo docker stop digest_backend
sudo docker rm digest_backend
sudo docker build -t digest_backend .
sudo docker create --restart always --name digest_backend -v digest_db_volume:/var/lib/postgresql/digest/ digest_backend
sudo docker network connect digest_net ddigest_backend
sudo docker network connect nginx-net digest_backend
sudo docker start digest_backend
