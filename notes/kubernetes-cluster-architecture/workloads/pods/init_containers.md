# [Init `Container`s](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)

## Understanding Init `Container`s

A `Pod` can have multiple `Container`s running apps within it as well as one
or more init `Container`s, which are run before the app `Container`s are
started. Few differences between init `Container`s and regular `Containers`:

- Init `Container`s always run to completion.
- Each init `Container` must complete successfully before the next one starts.

<mark>If a `Pod`'s init `Container` fails, the `kubelet` repeatedly restarts
that init `Container` until it succeeds. However, if the `Pod` has a
`restartPolicy` of `Never`, and an init `Container` fails during startup of that
`Pod`, k8s treats the overall `Pod` as `Failed`.</mark>

## Detailed Behavior

During `Pod` startup, the `kubelet` delays running init `Container`s until the
networking and storage are ready. Then the `kubelet` runs the `Pod`'s init
`Container`s in the order they appear in the `Pod`'s `spec`.

<mark>Each init `Container` must exit successfully before the next `Container`
starts.</mark> If a `Container` fails to start due to the runtime or exits with
failure, it is retried according to the `Pod` `restartPolicy`. However, if the
`Pod` `restartPolicy` is set to `Always`, the init `Container`s use
`restartPolicy` `OnFailure`.

<mark>A `Pod` cannot be `Ready` until all init `Container`s have succeeded.
</mark> The ports on an init `Container` are not aggregated under a
`Service`. A `Pod` that is initializing is in the `Pending` state but should
have a condition `Initialized` set to `False`.

<mark>Changes to the init `Container` `spec` are limited to the container
image field. Altering that field is equivalent to restarting the `Pod`.<mark>

<mark>Because init `Container`s can be restarted, retried, or re-executed,
init `Container` code should be idempotent.<mark> In particular, code that
writes to files on `EmptyDirs` should be prepared for the possibility that
an output file already exists.

Init `Container`s do not support the `lifecycle`, `livenessProbe`,
`readinessProbe`, or `startupProbe` fields whereas sidecar `Container`s support
all these. Init `Container`s must run to completion before the `Pod` can be
ready; sidecar `Container`s continue running during a `Pod`'s lifetime.

K8s prohibits `readinessProbe` from being used because init `Container`s cannot
define readiness distinct from completion. `activeDeadlineSeconds` can be used
on the `Pod` to prevent init `Container`s from failing forever. It is
recommended to use `activeDeadlineSeconds` only if teams deploy their
application as a `Job`, because `activeDeadlineSeconds` has an effect even
after init `Container`s finish. The `Pod` which is already running correctly
would be killed by `activeDeadlineSeconds` if we set.

## Using Init `Container`s

- Init `Container`s can contain utilities or custom code for setup that are not
  present in an app image. For example, there is no need to make an image
  `FROM` another image just to use a tool like `sed`, `awk`, `python`, or `dig`
  during setup.
- The application image builder and deployer roles can work independently
  without the need to jointly build a single app image.
- Init `Container`s can run with a different view of the filesystem than app
  `Container`s in the same `Pod`. Consequently, they can be given access to
  `Secret`s that app `Container`s cannot access.
- <mark>Because init `Container`s run to completion before any app
  `Container`s start, init `Container`s offer a mechanism to block or delay
  app `Container` startup until a set of preconditions are met. Once
  preconditions are met, all of the app `Container`s in a `Pod` can start in
  parallel.</mark>
- Init `Container`s can securely run utilities or custom code that would
  otherwise make an app `Container` image less secure. By keeping unnecessary
  tools separate you can limit the attack surface of your app `Container`
  image.
