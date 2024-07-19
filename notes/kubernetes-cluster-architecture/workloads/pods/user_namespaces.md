# [User `Namespace`s](https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/)

Several `Container` runtimes with their default configuration (like Docker
Engine, containerd, CRI-O) use Linux `Namespace`s for isolation. When creating
a `Pod`, by default, several new `Namespace`s are used for isolation: a network
`namespace` to isolate the network of the `Container`, a PID `Namespace` to
isolate the view of processes, etc. User `Namespace`s is a Linux feature that
allows to map users in the `Container` to different users in the host. If a
user `Namespace` is used, this will isolate the users in the `Container` from
the users in the `Node`. This means `Container`s can run as `root` and be
mapped to a non-`root` user on the host; in other words, the process has full
privileges for operations inside the user `Namespace`, but is unprivileged for
operations outside the `Namespace`. Inside the `Container` the process will
think it is running as `root` (and therefore tools like `apt`, `yum`, etc. work
fine), while in reality the process doesn't have privileges on the host. We can
verify this, for example, if we check which user the `Container` process is
running by executing `ps aux` from the host. The user `ps` shows is not the
same as the user we see if we execute inside the `Container` the command `id`.

A `Pod` can opt-in to use user `Namespace`s by setting the `pod.spec.hostUsers`
field to `false`. The `kubelet` will pick host UIDs/GIDs a `Pod` is mapped to,
and will do so in a way to guarantee that no two `Pod`s on the same `Node` use
the same mapping.

Capabilities granted to a `Pod` are limited to the `Pod` user `Namespace` and
mostly invalid out of it, some are even completely void. Here are two examples:

- `CAP_SYS_MODULE` does not have any effect if granted to a `Pod` using user
  `Namespace`s, the `Pod` isn't able to load kernel modules.
- `CAP_SYS_ADMIN` is limited to the `Pod`'s user `Namespace` and invalid
  outside of it.

This abstraction limits what can happen, for example, if the `Container`
manages to escape to the host. Given that the `Container` is running as a
non-privileged user on the host, it is limited what it can do to the host. As
users on each `Pod` will be mapped to different non-overlapping users in the
host, it is limited what they can do to other pods too.

Without using a user `Namespace` a `Container` running as `root`, in the case of
a `Container` breakout, has `root` privileges on the `Node`. And if some
capability were granted to the `Container`, the capabilities are valid on the
host too. None of this is true when we use user `Namespace`s. This also reduces
the damage a compromised `Container` can do to the host or other `Pod`s in the
same `Node`. <mark>There are [several security vulnerabilities](https://github.com/kubernetes/enhancements/tree/217d790720c5aef09b8bd4d6ca96284a0affe6c2/keps/sig-node/127-user-namespaces#motivation) rated either **HIGH** or **CRITICAL**
that were not exploitable when user `Namespace`s is active.</mark> It is
expected user `Namespace` will mitigate some future vulnerabilities too.
