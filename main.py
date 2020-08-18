from K8sTC import K8sTC
import time

if __name__ == '__main__':
    k8stc = K8sTC()
    print('Launching iperf3-server and iperf3-client ...')
    k8stc.create_iperf(name='server')
    k8stc.create_iperf(name='client')
    print('Waiting for pod ready ...')
    k8stc.wait_pods_ready(['server', 'client'])
    print('Setting bandwidth ...')
    k8stc.divide_pod_bw(2, 1000)

