# [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)

## Voluntary and Involuntary Disruptions

We call unavoidable cases ***involuntary disruptions*** to an app. Examples:

- A hardware failure of the physical machine backing the `Node`.
- Cluster administrator deletes VM (instance) by mistake.
- Cloud provider or hypervisor failure makes VM disappear.
- A kernel panic.
- The `Node` disappears from the cluster due to cluster network partition.
- Eviction of a `Pod` due to the `Node` being out-of-resources.

We call other cases ***voluntary disruptions***. These include both actions
initiated by the application owner and those initiated by a cluster
administrator.

- Typical application owner actions include:
  - Deleting the `Deployment` or other `Controller` that manages the `Pod`.
  - Updating a `Deployment`'s `Pod` template causing a restart.
  - Directly deleting a `Pod` (e.g. by accident).
- Cluster administrator actions include:
  - Draining a `Node` for repair or upgrade.
  - Draining a `Node` from a cluster to scale the cluster down.
  - Removing a `Pod` from a `Node` to permit something else to fit on that
    `Node`.
  - Rolling out `Node` software updates.
  - Some implementations of cluster (`Node`) autoscaling may cause voluntary
    disruptions to defragment and compact `Node`s.

Not all voluntary disruptions are constrained by `Pod Disruption Budget`s. For
example, deleting `Deployment`s or `Pod`s bypasses `Pod Disruption Budget`s.

## Dealing with Disruptions

Here are some ways we can mitigate involuntary disruptions:

- Ensure our `Pod` requests the resources it needs.
- Replicate our application if we need higher availability.
- For even higher availability when running replicated applications, spread
  applications across racks (using `anti-affinity`) or across zones (if using a
  multi-zone cluster.)

Cluster administrators or hosting provider should document what level of
voluntary disruptions, if any, to expect. Certain configuration options, such
as using `PriorityClasses` in our `Pod` `spec` can also cause voluntary (and
involuntary) disruptions.

## `Pod Disruption Budget`s

As an application owner, we can create a `PodDisruptionBudget` (PDB) for each
application. <mark>A PDB limits the number of `Pod`s of a replicated
application that are down simultaneously from voluntary disruptions.</mark>
For example, a quorum-based application would like to ensure that the number
of replicas running is never brought below the number needed for a quorum.
A web frontend might want to ensure that the number of replicas serving load
never falls below a certain percentage of the total.

<mark>Cluster managers and hosting providers should use tools which respect
`PodDisruptionBudget`s by calling the Eviction API instead of directly
deleting `Pod`s or `Deployment`s.</mark> For example, the `kubectl drain`
subcommand lets us mark a `Node` as going out of service. When we run
`kubectl drain`, the tool tries to evict all of the `Pod`s on the `Node`
we're taking out of service. The eviction request that `kubectl` submits on
our behalf may be temporarily rejected, so the tool periodically retries all
failed requests until all `Pod`s on the target `Node` are terminated, or
until a configurable timeout is reached.

<mark>A PDB specifies the number of replicas that an application can tolerate
having, relative to how many it is intended to have.</mark> For example, a
`Deployment` which has a `.spec.replicas: 5` is supposed to have 5 `Pod`s at
any given time. If its PDB allows for there to be 4 at a time, then the
Eviction API will allow voluntary disruption of one (but not two) `Pod`s at
a time.

<mark>The "intended" number of `Pod`s is computed from the `.spec.replicas`
of the `Workload` resource that is managing those `Pod`s.</mark> The
`Control Plane` discovers the owning `Workload` resource by examining the
`.metadata.ownerReferences` of the `Pod`.

<mark>Involuntary disruptions cannot be prevented by PDBs; however they do count
against the budget.</mark>

<mark>`Pod`s which are deleted or unavailable due to a rolling upgrade to an
application do count against the disruption budget, but `Workload` resources
(such as `Deployment` and `StatefulSet`) are not limited by PDBs when doing
rolling upgrades. Instead, the handling of failures during application updates
is configured in the `spec` for the specific `Workload` resource.</mark>

It is recommended to set `AlwaysAllow` Unhealthy Pod Eviction Policy to
`PodDisruptionBudget`s to support eviction of misbehaving applications
during a `Node` drain. The default behavior is to wait for the application
`Pod`s to become healthy before the drain can proceed.

When a `Pod` is evicted using the eviction API, it is gracefully terminated,
honoring the `terminationGracePeriodSeconds` setting in its `PodSpec`.

## `PodDisruptionBudget` Example

Consider a cluster with 3 `Node`s, node-1 through node-3. The cluster is
running several applications. One of them has 3 replicas initially called
pod-a, pod-b, and pod-c. Another, unrelated `Pod` without a PDB, called pod-x,
is also shown. Initially, the `Pod`s are laid out as follows:

|      node-1       |      node-2       |      node-3       |
|-------------------|-------------------|-------------------|
| pod-a *available* | pod-b *available* | pod-c *available* |
| pod-x *available* |                   |                   |

All 3 `Pod`s are part of a `Deployment`, and they collectively have a PDB which
requires there be at least 2 of the 3 `Pod`s to be available at all times.

Assume the cluster administrator wants to reboot into a new kernel version to
fix a bug in the kernel. The cluster administrator first tries to drain node-1
using the `kubectl drain` command. That tool tries to evict pod-a and pod-x.
This succeeds immediately. Both `Pod`s go into the terminating state at the
same time. This puts the cluster in this state:

|       node-1        |      node-2       |      node-3       |
|---------------------|-------------------|-------------------|
| pod-a *terminating* | pod-b *available* | pod-c *available* |
| pod-x *terminating* |                   |                   |

The `Deployment` notices that one of the `Pod`s is terminating, so it creates a
replacement called pod-d. Since node-1 is cordoned, it lands on another `Node`.
Assume something has also created pod-y as a replacement for pod-x.

For a `StatefulSet`, pod-a would need to terminate completely before its
replacement, which is also called pod-a but has a different UID, could be
created. Otherwise, the example applies to a `StatefulSet` as well.

Now the cluster is in this state:

|       node-1        |      node-2       |      node-3       |
|---------------------|-------------------|-------------------|
| pod-a *terminating* | pod-b *available* | pod-c *available* |
| pod-x *terminating* | pod-d *starting*  | pod-y             |

At some point, the pods terminate, and the cluster looks like this:

| node-1 *drained* |      node-2       |      node-3       |
|------------------|-------------------|-------------------|
|                  | pod-b *available* | pod-c *available* |
|                  | pod-d *starting*  | pod-y             |

At this point, if a cluster administrator tries to drain node-2 or node-3, the
drain command will block, because there are only 2 available `Pod`s for the
`Deployment`, and its PDB requires at least 2. After some time passes, pod-d
becomes available.

The cluster state now looks like this:

| node-1 *drained* |      node-2       |      node-3       |
|------------------|-------------------|-------------------|
|                  | pod-b *available* | pod-c *available* |
|                  | pod-d *available* | pod-y             |

Now, the cluster administrator tries to drain node-2. The drain command will
try to evict the two `Pod`s in some order, say pod-b first and then pod-d. It
will succeed at evicting pod-b. But, when it tries to evict pod-d, it will be
refused because that would leave only one `Pod` available for the `Deployment`.

The `Deployment` creates a replacement for pod-b called pod-e. Because there
are not enough resources in the cluster to schedule pod-e the drain will again
block. The cluster may end up in this state:

| node-1 *drained* |       node-2        |      node-3       |     *no node*    |
|------------------|---------------------|-------------------|------------------|
|                  | pod-b *terminating* | pod-c *available* |  pod-e *pending* |
|                  | pod-d *available*   | pod-y             |                  |

At this point, the cluster administrator needs to add a `Node` back to the
cluster to proceed with the upgrade.

<mark>We can see how K8s varies the rate at which disruptions can happen, according
to:</mark>

- <mark>How many replicas an application needs.</mark>
- <mark>How long it takes to gracefully shutdown an instance.</mark>
- <mark>How long it takes a new instance to start up.</mark>
- <mark>The type of controller.</mark>
- <mark>The cluster's resource capacity.</mark>

## Pod Disruption Conditions

When the `PodDisruptionConditions` feature gate is enabled in our cluster, a
dedicated Pod `DisruptionTarget` condition is added to indicate that the `Pod`
is about to be deleted due to a disruption. The reason field of the condition
additionally indicates one of the following reasons for the `Pod` termination:

- `PreemptionByScheduler`: `Pod` is due to be preempted by a scheduler in order
  to accommodate a new `Pod` with a higher priority based on
  [Pod priority preemption](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/).
- `DeletionByTaintManager`: `Pod` is due to be deleted by Taint Manager (which
  is part of the `Node` lifecycle controller within `kube-controller-manager`)
  due to a `NoExecute` taint that the `Pod` does not tolerate.
- `EvictionByEvictionAPI`: `Pod` has been marked for eviction using the K8s
  API.
- `DeletionByPodGC`: `Pod`, that is bound to a no longer existing `Node`, is
  due to be deleted by `Pod` garbage collection.
- `TerminationByKubelet`: `Pod` has been terminated by the `kubelet`, because
  of either `Node` pressure eviction or the graceful node shutdown.

A `Pod` disruption might be interrupted. The `Control Plane` might re-attempt
to continue the disruption of the same `Pod`, but it is not guaranteed. As a
result, the `DisruptionTarget` condition might be added to a `Pod`, but that
`Pod` might then not actually be deleted. In such a situation, after some time,
the `Pod` disruption condition will be cleared.

When using a `Job` (or `CronJob`), we may use these `Pod` disruption conditions
as part of our `Job`'s `Pod` `failurePolicy`.

## Separating Cluster Owner and Application Owner Roles

<mark>It is useful to think of the cluster manager and application owner as
separate roles with limited knowledge of each other. This separation of
responsibilities may make sense in these scenarios:</mark>

- <mark>when there are many application teams sharing a K8s cluster, and there is
  natural specialization of roles.</mark>
- <mark>when third-party tools or services are used to automate cluster management.</mark>

`PodDisruptionBudget`s support this separation of roles by providing an
interface between the roles.

## How to Perform Disruptive Actions on our Cluster

<mark>If we need to perform a disruptive action on ALL the `Node`s in our
cluster, such as a `Node` or system software upgrade, here are some
options:</mark>

- Accept downtime during the upgrade.
- Failover to another complete replica cluster.
  - No downtime, but may be costly both for the duplicated `Nodes` and for
    human effort to orchestrate the switchover.
- <mark>Write disruption tolerant applications and use PDBs.</mark>
  - No downtime.
  - Minimal resource duplication.
  - Allows more automation of cluster administration.
  - <mark>Writing disruption-tolerant applications is tricky, but the work to
    tolerate voluntary disruptions largely overlaps with work to support
    autoscaling and tolerating involuntary disruptions.</mark>
