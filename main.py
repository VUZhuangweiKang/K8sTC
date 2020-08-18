from K8sTC import K8sTC
import threading

if __name__ == '__main__':
    k8stc = K8sTC()
    print('Launching iperf3-server and iperf3-client ...')
    k8stc.create_iperf(name='server')
    k8stc.create_iperf(name='client')
    print('Waiting for pod ready ...')
    k8stc.wait_pod_ready()
    print('Setting bandwidth ...')
    k8stc.divide_pod_bw(2, 1000)

    server_ip = k8stc.list_pods_ip()['client']

    start_server = 'iperf3 -s'
    start_client = 'iperf3 -c %s' % server_ip

    k8stc.execute(start_server, 'server')
    k8stc.execute(start_client, 'client')

    print('server logs:', k8stc.get_logs('server'))
    print('client logs:', k8stc.get_logs('client'))

