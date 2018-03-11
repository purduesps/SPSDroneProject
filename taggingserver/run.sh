go build index.go
./index &
SERV_PID=$!
echo $SERV_PID > tagid.txt
