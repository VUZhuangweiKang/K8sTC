from K8sTC import K8sTC
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--deploy', action='store_true', default=False, help='run iperf-server/client deployment')
    parser.add_argument('--replica', type=int, default=10, help='the number of replicas for deployment')
    parser.add_argument('--bw', type=int, default=100, help='target bandwidth for each pod in mbps')
    k8stc = K8sTC()
    args = parser.parse_args()

    print('-------------- K8sTc --------------')

    if not args.deploy:
        k8stc.create_iperf(name='server')
        k8stc.create_iperf(name='client')
        print('Waiting for pod ready ...')
        k8stc.wait_pods_ready(['server', 'client'])
    else:
        k8stc.create_iperf_deploy(name='server')
        k8stc.create_iperf_deploy(name='client')
        print('Waiting for pod ready ...')
        while True:
            if len(k8stc.list_pods_name()) >= 2 * args.replica:
                break
        k8stc.wait_pods_ready(k8stc.list_pods_name())

    print('Limiting bandwidth ...')
    k8stc.limit_bw(args.bw)
    k8stc.execute()


