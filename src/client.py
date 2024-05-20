from kubernetes.client import AppsV1Api, CoreV1Api


class KubernetesClient:

    def __init__(self):

        self.app_v1_api = AppsV1Api()
        self.core_v1_api = CoreV1Api()
