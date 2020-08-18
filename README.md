# K8sTC
- Target: Limit bandwidth of k8s pods
- Idea: Perform traffic shaping on both ends of veth-pair using Linux TC TBF
- Test tool: iperf3
- Image: zhuangweikang/k8stc
- Total bandwidth: 1000mbps

```shell script
ubuntu@isislab11:~/K8sTC$ python3 main.py --help
usage: main.py [-h] [--deploy] [--replica REPLICA] [--bw BW]

optional arguments:
  -h, --help         show this help message and exit
  --deploy           run iperf-server/client deployment
  --replica REPLICA  the number of replicas for deployment
  --bw BW            target bandwidth for each pod in mbps

# Test 1: Run test in pods mode and set BW to 200mbps
ubuntu@isislab11:~/K8sTC$ sudo python3 main.py --bw 200
-------------- K8sTc --------------
Waiting for pod ready ...
Limiting bandwidth ...
ubuntu@isislab11:~/K8sTC$ cat client.log 
Unable to use a TTY - input is not a terminal or the right kind of file
Connecting to host 10.244.4.221, port 5201
[  4] local 10.244.3.57 port 35974 connected to 10.244.4.221 port 5201
[ ID] Interval           Transfer     Bandwidth       Retr  Cwnd
[  4]   0.00-1.00   sec  14.4 MBytes   121 Mbits/sec    0    595 KBytes       
[  4]   1.00-2.00   sec  23.2 MBytes   195 Mbits/sec   24    898 KBytes       
[  4]   2.00-3.00   sec  22.8 MBytes   191 Mbits/sec    0   1001 KBytes       
[  4]   3.00-4.00   sec  22.8 MBytes   191 Mbits/sec    0   1.05 MBytes       
[  4]   4.00-5.00   sec  22.8 MBytes   191 Mbits/sec    0   1.11 MBytes       
[  4]   5.00-6.00   sec  22.8 MBytes   191 Mbits/sec    0   1.15 MBytes       
[  4]   6.00-7.00   sec  22.5 MBytes   189 Mbits/sec    2    876 KBytes       
[  4]   7.00-8.00   sec  23.1 MBytes   194 Mbits/sec    0    930 KBytes       
[  4]   8.00-9.00   sec  22.7 MBytes   190 Mbits/sec    0    965 KBytes       
[  4]   9.00-10.00  sec  22.8 MBytes   191 Mbits/sec    0    987 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth       Retr
[  4]   0.00-10.00  sec   220 MBytes   184 Mbits/sec   26             sender
[  4]   0.00-10.00  sec   217 MBytes   182 Mbits/sec                  receiver

iperf Done.

# Test 2: Run test in deployment mode with replica=10, bw=100
ubuntu@isislab11:~/K8sTC$ sudo python3 main.py --deploy --replica 10 --bw 100
-------------- K8sTc --------------
Waiting for pod ready ...
Limiting bandwidth ...
ubuntu@isislab11:~/K8sTC$ ls
client-759df54f46-6km8b.log  client-759df54f46-jq82t.log  Dockerfile   server-546bc99fd6-6f5qw.log  server-546bc99fd6-lfxgq.log
client-759df54f46-7lwhq.log  client-759df54f46-ncsgc.log  K8sTC.py     server-546bc99fd6-ds8x2.log  server-546bc99fd6-lv9rg.log
client-759df54f46-c8ccs.log  client-759df54f46-qqfd9.log  main.py      server-546bc99fd6-fjf7x.log  server-546bc99fd6-t8zmn.log
client-759df54f46-ccml6.log  client-759df54f46-rxb67.log  __pycache__  server-546bc99fd6-fjw8p.log  server-546bc99fd6-wb57b.log
client-759df54f46-h8zb8.log  client-759df54f46-sqd2l.log  README.md    server-546bc99fd6-ftb9v.log  server-546bc99fd6-wnrmp.log
ubuntu@isislab11:~/K8sTC$ cat client-759df54f46-ccml6.log
Unable to use a TTY - input is not a terminal or the right kind of file
Connecting to host 10.244.5.48, port 5201
[  4] local 10.244.4.225 port 33858 connected to 10.244.5.48 port 5201
[ ID] Interval           Transfer     Bandwidth       Retr  Cwnd
[  4]   0.00-1.00   sec  14.3 MBytes   120 Mbits/sec    0    580 KBytes       
[  4]   1.00-2.00   sec  10.3 MBytes  86.4 Mbits/sec   14    326 KBytes       
[  4]   2.00-3.00   sec  9.94 MBytes  83.3 Mbits/sec    0    347 KBytes       
[  4]   3.00-4.00   sec  10.6 MBytes  89.0 Mbits/sec    0    369 KBytes       
[  4]   4.00-5.00   sec  11.4 MBytes  95.7 Mbits/sec    0    392 KBytes       
[  4]   5.00-6.00   sec  11.3 MBytes  95.2 Mbits/sec    0    412 KBytes       
[  4]   6.00-7.00   sec  11.4 MBytes  95.7 Mbits/sec    0    433 KBytes       
[  4]   7.00-8.00   sec  11.4 MBytes  95.7 Mbits/sec    0    452 KBytes       
[  4]   8.00-9.00   sec  11.3 MBytes  95.2 Mbits/sec    0    470 KBytes       
[  4]   9.00-10.00  sec  11.4 MBytes  95.7 Mbits/sec    0    487 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth       Retr
[  4]   0.00-10.00  sec   113 MBytes  95.2 Mbits/sec   14             sender
[  4]   0.00-10.00  sec   110 MBytes  92.3 Mbits/sec                  receiver

iperf Done.
ubuntu@isislab11:~/K8sTC$ cat client-759df54f46-sqd2l.log
Unable to use a TTY - input is not a terminal or the right kind of file
Connecting to host 10.244.6.133, port 5201
[  4] local 10.244.6.135 port 33364 connected to 10.244.6.133 port 5201
[ ID] Interval           Transfer     Bandwidth       Retr  Cwnd
[  4]   0.00-1.00   sec  12.8 MBytes   107 Mbits/sec    0    594 KBytes       
[  4]   1.00-2.00   sec  11.5 MBytes  96.2 Mbits/sec   27    496 KBytes       
[  4]   2.00-3.00   sec  11.4 MBytes  95.7 Mbits/sec    0    549 KBytes       
[  4]   3.00-4.00   sec  11.4 MBytes  95.7 Mbits/sec    0    584 KBytes       
[  4]   4.00-5.00   sec  11.0 MBytes  92.6 Mbits/sec    2    438 KBytes       
[  4]   5.00-6.00   sec  11.7 MBytes  98.2 Mbits/sec    0    472 KBytes       
[  4]   6.00-7.00   sec  11.3 MBytes  95.2 Mbits/sec    0    491 KBytes       
[  4]   7.00-8.00   sec  11.4 MBytes  95.7 Mbits/sec    0    501 KBytes       
[  4]   8.00-9.00   sec  11.3 MBytes  94.7 Mbits/sec    0    504 KBytes       
[  4]   9.00-10.00  sec  11.5 MBytes  96.2 Mbits/sec    0    512 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth       Retr
[  4]   0.00-10.00  sec   115 MBytes  96.7 Mbits/sec   29             sender
[  4]   0.00-10.00  sec   114 MBytes  95.5 Mbits/sec                  receiver

iperf Done.

```
