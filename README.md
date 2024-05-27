# Kubernetes Experiments

## [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)

In Kubernetes, namespaces provide a mechanism for isolating groups of resources within a single cluster. Names of resources need to be unique within a namespace, but not across namespaces. Namespace-based scoping is applicable only for namespaced objects (e.g. Deployments, Services, etc.) and not for cluster-wide objects (e.g. StorageClass, Nodes, PersistentVolumes, etc.).

Namespaces are intended for use in environments with many users spread across multiple teams, or projects.

Namespaces cannot be nested inside one another and each Kubernetes resource can only be in one namespace.

### Initial Namespaces

Kubernetes starts with 4 initial namespaces:
1. default:
Kubernetes includes this namespace so that you can start using your new cluster
without first creating a namespace.
2. kube-node-lease:
This namespace holds Lease objects associated with each node. Node leases allow
the kubelet to send heartbeats so that the control plane can detect node
failure.
3. kube-public:
This namespace is readable by all clients (including those not authenticated).
This namespace is mostly reserved for cluster usage, in case that some
resources should be visible and readable publicly throughout the whole cluster.
The public aspect of this namespace is only a convention, not a requirement.
4. kube-system:
The namespace for objects created by the Kubernetes system.


