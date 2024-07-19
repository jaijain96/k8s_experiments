# [Workload Management](https://kubernetes.io/docs/concepts/workloads/controllers/)

K8s provides several built-in APIs for declarative management of our workloads
and the components of those workloads. Our applications run as `Container`s
inside `Pod`s; however, managing individual `Pod`s would be a lot of effort.
For example, if a `Pod` fails, we probably want to run a new `Pod` to replace
it. K8s can do that for us.

We use the K8s API to create a workload object that represents a higher
abstraction level than a `Pod`, and then the `Control Plane` automatically
manages `Pod` objects on our behalf, based on the specification for the
workload object we defined. The built-in APIs for managing workloads are:

- <mark>`Deployment`</mark> (and, indirectly, `ReplicaSet`), the most common
  way to run an application on a cluster. `Deployment` is a good fit for
  managing a stateless application workload on our cluster, where any `Pod` in
  the `Deployment` is interchangeable and can be replaced if needed.
  (`Deployments` are a replacement for the legacy `ReplicationController` API).
- A <mark>`StatefulSet`</mark> lets us manage one or more `Pod`s – all running
  the same application code – where the `Pod`s rely on having a distinct
  identity. This is different from a `Deployment` where the `Pod`s are expected
  to be interchangeable. The most common use for a `StatefulSet` is to be able
  to make a link between its `Pod`s and their persistent storage. For example,
  we can run a `StatefulSet` that associates each `Pod` with a
  `PersistentVolume`. If one of the `Pod`s in the `StatefulSet` fails,
  K8s makes a replacement `Pod` that is connected to the same
  `PersistentVolume`.
- A <mark>`DaemonSet`</mark> defines `Pod`s that provide facilities that are
  local to a specific `Node`; for example, a driver that lets `Container`s on
  that `Node` access a storage system. We use a `DaemonSet` when the driver, or
  other node-level service, has to run on the `Node` where it's useful. Each
  `Pod` in a `DaemonSet` performs a role similar to a system daemon on a
  classic Unix/POSIX server. A `DaemonSet` might be fundamental to the
  operation of a cluster, such as a plugin to let that `Node` access cluster
  networking, it might help in managing the `Node`, or it could provide less
  essential facilities that enhance the container platform running on the
  `Node`. We can run `DaemonSet`s (and their `Pod`s) across every `Node` in our
  cluster, or across just a subset (for example, only install the GPU
  accelerator driver on `Node`s that have a GPU installed).
- We can use a <mark>`Job` and/or a `CronJob`</mark> to define tasks that run
  to completion and then stop. A `Job` represents a one-off task, whereas each
  `CronJob` repeats according to a schedule.
