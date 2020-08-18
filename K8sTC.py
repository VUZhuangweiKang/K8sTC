import subprocess
import time

from kubernetes import client, config
from kubernetes.stream import stream
import os


class K8sTC(object):
    def __init__(self):
        config.load_kube_config()
        self.apps_v1_api = client.AppsV1Api()
        self.core_v1_api = client.CoreV1Api()

    def create_iperf(self, name='server'):
        self.core_v1_api.create_namespaced_pod(
            namespace="default",
            body=client.V1Pod(
                api_version="v1",
                kind="Pod",
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace="default"
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="iperf",
                            tty=True,
                            image="zhuangweikang/k8stc:latest",
                            image_pull_policy="IfNotPresent",
                            security_context=client.V1SecurityContext(
                                capabilities=client.V1Capabilities(add=["NET_ADMIN"])),
                            resources=client.V1ResourceRequirements(
                                limits={"cpu": "100m", "memory": "1Gi"},
                                requests={"cpu": "100m", "memory": "1Gi"})
                        )
                    ],
                    restart_policy="Never"
                )
            ), async_req=False)

    def create_iperf_deploy(self, name):
        self.apps_v1_api.create_namespaced_deployment(
            namespace='default',
            body=client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace="default",
                    labels={'app': name}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=10,
                    selector=client.V1LabelSelector(match_labels={'app': name}),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(labels={'app': name}),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    tty=True,
                                    image="zhuangweikang/k8stc:latest",
                                    image_pull_policy="IfNotPresent",
                                    security_context=client.V1SecurityContext(
                                        capabilities=client.V1Capabilities(add=["NET_ADMIN"])),
                                    resources=client.V1ResourceRequirements(
                                        limits={"cpu": "100m", "memory": "1Gi"},
                                        requests={"cpu": "100m", "memory": "1Gi"})
                                )
                            ]
                        )
                    )
                )
            )
        )

    def list_nodes_name(self):
        nodes = []
        for node in self.core_v1_api.list_node().items:
            nodes.append(node.metadata.name)
        return nodes

    def list_nodes_ip(self):
        nodes_addr = {}
        for node in self.core_v1_api.list_node().items:
            for addr in node.status.addresses:
                if addr.type == "InternalIP":
                    nodes_addr.update({node.metadata.name: addr.address})
        return nodes_addr

    def list_pods_ip(self):
        pods_addr = {}
        for pod in self.core_v1_api.list_namespaced_pod(namespace="default").items:
            pods_addr.update({pod.metadata.name: pod.status.pod_ip})
        return pods_addr

    def list_pods_name(self):
        pods_name = []
        for pod in self.core_v1_api.list_namespaced_pod(namespace="default").items:
            pods_name.append(pod.metadata.name)
        return pods_name

    def get_containers(self):
        containers = {}
        for pod in self.core_v1_api.list_namespaced_pod(namespace='default').items:
            pod_name = pod.metadata.name
            node_name = pod.spec.node_name
            con_ids = [con.container_id.split('docker://')[1] for con in pod.status.container_statuses]
            if node_name not in containers:
                containers.update({node_name: {pod_name: con_ids}})
            else:
                containers[node_name].update({pod_name: con_ids})
        return containers

    def get_container_veth(self):
        containers = self.get_containers()
        veth_ifs = {}
        for node in containers:
            veth_ifs.update({node: []})
            # get all ifaces from node
            exec_command = "sudo ssh %s ip ad | grep @" % node
            tmp = subprocess.check_output(exec_command, shell=True).decode().strip().split('\n')
            tmp = [x.split('@')[0] for x in tmp]
            vifs = {}
            for item in tmp:
                ifpair = item.split(': ')
                vifs.update({ifpair[0]: ifpair[1]})
            for pod in containers[node]:
                exec_command = [
                    '/bin/sh',
                    '-c',
                    'cat /sys/class/net/eth0/iflink | sed s/[^0-9]*//g']
                ifindex = stream(self.core_v1_api.connect_get_namespaced_pod_exec, name=pod, namespace='default',
                                 command=exec_command,
                                 stderr=True, stdin=False,
                                 stdout=True, tty=False)
                # ifindex = iflink
                veth_ifs[node].append((pod, vifs[ifindex]))
        return veth_ifs

    def limit_bw(self, bw):
        veths = self.get_container_veth()
        for node in veths:
            for veth in veths[node]:
                # set download BW in node
                cmd = "ssh %s sudo tc qdisc add dev %s root tbf rate %dmbit latency 50ms burst 10000 mpu 64 mtu 15000" % (
                    node, veth[1], bw)
                subprocess.check_output(cmd, shell=True).decode()

                # set upload BW in container
                cmd = "tc qdisc add dev eth0 root tbf rate %dmbit latency 50ms burst 10000 mpu 64 mtu 15000" % bw
                stream(self.core_v1_api.connect_get_namespaced_pod_exec, name=veth[0], namespace='default',
                       command=cmd,
                       stderr=True, stdin=False,
                       stdout=True, tty=False)

    def wait_pods_ready(self, pods):
        while True:
            try:
                for pod in self.core_v1_api.list_namespaced_pod(namespace='default').items:
                    for con_status in pod.status.container_statuses:
                        if con_status.state.running is not None and pod.metadata.name in pods:
                            pods.remove(pod.metadata.name)
            except:
                pass
            if len(pods) == 0:
                break

    def execute(self):
        servers = []
        servers_ip = []
        clients = []
        for pod in self.core_v1_api.list_namespaced_pod(namespace='default').items:
            if 'server' in pod.metadata.name:
                servers.append(pod.metadata.name)
                servers_ip.append(pod.status.pod_ip)
            else:
                clients.append(pod.metadata.name)
        for i in range(len(servers)):
            start_server = 'nohup kubectl exec -it %s -- iperf3 -s > %s.log 2>&1 &' % (servers[i], servers[i])
            os.system(start_server)
            time.sleep(2)
            start_client = 'nohup kubectl exec -it %s -- iperf3 -c %s > %s.log 2>&1 &' % (clients[i], servers_ip[i], clients[i])
            os.system(start_client)