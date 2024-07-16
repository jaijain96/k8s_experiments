# [`Pod` Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

`Pod`s follow a defined lifecycle, starting in the `Pending` phase, moving
through `Running` if at least one of its primary `Container`s starts `OK`, and
then through either the `Succeeded` or `Failed` phases depending on whether any
`Container` in the `Pod` terminated in failure.

Like individual application `Container`s, `Pod`s are considered to be
relatively ephemeral entities. `Pod`s are created, assigned a unique ID (UID),
and scheduled to run on `Node`s where they remain until termination (according
to restart policy) or deletion. If a `Node` dies, the `Pod`s running on (or
scheduled to run on) that `Node` are marked for deletion. The `Control Plane`
marks the `Pod`s for removal after a timeout period.

## `Pod` lifetime

Whilst a `Pod` is running, the `kubelet` is able to restart `Container`s to
handle some kind of faults. Within a `Pod`, Kubernetes tracks different
`Container` states and determines what action to take to make the `Pod` healthy
again.

`Pod`s have both a specification and an actual status. The status for a `Pod`
object consists of a set of `Pod` conditions. We can also inject custom
readiness information into the condition data for a `Pod`, if that is useful to
our application.

`Pod`s are only scheduled once in their lifetime; assigning a `Pod` to a
specific `Node` is called *binding*, and the process of selecting which `Node` to use is called *scheduling*. Once a `Pod` has been scheduled and is bound to
a `Node`, Kubernetes tries to run that `Pod` on the `Node`. The `Pod` runs on
that `Node` until it stops, or until the `Pod` is terminated; if Kubernetes
isn't able start the `Pod` on the selected `Node` (for example, if the `Node`
crashes before the `Pod` starts), then that particular `Pod` never starts.

### `Pod`s and fault recovery

If one of the `Container`s in the `Pod` fails, then Kubernetes may try to
restart that specific `Container`. `Pod`s can however fail in a way that the
cluster cannot recover from, and in that case Kubernetes does not attempt to
heal the `Pod` further; instead, Kubernetes deletes the `Pod` and relies on
other components to provide automatic healing.

If a `Pod` is scheduled to a `Node` and that `Node` then fails, the `Pod` is
treated as unhealthy and Kubernetes eventually deletes the `Pod`. A `Pod` won't
survive an eviction due to a lack of resources or `Node` maintenance.
Kubernetes uses a higher-level abstraction, called a `Controller`, that handles
the work of managing the relatively disposable `Pod` instances.

A given `Pod` (as defined by a UID) is never "rescheduled" to a different
`Node`; instead, that `Pod` can be replaced by a new, near-identical `Pod`. If
we make a replacement `Pod`, it can even have same name (as in
`.metadata.name`) that the old `Pod` had, but the replacement would have a
different `.metadata.uid` from the old `Pod`. Kubernetes does not guarantee
that a replacement for an existing `Pod` would be scheduled to the same `Node`
as the old `Pod` that was being replaced.

### Associated lifetimes

When something is said to have the same lifetime as a `Pod`, such as a
`volume`, that means that the thing exists as long as that specific `Pod` (with
that exact UID) exists. If that `Pod` is deleted for any reason, and even if an
identical replacement is created, the related thing (a `volume`, in this
example) is also destroyed and created anew.

## `Pod` phase

A `Pod`'s `status` field is a `PodStatus` object, which has a `phase` field.

The `phase` of a `Pod` is a simple, high-level summary of where the `Pod` is in
its lifecycle. The `phase` is not intended to be a comprehensive rollup of
observations of `Container` or `Pod` state, nor is it intended to be a
comprehensive state machine. **The number and meanings of `Pod` `phase` values
are tightly guarded**. Other than what is documented [here](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase), nothing should be
assumed about `Pod`s that have a given `phase` value.

If a `Node` dies or is disconnected from the rest of the cluster, Kubernetes
applies a policy for setting the `phase` of all `Pod`s on the lost `Node` to
`Failed`.

## `Container` States

As well as the `phase` of the `Pod` overall, Kubernetes tracks the `state` of
each `Container` inside a `Pod`. Once the `scheduler` assigns a `Pod` to a
`Node`, the `kubelet` starts creating `Container`s for that `Pod` using a
`Container` runtime. There are three possible `Container` `state`s: `Waiting`,
`Running`, and `Terminated`. To check the state of a `Pod`'s `Container`s, you
can use:

```bash
kubectl describe pod <name-of-pod>
```

The output shows the `state` for each `Container` within that `Pod`. Each
`state` has a specific meaning:

1. Waiting: 
