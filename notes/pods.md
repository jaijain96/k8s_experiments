# [`Pod`s](https://kubernetes.io/docs/concepts/workloads/pods/)

`Pod`s are the smallest deployable units of computing that we can create and
manage in Kubernetes. A `Pod` is a group of one or more `Container`s, with
shared storage and network resources, and a specification for how to run the
`Container`s. A `Pod`'s contents are always co-located and co-scheduled, and
run in a shared context. A `Pod` models an application-specific
"logical host": it contains one or more application `Container`s which are
relatively tightly coupled. In non-cloud contexts, applications executed on the
same physical or virtual machine are analogous to cloud applications executed
on the same logical host.

## [What is a `Pod`](https://kubernetes.io/docs/concepts/workloads/pods/#what-is-a-pod)

We need to install a `Container` runtime into each `Node` in the cluster so
that `Pod`s can run there. The shared context of a `Pod` is a set of Linux
`namespace`s, `cgroup`s, and potentially other facets of isolation - the same
things that isolate a `Container`. Within a `Pod`'s context, the individual
applications may have further sub-isolations applied.

A `Pod` is similar to a set of `Container`s with shared `Namespace`s and shared
filesystem volumes.

`Pod`s in a Kubernetes cluster are used in two main ways:

1. `Pod`s that run a single container: The "one-container-per-Pod" model is the
   most common Kubernetes use case; we can think of a `Pod` as a wrapper around
   a single `Container`; Kubernetes manages `Pod`s rather than managing the
   containers directly.
2. `Pod`s that run multiple `Container`s that need to work together. A `Pod`
   can encapsulate an application composed of multiple co-located `Container`s
   that are tightly coupled and need to share resources. These co-located
   containers form a single cohesive unit.

Usually we don't need to create `Pod`s directly, even singleton `Pod`s. Instead,
we create them using `Workload` resources such as `Deployment` or `Job`. If our
`Pod`s need to track state, we can use the `StatefulSet` resource. `Pod`s are
designed as relatively ephemeral, disposable entities. When a `Pod` gets
created (directly by us, or indirectly by a `Controller`), the new `Pod` is
scheduled to run on a `Node` in your cluster. The `Pod` remains on that `Node`
until the `Pod` finishes execution, the `Pod` object is deleted, the `Pod` is
evicted for lack of resources, or the `Node` fails. Restarting a `Container` in
a `Pod` should not be confused with restarting a `Pod`. <mark> A `Pod` is not a
process, but an environment for running `Container`(s)</mark>. A `Pod` persists until it is deleted.

A `Controller` for the resource handles replication and rollout and automatic
healing in case of `Pod` failure. For example, if a `Node` fails, a
`Controller` notices that `Pod`s on that `Node` have stopped working and
creates a replacement `Pod`. The `Scheduler` places the replacement `Pod` onto
a healthy `Node`.

## [`Pod` Templates](https://kubernetes.io/docs/concepts/workloads/pods/#pod-templates)

`Controller`s for `Workload` resources create `Pod`s from a `Pod` template and
manage those `Pod`s on our behalf. Each `Controller` for a `Workload` resource
uses the `PodTemplate` inside the `Workload` object to make actual `Pod`s. The
`PodTemplate` is part of the desired state of whatever `Workload` resource we
use to run our app.

Modifying the `Pod` template or switching to a new `Pod` template has no direct
effect on the `Pod`s that already exist. If we change the `Pod` template for a
`Workload` resource, that resource needs to create replacement `Pod`s that use
the updated template. On `Node`s, the `kubelet` doesn't directly observe or
manage any of the details around `Pod` templates and updates.

Kubernetes doesn't prevent us from managing `Pod`s directly, albeit, with some
limitations, as mentioned [here](https://kubernetes.io/docs/concepts/workloads/pods/#pod-update-and-replacement).

## [Resource sharing and communication](https://kubernetes.io/docs/concepts/workloads/pods/#resource-sharing-and-communication)

`Pod`s enable data sharing and communication among their constituent
`Container`s.

**Storage**: A `Pod` can specify a set of shared storage `Volume`s. All
`Container`s in the `Pod` can access the shared `Volume`s, allowing those
`Container`s to share data. `Volume`s also allow persistent data in a `Pod` to
survive in case one of the `Container`s within needs to be restarted.

**Networking**: Each `Pod` is assigned a unique IP address for each address
family. Every `Container` in a `Pod` shares the network namespace, including
the IP address and network ports. Inside a `Pod` (and **only** then), the
`Container`s that belong to the `Pod` can communicate with one another using
`localhost`. When `Container`s in a `Pod` communicate with entities outside the
`Pod`, they must coordinate how they use the shared network resources (such as
ports). Within a `Pod`, `Container`s share an IP address and port space, and
can find each other via `localhost`. The `Container`s in a `Pod` can also
communicate with each other using standard inter-process communications like
SystemV semaphores or POSIX shared memory. `Container`s in different `Pod`s
have distinct IP addresses and can not communicate by OS-level IPC without
special configuration. `Container`s that want to interact with a `Container`
running in a different `Pod` can use IP networking to communicate. `Container`s
within the `Pod` see the system hostname as being the same as the configured
`name` for the `Pod`.

## [`Container` probes](https://kubernetes.io/docs/concepts/workloads/pods/#container-probes)

A probe is a diagnostic performed periodically by the `kubelet` on a
`Container`. To perform a diagnostic, the `kubelet` can invoke different
actions:

1. `ExecAction` (performed with the help of the `Container` runtime)
2. `TCPSocketAction` (checked directly by the `kubelet`)
3. `HTTPGetAction` (checked directly by the `kubelet`)
