# [`Deployment`s](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

A `Deployment` provides declarative updates for `Pod`s and `ReplicaSet`s. We
describe a desired state in a `Deployment`, and the `Deployment` `Controller`
changes the actual state to the desired state at a controlled rate. We can
define `Deployment`s to create new `ReplicaSet`s, or to remove existing
`Deployment`s and adopt all their resources with new `Deployment`s. It isn't
advisable to manually manage `ReplicaSet`s owned by a `Deployment`.

## Use Cases

The following are typical use cases for `Deployment`s:

- Create a `Deployment` to rollout a `ReplicaSet`. The `ReplicaSet` creates
  `Pod`s in the background. Check the status of the rollout to see if it
  succeeds or not.
- Declare the new state of the `Pod`s by updating the `PodTemplateSpec` of the
  `Deployment`. A new `ReplicaSet` is created and the `Deployment` manages
  moving the `Pod`s from the old `ReplicaSet` to the new one at a controlled
  rate. Each new `ReplicaSet` updates the revision of the `Deployment`.
- Rollback to an earlier `Deployment` revision if the current state of the
  `Deployment` is not stable. Each rollback updates the revision of the
  `Deployment`.
- Scale up the `Deployment` to facilitate more load.
- Pause the rollout of a `Deployment` to apply multiple fixes to its
  `PodTemplateSpec` and then resume it to start a new rollout.
- Use the status of the `Deployment` as an indicator that a rollout has stuck.
- Clean up older `ReplicaSet`s that aren't needed anymore.

## Writing a `Deployment` `Spec`

As with all other K8s configs, a `Deployment` needs `.apiVersion`, `.kind`, and
`.metadata` fields. When the `Control Plane` creates new `Pod`s for a
`Deployment`, the `.metadata.name` of the `Deployment` is part of the basis for
naming those `Pod`s. The name of a `Deployment` must be a valid DNS subdomain
value, but this can produce unexpected results for the `Pod` hostnames. For
best compatibility, the name should follow the more restrictive rules for a DNS
label. A `Deployment` also needs a `.spec` section.

### `Pod` Template

The `.spec.template` and `.spec.selector` are the only required fields of the
`.spec`.

The `.spec.template` is a `Pod` template. It has exactly the same schema as a
`Pod`, except it is nested and does not have an `apiVersion` or `kind`. In
addition to required fields for a `Pod`, a `Pod` template in a `Deployment`
must specify appropriate `Label`s and an appropriate `restartPolicy`. `Label`s
shouln't overlap with other `Controller`s.

Only a `.spec.template.spec.restartPolicy` equal to `Always` is allowed, which
is the default if not specified.

### Replicas

`.spec.replicas` is an optional field that specifies the number of desired
`Pod`s, it defaults to 1. If a `HorizontalPodAutoscaler` (or any similar API
for horizontal scaling) is managing scaling for a `Deployment`, we don't set
`.spec.replicas`, thereby, allowing the `Control Plane` to manage the
`.spec.replicas` field automatically.

### Selector

`.spec.selector` is a required field that specifies a `Label` selector for the
`Pod`s targeted by this `Deployment`. `.spec.selector` must match
`.spec.template.metadata.labels`, or it will be rejected by the API. In API
version `apps/v1`, `.spec.selector` and `.metadata.labels` do not default to
`.spec.template.metadata.labels` if not set and must be set explicitly. Note
that `.spec.selector` is immutable after creation of the `Deployment` in
`apps/v1`.

A `Deployment` may terminate `Pod`s whose `Label`s match the selector if their
template is different from `.spec.template` or if the total number of such
`Pod`s exceeds `.spec.replicas`. It brings up new `Pod`s with `.spec.template`
if the number of `Pod`s is less than the desired number. We shouldn't create
other `Pod`s whose `Label`s match this selector, either directly, by creating
another `Deployment`, or by creating another `Controller` such as a
`ReplicaSet` or a `ReplicationController`. If we do so, the first `Deployment`
thinks that it created these other `Pod`s. K8s does not stop us from doing this.
Similarly, if we have multiple `Controller`s that have overlapping selectors, the `Controller`s will fight with each other and won't behave correctly.

### Strategy

`.spec.strategy` specifies the strategy used to replace old `Pod`s by new
ones. `.spec.strategy.type` can be `Recreate` or `RollingUpdate` (default).

#### Recreate `Deployment`

All existing `Pod`s are killed before new ones are created when
`.spec.strategy.type==Recreate`. This will only guarantee `Pod` termination
previous to creation for upgrades. If we upgrade a `Deployment`, all `Pod`s of
the old revision will be terminated immediately. Successful removal is awaited
before any `Pod` of the new revision is created. If we manually delete a `Pod`,
the lifecycle is controlled by the `ReplicaSet` and the replacement will be
created immediately (even if the old `Pod` is still in a `Terminating` state).
If an "at most" guarantee is needed for `Pod`s, consider using a `StatefulSet`.

#### Rolling Update `Deployment`

The `Deployment` updates `Pod`s in a rolling update fashion when
`.spec.strategy.type==RollingUpdate`. We can specify `maxUnavailable` and
`maxSurge` to control the rolling update process.

##### Max Unavailable

`.spec.strategy.rollingUpdate.maxUnavailable` is an optional field that
specifies the maximum number of `Pod`s that can be unavailable during the
update process. The value can be an absolute number (for example, 5) or a
percentage of desired `Pod`s (for example, 10%). The absolute number is
calculated from percentage by rounding down. The value cannot be 0 if
`.spec.strategy.rollingUpdate.maxSurge` is 0. The default value is 25%.

For example, when this value is set to 30%, the old `ReplicaSet` can be scaled
down to 70% of desired `Pod`s immediately when the rolling update starts. Once
new `Pod`s are ready, old `ReplicaSet` can be scaled down further, followed by
scaling up the new `ReplicaSet`, ensuring that the total number of `Pod`s
available at all times during the update is at least 70% of the desired `Pod`s.

##### Max Surge

`.spec.strategy.rollingUpdate.maxSurge` is an optional field that specifies the
maximum number of `Pod`s that can be created over the desired number of `Pod`s.
The value can be an absolute number (for example, 5) or a percentage of desired
`Pod`s (for example, 10%). The value cannot be 0 if `MaxUnavailable` is 0. The
absolute number is calculated from the percentage by rounding up. The default
value is 25%.

For example, when this value is set to 30%, the new `ReplicaSet` can be scaled
up immediately when the rolling update starts, such that the total number of
old and new `Pod`s does not exceed 130% of desired `Pod`s. Once old `Pod`s have
been killed, the new `ReplicaSet` can be scaled up further, ensuring that the
total number of `Pod`s running at any time during the update is at most 130% of
desired `Pod`s.

### Min Ready Seconds

`.spec.minReadySeconds` is an optional field that specifies the minimum number
of seconds for which a newly created `Pod` should be ready without any of its
`Container`s crashing, for it to be considered available. This defaults to 0
(the `Pod` will be considered available as soon as it is ready). `Pod`
readiness has already been discussed in the [`Pod` lifecycle document](../pods/pod_lifecycle.md).

### Progress Deadline Seconds

`.spec.progressDeadlineSeconds` is an optional field that specifies the number
of seconds we want to wait for our `Deployment` to progress before the system
reports back that the `Deployment` has failed progressing - surfaced as a
condition with type: `Progressing`, `status: False` and
`reason: ProgressDeadlineExceeded` in the status of the resource. The
`Deployment` `Controller` will keep retrying the `Deployment`. This defaults
to 600. In future, once automatic rollback will be implemented, the
`Deployment` `Controller` will roll back a `Deployment` as soon as it observes
such a condition. If specified, this field needs to be greater than
`.spec.minReadySeconds`.

### Revision History Limit

A `Deployment`'s revision history is stored in the `ReplicaSet`s it controls.
`.spec.revisionHistoryLimit` is an optional field that specifies the number of
old `ReplicaSet`s to retain to allow rollback. These old `ReplicaSet`s consume
resources in `etcd` and crowd the output of `kubectl get rs`. The configuration
of each `Deployment` revision is stored in its `ReplicaSet`s; therefore, once
an old `ReplicaSet` is deleted, we lose the ability to rollback to that
revision of `Deployment`. By default, 10 old `ReplicaSet`s will be kept,
however its ideal value depends on the frequency and stability of new
`Deployment`s. Setting this field to 0 means that all old `ReplicaSet`s with 0
replicas will be cleaned up, a new `Deployment` rollout cannot be undone, since
its revision history is cleaned up.

### Paused

`.spec.paused` is an optional boolean field for pausing and resuming a
`Deployment`. The only difference between a paused `Deployment` and one that is
not paused, is that any changes into the `PodTemplateSpec` of the paused
`Deployment` will not trigger new rollouts as long as it is paused. A
`Deployment` is not paused by default when it is created.
