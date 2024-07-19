# [Sidecar `Container`s](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)

Sidecar `Container`s run along with the main application `Container` within the
same `Pod`. These `Container`s are used to enhance or to extend the
functionality of the primary app `Container` by providing additional services,
or functionality such as logging, monitoring, security, or data
synchronization, without directly altering the primary application code.

K8s implements sidecar `Container`s as a special case of init `Container`s;
sidecar `Container`s remain running after `Pod` startup. Provided that our
cluster has the `SidecarContainers` feature gate enabled, we can specify a
`restartPolicy` for `Container`s listed in a `Pod`'s `initContainers` field.
These restartable sidecar `Container`s are independent from other init
`Container`s and from the main application `Container`(s) within the same
`Pod`. These can be started, stopped, or restarted without effecting the main
application `Container` and other init `Container`s.

<mark>We can also run a `Pod` with multiple `Container`s that are not marked as
init or sidecar `Container`s.</mark> This is appropriate if the `Container`s
within the `Pod` are required for the `Pod` to work overall, but we don't need
to control which `Container`s start or stop first. We can also do this if we
need to support older versions of K8s that don't support a `Container`-level
`restartPolicy` field.

If an init `Container` is created with its `restartPolicy` set to `Always`, it
will start and remain running during the entire life of the `Pod`. If a
`readinessProbe` is specified for this init `Container`, its result will be
used to determine the ready state of the `Pod`. Since these `Container`s are
defined as init `Container`s, they benefit from the same ordering and
sequential guarantees as regular init `Container`s, allowing us to mix sidecar
`Container`s with regular init `Container`s for complex `Pod` initialization
flows. After a sidecar-style init `Container` is running (the `kubelet` has set
the started status for that init `Container` to `true`), the `kubelet` then
starts the next init `Container` from the ordered `.spec.initContainers` list.
That status either becomes `true` because there is a process running in the
`Container` and no `startupProbe` defined, or as a result of its `startupProbe`
succeeding.

If we define a `Job` that uses sidecar using K8s-style init `Container`s, the
sidecar `Container` in each `Pod` does not prevent the `Job` from completing
after the main application/job `Container` has finished.

Sidecar `Container`s have their own independent lifecycles. They can be
started, stopped, and restarted independently of app `Container`s. This means
we can update, scale, or maintain sidecar `Container`s without affecting the
primary application. They share the same network and storage `Namespace`s with
the primary `Container` allowing them to interact closely and share resources.
In contrast, regular init `Container`s stop before the main application
`Container`s start up, so they can't exchange messages with the app
`Container` in a `Pod`. Any data passing is one-way (for example, an init
`Container` can put information inside an `emptyDir` volume).
