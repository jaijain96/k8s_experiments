# Nodes

Kubernetes runs our workload by placing `Container`s in `Pod`s that run on
`Node`s, which can be a physical or virtual machine. Each `Node` is managed by
the `Control Plane` and contains the services necessary to run `Pod`s. The
components on a `Node` include the `kubelet`, a `Container` runtime, and the
`kube-proxy`.

There are two main ways to have `Node`s added to the API server:
1. The `kubelet` on a node self-registers to the `Control Plane`.
2. We (or another human user) manually add(s) a `Node` object to the API
   server.

In either of the above cases:
1. Kubernetes creates a `Node` object internally (the representation).
2. The `Control Plane` checks whether the new `Node` object is valid, i.e, all
   necessary services to run a `Pod` are running on the `Node`.
3. If the `Node` is valid, it is eligible to run a `Pod`, else it is ignored
   from cluster activity until it becomes healthy.

## Node `name` uniqueness

The `metadata.name` field uniquely identifies a `Node`. Kubernetes also assumes
that a resource with the same `name` is the same object. In case of a `Node`,
it is implicitly assumed that an instance using the same `name` will have the
same state (e.g. network settings, root disk contents) and `attributes` like 
`Node` `Label`s. This may lead to inconsistencies if an instance was modified
without changing its name. If the `Node` needs to be replaced or updated
significantly, the existing `Node` object needs to be removed from API server
first and re-added after the update.

## Node Status

We can use `kubectl` to view a `Node`'s status and other details:
```
kubectl describe node <insert-node-name-here>
```

## `Node` `Heartbeat`s

`Heartbeat`s, sent by Kubernetes `Node`s, help our cluster determine the
availability of each `Node`, and to take action when failures are detected.

## `Node` `Controller`

The `Node` `Controller` is a Kubernetes `Control Plane` component that manages
various aspects of `Node`s:
1. Assigning a CIDR block to the `Node` when it is registered (if CIDR 
   assignment is turned on).
2. Keeping the `Node` `Controller`'s internal list of `Node`s up to date with
   the cloud provider's list of available machines. When running in a cloud environment and whenever a `Node` is unhealthy, the `Node` `Controller` asks
   the cloud provider if the VM for that `Node` is still available. If not, the
   `Node` `Controller` deletes the `Node` from its list of nodes.
3. Monitoring the `Node`s' health.
   1. In the case that a `Node` becomes unreachable, updating the `Ready`
      condition in the `Node`'s `.status` field. In this case the `Node`
      `Controller` sets the `Ready` condition to `Unknown`.
   2. If a `Node` remains unreachable: triggering API-initiated eviction for
      all of the `Pod`s on the unreachable `Node`. By default, the `Node`
      `Controller` waits 5 minutes between marking the `Node` as `Unknown`
      and submitting the first eviction request.

## Resource Capacity tracking

`Node` objects track information about the `Node`'s resource capacity: for
example, the amount of memory available and the number of CPUs. The Kubernetes
`Scheduler` ensures that there are enough resources for all the `Pod`s on a
`Node`. The `Scheduler` checks that the sum of the requests of `Container`s on
the `Node` is no greater than the `Node`'s capacity. That sum of requests
includes all `Container`s managed by the `kubelet`, but excludes any
`Container`s started directly by the `Container` runtime, and also excludes
any processes running outside of the `kubelet`'s control.

## Communication between `Node`s and the `Control Plane`

### `Node` to `Control Plane`

Kubernetes has a "hub-and-spoke" API pattern. All API usage from `Node`s
(or the `Pod`s they run) terminates at the API server. None of the other
`Control Plane` components are designed to expose remote services.
**Doubt here: Does this mean that all communication always has to go through
the API server, i.e, if 2 `Controller`s need to communicate, they have to do
so via the API server and not directly between themselves, what about the
controller and the `Container`s?**



