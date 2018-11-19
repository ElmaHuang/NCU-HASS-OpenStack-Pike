#! /bin/sh

sudo strace -p 1 &
sudo kill -9 1

#chmod +x os_hang.sh