from K8sTC import K8sTC


if __name__ == '__main__':
    k8stc = K8sTC()
    k8stc.create_iperf(name='server')
    k8stc.create_iperf(name='client')
    k8stc.wait_pod_ready()
    k8stc.divide_pod_bw(2, 1000)

