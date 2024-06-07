# Kubernetes Components

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

If out Kubernetes cluster uses etcd as its backing store, we need to make sure
we have a back up plan for the data. Why? As stated above, `etcd` is
consistent and highly avaialable, which according to CAP theorem, makes it
non-partition tolerant. Therefore, we need a backup plan for `etcd` data, to
save us in case of system faults.
