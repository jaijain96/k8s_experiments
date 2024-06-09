# [`Node`s](https://kubernetes.io/docs/concepts/architecture/nodes/)

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

## [Communication between `Node`s and the `Control Plane`](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)

### `Node` to `Control Plane`

Kubernetes has a "hub-and-spoke" API pattern. All API usage from `Node`s
(or the `Pod`s they run) terminates at the API server. None of the other
`Control Plane` components are designed to expose remote services.
**Doubt here: Does this mean that all communication always has to go through
the API server, i.e, if 2 `Controller`s need to communicate, they have to do
so via the API server and not directly between themselves, what about the
controller and the `Container`s?**

The `Node`s and the `Pod`s within those use TLS to communicate with the API
server and as such, the default operating mode for connections from the
`Node`s and `Pod`s running on the them to the `Control Plane` is secured by
default and can run over untrusted and/or public networks. There would be some
configuration needed, checkout the official [doc](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/#node-to-control-plane) for this section to get more info.

### `Contol Plane` to `Node`

There are two primary communication paths from the `Control Plane` (the 
API server) to the `Node`s:
1. From the API server to the `kubelet` process which runs on each `Node` in
   the cluster.
2. From the API server to any `Node`, `Pod`, or `Service` through the API
   server's proxy functionality.

#### API Server to `kubelet`

The connections from the API server to the `kubelet` are used for:
1. Fetching logs for `Pod`s.
2. Attaching (usually through `kubectl`) to running `Pod`s.
3. Providing the `kubelet`'s port-forwarding functionality.

These connections terminate at the `kubelet`'s HTTPS endpoint. By default, the
API server does not verify the `kubelet`'s serving certificate, which makes the
connection subject to man-in-the-middle attacks and unsafe to run over
untrusted and/or public networks. However, we can configure these connections
to be secure, checkout the official [doc](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/#control-plane-to-node) for this section to get more info.

#### API server to `Node`s, `Pod`s, and `Service`s

The connections from the API server to a `Node`, `Pod`, or `Service` default
to plain HTTP connections and are therefore neither authenticated nor
encrypted. They can be run over a secure HTTPS connection by prefixing
`https:` to the `Node`, `Pod`, or `Service` name in the API URL, but they will
not validate the certificate provided by the HTTPS endpoint nor provide client
credentials. So while the connection will be encrypted, it will not provide any
guarantees of integrity. These connections are not currently safe to run over
untrusted or public networks.

These connections can be made secure using [SSH Tunneling](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/#ssh-tunnels)
(deprecated) or via the [Konnectivity service](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/#konnectivity-service), refer the
official docs for more info.

