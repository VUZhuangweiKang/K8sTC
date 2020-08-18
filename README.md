# K8sTC
- Target: Limit bandwidth of k8s pods
- Idea: Perform traffic shaping on both ends of veth-pair using Linux TC TBF
- Test tool: iperf3
- Image: zhuangweikang/k8stc

### Test Environment
```shell script
# Total bandwidth: 1000mbps
# Set bandwidth of iperf-server and iperf-client to 500mbps  
python3 main.py

# results

```
