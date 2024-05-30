# Kubernetes Experiments

## [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)

In Kubernetes, namespaces provide a mechanism for isolating groups of resources within a single cluster. Names of resources need to be unique within a namespace, but not across namespaces. Namespace-based scoping is applicable only for namespaced objects (e.g. Deployments, Services, etc.) and not for cluster-wide objects (e.g. StorageClass, Nodes, PersistentVolumes, etc.).

Namespaces are intended for use in environments with many users spread across multiple teams, or projects.

Namespaces cannot be nested inside one another and each Kubernetes resource can only be in one namespace.

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

When we create a k8s Service, it creates a corresponding DNS entry. This entry
is of the form `<service-name>.<namespace-name>.svc.cluster.local`, which means
that if a container only uses `<service_name>` it would resolve to the service
which is local to a namespace. To reach across namespaces, we need to specify
the fully qualified domain name (FQDN).

Not all objects are in a namespace, i.e, there are objects which aren't in any
namespace. For instance, low-level resources such as `nodes` and 
`persistentVolumes` are not in any namespace. Namespace objects are themselves
not in any namespace.

To check which API resources are in a namespace (and which aren't), use:

`kubectl api-resources --namespaced=true`
`kubectl api-resources --namespaced=false` 

## [Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)

You can use Kubernetes `Annotations` to attach arbitrary non-identifying
metadata to objects. Clients such as tools and libraries can retrieve this
metadata.

`Label`s can be used to select objects and to find collections of objects that
satisfy certain conditions. In contrast, `Annotation`s are not used to identify
and select objects. The metadata in an `Annotation` can be small or large,
structured or unstructured, and can include characters not permitted by
`Label`s. It is possible to use `Label`s as well as `Annotation`s in the
metadata of the same object.

Here are some examples of information that could be recorded in annotations:
1. Fields managed by a declarative configuration layer. Attaching these fields
as annotations distinguishes them from default values set by clients or
servers, and from auto-generated fields and fields set by auto-sizing or
auto-scaling systems.
2. Build, release, or image information like timestamps, release IDs,
git branch, PR numbers, image hashes, and registry address.
3. Pointers to logging, monitoring, analytics, or audit repositories.
4. Client library or tool information that can be used for debugging purposes,
for example, name, version, and build information.
5. User or tool/system provenance information, such as URLs of related objects
from other ecosystem components.
6. Lightweight rollout tool metadata: for example, config or checkpoints.
7. Phone or pager numbers of persons responsible, or directory entries that
specify where that information can be found, such as a team web site.
8.Directives from the end-user to the implementations to modify behavior or
engage non-standard features.



