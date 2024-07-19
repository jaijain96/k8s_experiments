# [Ephemeral `Container`s](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)

`Pod`s are the fundamental building block of K8s applications. Since `Pod`s are
intended to be disposable and replaceable, we can't add a `Container` to a
`Pod` once it has been created. Instead, we usually delete and replace `Pod`s
in a controlled fashion using `Deployments`.

Sometimes it's necessary to inspect the state of an existing `Pod`, for example
to troubleshoot a hard-to-reproduce bug. In these cases we can run an ephemeral
`Container` in an existing `Pod` to inspect its state and run arbitrary
commands. Ephemeral `Container`s are a special type of `Container` that runs
temporarily in an existing `Pod` to accomplish user-initiated actions such as
troubleshooting. We can use ephemeral `Container`s to inspect services rather
than to build applications.

Ephemeral `Container`s differ from other `Container`s in that they lack
guarantees for resources or execution, and they will never be automatically
restarted, so they are not appropriate for building applications. Ephemeral
`Container`s are described using the same `ContainerSpec` as regular
`Container`s, but many fields are incompatible and disallowed for ephemeral
`Container`s:

- They may not have `ports`, so fields such as `ports`, `livenessProbe`,
  `readinessProbe` are disallowed.
- `Pod` resource allocations are immutable, so setting resources is disallowed.

Ephemeral `Container`s are created using a special `ephemeralcontainers`
handler in the API rather than by adding them directly to `pod.spec`, so it's
not possible to add an ephemeral `Container` using `kubectl` edit. Like regular
`Container`s, we may not change or remove an ephemeral `Container` after we
have added it to a `Pod`.

Ephemeral `Container`s are useful for interactive troubleshooting when
`kubectl exec` is insufficient because a `Container` has crashed or a
`Container` image doesn't include debugging utilities.

In particular, [distroless images](https://github.com/GoogleContainerTools/distroless) enable us to deploy minimal `Container` images that reduce attack
surface and exposure to bugs and vulnerabilities. Since distroless images don't
include a shell or any debugging utilities, it's difficult to troubleshoot
distroless images using `kubectl exec` alone.

When using ephemeral `Container`s, it's helpful to enable [process namespace sharing](https://kubernetes.io/docs/tasks/configure-pod-container/share-process-namespace/) so we can view processes in other `Container`s.
