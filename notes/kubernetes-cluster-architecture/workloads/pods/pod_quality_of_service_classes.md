# [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)

K8s assigns a QoS class to each `Pod` as a consequence of the resource
constraints that we specify for the `Container`s in that `Pod`. K8s relies on
this classification to make decisions about which `Pod`s to evict when there
aren't enough available resources on a `Node`, i.e, `Node`s experiencing
[Node Pressure](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/).

## Quality of Service Classes

K8s does QoS classification of a `Pod` based on the resource `request`s of the
component `Container`s in that `Pod`, along with how those `request`s relate to
resource `limit`s. The possible QoS classes are `Guaranteed`, `Burstable`, and
`BestEffort`. When a `Node` runs out of resources, K8s will first evict
`BestEffort` `Pod`s running on that `Node`, followed by `Burstable` and finally
`Guaranteed` `Pod`s. When this eviction is due to resource pressure, only
`Pod`s exceeding resource requests are candidates for eviction.

### `Guaranteed`

`Pod`s that are `Guaranteed` have the strictest resource `limit`s and are least
likely to face eviction. They are guaranteed not to be killed until they exceed
their `limit`s or there are no lower-priority `Pod`s that can be preempted from
the `Node`. They may not acquire resources beyond their specified `limit`s.
These `Pod`s can also make use of exclusive CPUs using the [`static`](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/#static-policy) CPU management policy.

Detailed [criteria](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#criteria) for `Guaranteed` QoS.

### `Burstable`

`Pod`s that are `Burstable` have some lower-bound resource guarantees based on
the `request`, but do not require a specific `limit`. If a `limit` is not
specified, it defaults to a `limit` equivalent to the capacity of the `Node`,
which allows the `Pod`s to flexibly increase their resources if resources are
available. In the event of `Pod` eviction due to `Node` resource pressure,
these `Pod`s are evicted only after all `BestEffort` `Pod`s are evicted.
Because a `Burstable` `Pod` can include a `Container` that has no resource
`limit`s or `request`s, a `Pod` that is `Burstable` can try to use any amount
of `Node` resources.

Detailed [criteria](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#criteria-1) for `Burstable` QoS.

### `BestEffort`

`Pod`s in the `BestEffort` QoS class can use `Node` resources that aren't
specifically assigned to `Pod`s in other QoS classes. For example, if we have
a `Node` with 16 CPU cores available to the `kubelet`, and we assign 4 CPU
cores to a `Guaranteed` `Pod`, then a `Pod` in the `BestEffort` QoS class can
try to use any amount of the remaining 12 CPU cores.

The `kubelet` prefers to evict `BestEffort` `Pod`s if the `Node` comes under
resource pressure.

Detailed [criteria](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/#criteria-2) for `BestEffort` QoS.

## Memory QoS with cgroupv2

Memory QoS uses the memory `Controller` of cgroup v2 to guarantee memory
resources in K8s. Memory `request`s and `limit`s of `Container`s in a `Pod` are
used to set specific interfaces, `memory.min` and `memory.high` provided by the
memory `Controller`.

- When `memory.min` is set to memory `request`s, memory resources are reserved
  and never reclaimed by the kernel, ensuring memory availability for K8s
  `Pod`s.
- If memory `limit`s are set in the `Container`, this means that the system
  needs to limit `Container` memory usage; Memory QoS uses `memory.high` to
  throttle workload approaching its memory `limit`, ensuring that the system is
  not overwhelmed by instantaneous memory allocation.

Memory QoS relies on QoS class to determine which settings to apply; however,
these are different mechanisms that both provide controls over quality of
service.

## Some Behavior is Independent of QoS Class

- Any `Container` exceeding a resource `limit` will be killed and restarted by
  the `kubelet` without affecting other `Container`s in that `Pod`.
- If a `Container` exceeds its resource `request` and the `Node` it runs on
  faces resource pressure, the `Pod` it is in becomes a candidate for eviction.
  If this occurs, all `Container`s in the `Pod` will be terminated. K8s may
  create a replacement `Pod`, usually on a different `Node`.
- The resource `request` of a `Pod` is equal to the sum of the resource
  `request`s of its component `Container`s, and the resource `limit` of a `Pod`
  is equal to the sum of the resource `limit`s of its component `Container`s.
- The `kube-scheduler` does not consider QoS class when selecting which
  `Pod`s to
  [preempt](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/#preemption).
  Preemption can occur when a cluster does not have enough resources to run
  all the `Pod`s we defined.
