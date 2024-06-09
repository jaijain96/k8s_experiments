# [`Workload`s](https://kubernetes.io/docs/concepts/workloads/)

A `Workload` is an application running on Kubernetes, inside a set of `Pod`s.
`Pod`s have a defined lifecycle. For example, once a `Pod` is running in
our cluster then a critical fault on the `Node` where that `Pod` is running
means that all the `Pod`s on that `Node` fail. Kubernetes treats that level of
failure as final: we would need to create a new `Pod` to recover, even if the
`Node` later becomes healthy.

To make life easier, we don't need to manage each `Pod` directly. Instead, we
use `Workload` resources that manage a set of `Pod`s. These resources configure
`Controller`s that make sure the right number of the right kind of `Pod` are
running, to match the state we specified. Kubernetes provides several built-in
`Workload` resources:
1. `Deployment` and `ReplicaSet` (replacing the legacy resource
   `ReplicationController`): `Deployment` is a good fit for managing a
   stateless application workload on our cluster, where any `Pod` in the
   `Deployment` is interchangeable and can be replaced if needed.
2. `StatefulSet`: lets us run one or more related `Pod`s that do track state
   somehow. For example, if our workload records data persistently, we can run
   a `StatefulSet` that matches each `Pod` with a `PersistentVolume`. Our code,
   running in the `Pod`s for that `StatefulSet`, can replicate data to other
   `Pod`s in the same `StatefulSet` to improve overall resilience.
3. `DaemonSet`: defines `Pod`s that provide facilities that are local to
   `Node`s. Every time we add a `Node` to our cluster that matches the
   specification in a `DaemonSet`, the `Control Plane` schedules a `Pod` for
   that `DaemonSet` onto the new `Node`. Each `Pod` in a `DaemonSet` performs a
   job similar to a system daemon on a classic Unix / POSIX server. A
   `DaemonSet` might be fundamental to the operation of our cluster, such as a
   plugin to run cluster networking, it might help us to manage the `Node`, or
   it could provide optional behavior that enhances the `Container` platform
   we are running.
4. `Job` and `CronJob` provide different ways to define tasks that run to
   completion and then stop. We can use a `Job` to define a task that runs to
   completion, just once. We can use a `CronJob` to run the same `Job` multiple
   times according a schedule.

