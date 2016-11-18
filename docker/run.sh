nvidia-docker rm inferer
nvidia-docker run --ulimit nofile=327680:327680 --ulimit nproc=65536:65536 --name inferer -p 5000:5000 -v /home/ivan/Documentos/tileo:/tileo -w /tileo tileo/ml-py-inferer:latest
