# K8sTC
- Target: Limit bandwidth of k8s pods
- Idea: Perform traffic shaping on both ends of veth-pair using Linux TC TBF
- Test tool: iperf3
- Image: zhuangweikang/k8stc
- Total bandwidth: 1000mbps
- Test purpose: Set bandwidth of two pods(server, client) to 500mbps  
- K8s CNI plugin: Flannel

```shell script
ubuntu@isislab11:~/K8sTC$ sudo python3 main.py 
Launching iperf3-server and iperf3-client ...
Waiting for pod ready ...
Setting bandwidth ...

ubuntu@isislab11:~/K8sTC$ kubectl get pods -o wide
NAME     READY   STATUS    RESTARTS   AGE   IP             NODE        NOMINATED NODE   READINESS GATES
client   1/1     Running   0          54s   10.244.4.175   isislab15   <none>           <none>
server   1/1     Running   0          54s   10.244.1.12    isislab13   <none>           <none>

ubuntu@isislab11:~/K8sTC$ kubectl exec -it server -- iperf3 -s
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
Accepted connection from 10.244.4.175, port 59208
[  5] local 10.244.1.12 port 5201 connected to 10.244.4.175 port 59210
[ ID] Interval           Transfer     Bandwidth
[  5]   0.00-1.00   sec  54.9 MBytes   460 Mbits/sec                  
[  5]   1.00-2.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   2.00-3.00   sec  56.8 MBytes   476 Mbits/sec                  
[  5]   3.00-4.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   4.00-5.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   5.00-6.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   6.00-7.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   7.00-8.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   8.00-9.00   sec  56.9 MBytes   477 Mbits/sec                  
[  5]   9.00-10.00  sec  56.9 MBytes   477 Mbits/sec                  
[  5]  10.00-10.07  sec  4.25 MBytes   477 Mbits/sec                  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth
[  5]   0.00-10.07  sec  0.00 Bytes  0.00 bits/sec                  sender
[  5]   0.00-10.07  sec   571 MBytes   476 Mbits/sec                  receiver
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------

ubuntu@isislab11:~/K8sTC$ kubectl exec -it client -- iperf3 -c 10.244.1.12
Connecting to host 10.244.1.12, port 5201
[  4] local 10.244.4.175 port 59210 connected to 10.244.1.12 port 5201
[ ID] Interval           Transfer     Bandwidth       Retr  Cwnd
[  4]   0.00-1.00   sec  60.9 MBytes   510 Mbits/sec    0   2.87 MBytes       
[  4]   1.00-2.00   sec  56.9 MBytes   478 Mbits/sec   89   2.28 MBytes       
[  4]   2.00-3.00   sec  56.7 MBytes   476 Mbits/sec    0   2.46 MBytes       
[  4]   3.00-4.00   sec  56.9 MBytes   477 Mbits/sec    0   2.61 MBytes       
[  4]   4.00-5.00   sec  56.9 MBytes   477 Mbits/sec    0   2.73 MBytes       
[  4]   5.00-6.00   sec  56.9 MBytes   477 Mbits/sec    0   2.82 MBytes       
[  4]   6.00-7.00   sec  56.9 MBytes   477 Mbits/sec    0   2.89 MBytes       
[  4]   7.00-8.00   sec  56.9 MBytes   478 Mbits/sec    6   2.14 MBytes       
[  4]   8.00-9.00   sec  56.9 MBytes   477 Mbits/sec    0   2.24 MBytes       
[  4]   9.00-10.00  sec  56.9 MBytes   477 Mbits/sec   33   2.27 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth       Retr
[  4]   0.00-10.00  sec   573 MBytes   481 Mbits/sec  128             sender
[  4]   0.00-10.00  sec   571 MBytes   479 Mbits/sec                  receiver

iperf Done.
```
