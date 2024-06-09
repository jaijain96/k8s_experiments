# [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)

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
8. Directives from the end-user to the implementations to modify behavior or
engage non-standard features.

## [Field Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/field-selectors/)

Field selectors let us select Kubernetes objects based on the value of one or
more resource fields. Here are some examples of field selector queries:
```
metadata.name=my-service
metadata.namespace!=default
status.phase=Pending

kubectl get pods --field-selector status.phase=Running
```

Field selectors are essentially resource filters.

You can use the `=`, `==`, and `!=` operators with field selectors
(`=` and `==` mean the same thing). This kubectl command, for example, selects
all Kubernetes Services that aren't in the default namespace:
```
kubectl get services  --all-namespaces --field-selector metadata.namespace!=default
```
Set-based operators (`in`, `notin`, `exists`) are not supported for field
selectors.

**Doubt here: where to use `Label`s, where to use `Annotation`s and where to
use `Field Selector`s.**

## [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)

Finalizers are namespaced keys that tell Kubernetes to wait until specific
conditions are met before it fully deletes resources marked for deletion.
Finalizers alert controllers to clean up resources the deleted object owned.

We can use finalizers to control garbage collection of resources. For example,
we can define a finalizer to clean up related resources or infrastructure before
the controller deletes the target resource.

We can use finalizers to control garbage collection of objects by alerting
controllers to perform specific cleanup tasks before deleting the target
resource.

Finalizers don't usually specify the code to execute. Instead, they are
typically lists of keys on a specific resource similar to annotations.
Kubernetes specifies some finalizers automatically, but we can also specify our
own.

When we create a resource using a manifest file, you can specify finalizers in
the `metadata.finalizers` field. When we attempt to delete the resource, the
API server handling the delete request notices the values in the finalizers
field and does the following:
1. Modifies the object to add a `metadata.deletionTimestamp` field with the
time at which we started the deletion.
2. Prevents the object from being removed until all items are removed from its
`metadata.finalizers` field.
3. Returns a `202` status code (HTTP `Accepted`).

The `Controller` managing that `Finalizer` notices the update to the object
setting the `metadata.deletionTimestamp`, indicating deletion of the object has been requested. The `Controller` then attempts to satisfy the requirements of
the `Finalizer`s specified for that resource. Each time a `Finalizer` condition
is satisfied, the `Controller` removes that key from the resource's
`Finalizer`s field. When the `Finalizer`s field is emptied, an object with a
`deletionTimestamp` field set is automatically deleted. You can also use
`Finalizer`s to prevent deletion of unmanaged resources.

### Owner references, labels, and finalizers

Like `Label`s, `Owner` references describe the relationships between objects in
Kubernetes, but are used for a different purpose. When a `Controller` manages
objects like `Pod`s, it uses `Label`s to track changes to groups of related
objects. For example, when a `Job` creates one or more `Pod`s, the
`Job Controller` applies `Label`s to those `Pod`s and tracks changes to any
`Pod`s in the cluster with the same `Label`.

The `Job Controller` also adds `Owner` references to those `Pod`s, pointing at
the `Job` that created the `Pod`s. If we delete the `Job` while these `Pod`s
are running, Kubernetes uses the `Owner` references (not `Label`s) to determine
which `Pod`s in the cluster need cleanup.

Kubernetes also processes `Finalizer`s when it identifies `Owner` references on
a resource targeted for deletion.

In some situations, `Finalizer`s can block the deletion of `Dependent` objects,
which can cause the targeted `Owner` object to remain for longer than expected
without being fully deleted. In these situations, we should check `Finalizer`s
and `Owner` references on the target `Owner` and `Dependent` objects to
troubleshoot the cause.

## [Owners and Dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)

Ownership is different from the `Label`s and `Selector`s mechanism that some
resources also use. For example, consider a `Service` that creates
`EndpointSlice` objects. The `Service` uses `Label`s to allow the
`Control Plane` to determine which `EndpointSlice` objects are used for that
`Service`. In addition to the `Label`s, each `EndpointSlice` that is managed on
behalf of a `Service` has an `Owner` reference. `Owner` references help
different parts of Kubernetes avoid interfering with objects they don’t
control.

`Dependent` objects have a `metadata.ownerReferences` field that references
their `Owner` object. Kubernetes sets the value of this field automatically for
objects that are `Dependent`s of other objects like `ReplicaSet`s,
`DaemonSet`s, `Deployment`s, `Job`s and `CronJob`s, and
`ReplicationController`s. We can also configure these relationships manually by
changing the value of this field but we usually don't need to and can allow
Kubernetes to automatically manage the relationships.

Cross-`Namespace` `Owner` references are disallowed by design.

When we tell Kubernetes to delete a resource, the API server allows the
managing `Controller` to process any `Finalizer` rules for the resource.
`Finalizer`s prevent accidental deletion of resources our cluster may still
need to function correctly. For example, if we try to delete a
`PersistentVolume` that is still in use by a `Pod`, the deletion does not
happen immediately because the `PersistentVolume` has the
`kubernetes.io/pv-protection` `Finalizer` on it. Instead, the volume remains
in the `Terminating` status until Kubernetes clears the `Finalizer`, which
only happens after the `PersistentVolume` is no longer bound to a `Pod`.



