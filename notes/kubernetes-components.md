# [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)

![](images/components-of-kubernetes.svg)

We deploy Kubernetes on a set of interconnected machines (or virtual
machines), on doing so, we get a cluster.

A Kubernetes cluster consists of a set of worker machines, called `Node`s,
that run containerized applications. Every cluster has at least one worker
`Node`.

The worker `Node` hosts the `Pod`s that are the components of the application
workload. The `Control Plane` manages the worker `Node`s and the `Pod`s in the
cluster. In production environments, the `Control Plane` usually runs across
multiple computers and a cluster usually runs multiple `Node`s, providing
fault-tolerance and high availability.

## Control Plane Components

The `Control Plane`'s components make global decisions about the cluster
(for example, scheduling), as well as detecting and responding to cluster
events (for example, starting up a new `Pod` when a `Deployment`'s `replicas`
field is unsatisfied).

`Control Plane` components can be run on any machine in the cluster and span
multiple machines in the cluster. **Doubt here: is the control plane also
running as a container? are their different components in the control plane
that run on separate containers deployed on various nodes in the cluster?**

### kube-apiserver

The API server is a component of the Kubernetes control plane that exposes the
Kubernetes API. The API server is the frontend for the Kubernetes control
plane.

The main implementation of a Kubernetes API server is `kube-apiserver`.
`kube-apiserver` is designed to scale horizontally — that is, it scales by
deploying more instances. We can run several instances of `kube-apiserver` and
balance traffic between those instances. **Doubt here: Again, do the
instances mentioned here mean containers?**

### etcd

`etcd` is a consistent and highly-available key value store used as
Kubernetes' backing store for all cluster data.

If our Kubernetes cluster uses etcd as its backing store, we need to make sure
we have a back up plan for the data. Why? As stated above, `etcd` is
consistent and highly avaialable, which according to CAP theorem, makes it
non-partition tolerant. Therefore, we need a backup plan for `etcd` data, to
save us in case of system faults.

### kube-scheduler

`Control Plane` component that watches for newly created `Pod`s with no
assigned `Node`, and selects a `Node` for them to run on.

### kube-controller-manager

`Control Plane` component that runs `Controller` processes. Logically, each
`Controller` is a separate process, but to reduce complexity, they are all
compiled into a single binary and run in a single process.

There are many different types of `Controller`s. Some examples of them are:
1. `Node` `Controller`: Responsible for noticing and responding when nodes go
   down.
2. `Job` `Controller`: Watches for `Job` objects that represent one-off tasks,
   then creates `Pod`s to run those tasks to completion.
3. `EndpointSlice` `Controller`: Populates `EndpointSlice` objects (to provide a
   link between `Service`s and `Pod`s).
4. `ServiceAccount Controller`: Create default `ServiceAccounts` for new
   `Namespace`s.

The above is not an exhaustive list.

### `cloud-controller-manager`

This `Contol Plane` component embeds cloud-specific control logic, by helping
us link our cluster into our cloud provider's API and separates out the
components that interact with that cloud platform from components that only
interact with our cluster. This `Controller` only runs `Controller`s that are
specific to our cloud provider and if we are running a cluster on our
on-premise cluster or any environment other than a cloud provider, the
`cloud-controller-manager` will not be present in our cluster.

The following `Controller`s can have cloud provider dependencies:
1. `Node` `Controller`: For checking the cloud provider to determine if a `Node`
   has been deleted in the cloud after it stops responding.
2. `Route` `Controller`: For setting up routes in the underlying cloud
   infrastructure.
3. `Service` `Controller`: For creating, updating and deleting cloud provider
   load balancers.

Refer the [`cloud-controller-manager`](https://kubernetes.io/docs/concepts/architecture/cloud-controller/) doc for more info.

## `Node` Components

`Node` components run on every `Node`, maintaining running `Pod`s and providing
the Kubernetes runtime environment.

### `kubelet`

Runs on each `Node` in the cluster, it makes sure that `Container`s are running
in a `Pod`.

The `kubelet` takes a set of `PodSpec`s that are provided through various
mechanisms and ensures that the `Container`s described in those `PodSpec`s are
running and healthy. The `kubelet` doesn't manage `Container`s which were not
created by Kubernetes.

### `kube-proxy`

`kube-proxy` is a network proxy that runs on each `Node` in our cluster,
implementing part of the Kubernetes `Service` concept.

`kube-proxy` maintains network rules on `Node`s. These network rules allow
network communication to our `Pod`s from network sessions inside or outside
of our cluster.

### `Container` Runtime

A fundamental component that empowers Kubernetes to run `Container`s
effectively. It is responsible for managing the execution and lifecycle of
`Container`s within the Kubernetes environment.

Kubernetes supports `Container` runtimes such as `containerd`, `CRI-O`, and any
other implementation of the Kubernetes CRI (`Container` Runtime Interface).

Refer the [`Container` Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/) doc for more info.

## Addons

Addons use Kubernetes resources (`DaemonSet`, `Deployment`, etc.) to implement
cluster features. Because these are providing cluster-level features,
`Namespace`d resources for addons belong within the `kube-system` `Namespace`.

### DNS

While the other addons are not strictly required, all Kubernetes clusters
should have `Cluster DNS`, as many examples rely on it. `Cluster DNS` is a DNS
server, in addition to the other DNS server(s) in your environment, which
serves DNS records for Kubernetes services. `Container`s started by Kubernetes
automatically include this DNS server in their DNS searches.
**Doubt here: how is the `Cluster DNS` service implemented? Is it also running
as a `Container` in a `Pod`? Are these deployed on various `Node`s in the
cluster?**

### Web UI (Dashboard)

Dashboard is a web-based UI that allows users to manage and troubleshoot
applications running in the cluster, as well as the cluster itself.

### `Container` Resource Monitoring

`Container` Resource Monitoring records generic time-series metrics about
`Container`s in a central database, and provides a UI for browsing that data.

### Cluster-level Logging

A cluster-level logging mechanism is responsible for saving `Container` logs to
a central log store with search/browsing interface.

### Network Plugins

Network plugins are software components that implement the `Container` network
interface (CNI) specification. They are responsible for allocating IP
addresses to `Pod`s and enabling them to communicate with each other within the
cluster.

