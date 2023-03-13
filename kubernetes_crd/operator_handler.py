  
import kopf 
import kubernetes 
import yaml 
@kopf.on.create('cogno.org', 'v1', 'grafana') 
def create_fn(body, spec, **kwargs): 

    # Get info from grafana object 
    name = body['metadata']['name'] 
    namespace = body['metadata']['namespace'] 
    nodeport = spec['nodeport'] 
    image = 'grafana/grafana' 
    port = 3000 
    if not nodeport: 
        raise kopf.HandlerFatalError(f"Nodeport must be set. Got {nodeport}.") 

      # Pod template 
    pod = {'apiVersion': 'v1', 'metadata': {'name' : name, 'labels': {'app': 'grafana'}},'spec': {'containers': [ { 'image': image, 'name': name }]}} 
 
    # Service template 
    svc = {'apiVersion': 'v1', 'metadata': {'name' : name}, 'spec': { 'selector': {'app': 'grafana'}, 'type': 'NodePort', 'ports': [{ 'port': port, 'targetPort': port,  'nodePort': nodeport }]}} 

    # Make the Pod and Service the children of the grafana object 
    kopf.adopt(pod, owner=body) 
    kopf.adopt(svc, owner=body) 
  
    # Object used to communicate with the API Server 
    api = kubernetes.client.CoreV1Api() 

    # Create Pod 
    obj = api.create_namespaced_pod(namespace, pod) 
    print(f"Pod {obj.metadata.name} created") 

    # Create Service 
    obj = api.create_namespaced_service(namespace, svc) 
    print(f"NodePort Service {obj.metadata.name} created, exposing on port {obj.spec.ports[0].node_port}") 

    # Update status 
    msg = f"Pod and Service created for grafana object {name}" 
    return {'message': msg}
@kopf.on.delete('cogno.org', 'v1', 'grafana') 
def delete(body, **kwargs): 
    msg = f"Grafana {body['metadata']['name']} and its Pod / Service children deleted" 
    return {'message': msg} 