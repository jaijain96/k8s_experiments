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

## `Pod` Lifetime

Whilst a `Pod` is running, the `kubelet` is able to restart `Container`s to
handle some kind of faults. Within a `Pod`, Kubernetes tracks different
`Container` states and determines what action to take to make the `Pod` healthy
again.

`Pod`s have both a specification and an actual status. The status for a `Pod`
object consists of a set of `Pod` conditions. We can also inject custom
readiness information into the condition data for a `Pod`, if that is useful to
our application.

<mark>`Pod`s are only scheduled once in their lifetime; the process of
selecting which `Node` to use is called *scheduling*, and assigning a `Pod`
to a specific `Node` is called *binding*. Once a `Pod` has been scheduled and
is bound to a `Node`, Kubernetes tries to run that `Pod` on THAT `Node`. The
`Pod` runs on that `Node` until it stops, or until the `Pod` is terminated;
if Kubernetes isn't able start the `Pod` on the selected `Node` (for example,
if the `Node` crashes before the `Pod` starts), then that particular `Pod`
never starts.</mark>

### `Pod`s and Fault Recovery

If one of the `Container`s in the `Pod` fails, then Kubernetes may try to
restart that specific `Container`. `Pod`s can however fail in a way that the
cluster cannot recover from, and in that case Kubernetes does not attempt to
heal the `Pod` further; instead, Kubernetes deletes the `Pod` and relies on
other components to provide automatic healing.<br>
<mark>DOUBT: examples of scenarios of this automatic healing?</mark>

If a `Pod` is scheduled to a `Node` and that `Node` then fails, the `Pod` is
treated as unhealthy and Kubernetes eventually deletes the `Pod`. A `Pod` won't
survive an eviction due to a lack of resources or `Node` maintenance.
Kubernetes uses `Controller`s to manage the relatively disposable `Pod`
instances.

<mark>A given `Pod` (as defined by a UID) is never "rescheduled" to a
different `Node`; instead, that `Pod` can be replaced by a new,
near-identical `Pod`. If we make a replacement `Pod`, it can even have the
same name (`.metadata.name`) that the old `Pod` had, but the replacement
would have a different `.metadata.uid` from the old `Pod`. Kubernetes
doesn't guarantee that a replacement for an existing `Pod` would be
scheduled to the same `Node` as the old `Pod` that was being replaced.</mark>

### Associated Lifetimes

When something is said to have the same lifetime as a `Pod`, such as a
`volume`, that means that the thing exists as long as that specific `Pod` (with
that exact UID) exists. If that `Pod` is deleted for any reason, and even if an
identical replacement is created, the related thing (a `volume`, in this
example) is also destroyed and created anew.

## `Pod` Phase

A `Pod`'s `status` field is a `PodStatus` object, which has a `phase` field.

<mark>The `phase` of a `Pod` is a simple, high-level summary of where the `Pod` is in
its lifecycle. The `phase` is not intended to be a comprehensive rollup of
observations of `Container` or `Pod` state, nor is it intended to be a
comprehensive state machine. The number and meanings of `Pod` `phase` values
are tightly guarded. Other than what is documented
[here](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-phase),
nothing should be assumed about `Pod`s that have a given `phase` value.</mark>

If a `Node` dies or is disconnected from the rest of the cluster, Kubernetes
applies a policy for setting the `phase` of all `Pod`s on the lost `Node` to
`Failed`.

## `Container` States

<mark>As well as the `phase` of the `Pod` overall, Kubernetes tracks the
`state` of each `Container` inside a `Pod`.</mark> Once the `scheduler`
assigns a `Pod` to a `Node`, the `kubelet` starts creating `Container`s for
that `Pod` using a `Container` runtime. There are three possible `Container`
`state`s: `Waiting`, `Running`, and `Terminated`. To check the state of a
`Pod`'s `Container`s, you can use:

```bash
kubectl describe pod <name-of-pod>
```

The output shows the `state` for each `Container` within that `Pod`. Each
`state` has a specific meaning:

1. `Waiting`: A `Container` in the `Waiting` `state` is still running the
   operations it requires in order to complete start up: for example, pulling
   the `Container` image from a `Container` image registry, or applying `Secret`
   data.
2. `Running`: The `Running` status indicates that a `Container` is executing
   without issues.
3. `Terminated`: A `Container` in the `Terminated` `state` began execution and
   then either ran to completion or failed for some reason.

## How `Pod`s Handle Problems with `Container`s

<mark>Kubernetes manages `Container` failures within `Pod`s using a `restartPolicy`
defined in the `Pod` `spec`. This policy determines how Kubernetes reacts to
`Container`s exiting due to errors or other reasons</mark>, which falls in the
following sequence:

1. Initial crash: Kubernetes attempts an immediate restart based on the `Pod`
   `restartPolicy`.
2. Repeated crashes: After the initial crash Kubernetes applies an exponential
   backoff delay for subsequent restarts, described in `restartPolicy`. This
   prevents rapid, repeated restart attempts from overloading the system.
3. `CrashLoopBackOff` `state`: This indicates that the backoff delay mechanism
   is currently in effect for a given `Container` that is in a crash loop,
   failing and restarting repeatedly.
4. Backoff reset: If a `Container` runs successfully for a certain duration
   (e.g., 10 minutes), Kubernetes resets the backoff delay, treating any new
   crash as the first one.

### `Container` `restartPolicy`

The `spec` of a `Pod` has a `restartPolicy` field with possible values
`Always`, `OnFailure`, and `Never`. The default value is `Always`. The
`restartPolicy` applies to app `Container`s in the `Pod` and to regular init
`Container`s. Sidecar `Container`s ignore the `Pod`-level `restartPolicy`
field: in Kubernetes, a sidecar is defined as an entry inside `initContainer`s
that has its `Container`-level `restartPolicy` set to `Always`.

- `Always`: Automatically restarts the `Container` after any termination.
- `OnFailure`: Only restarts the `Container` if it exits with an error
  (non-zero exit status).
- `Never`: Does not automatically restart the terminated `Container`.

<mark>When the `kubelet` is handling `Container` restarts according to the
configured `restartPolicy`, that only applies to restarts that make
replacement `Container`s inside the SAME `Pod` and running on the SAME
`Node`.</mark> After `Container`s in a `Pod` exit, the `kubelet` restarts
them with an exponential backoff delay (10s, 20s, 40s, …), that is capped at
300 seconds (5 minutes). Once a `Container` has executed for 10 minutes
without any problems, the `kubelet` resets the restart backoff timer for that
`Container`.

## `Pod` Conditions

A `Pod` has a `PodStatus`, which has an array of `PodConditions` through which
the `Pod` has or has not passed. `kubelet` manages the following
`PodConditions`:

- `PodScheduled`: the `Pod` has been scheduled to a `Node`.
- `PodReadyToStartContainers`: (beta feature; enabled by default) the `Pod`
  sandbox has been successfully created and networking configured.
- `ContainersReady`: all `Container`s in the `Pod` are ready.
- `Initialized`: all init `Container`s have completed successfully.
- `Ready`: the `Pod` is able to serve requests and should be added to the load
  balancing pools of all matching `Service`s.

### `Pod` Readiness

Our application can inject extra feedback or signals into `PodStatus`: `Pod`
readiness. To use this, set `readinessGates` in the `Pod`'s `spec` to specify
a list of additional conditions that the `kubelet` evaluates for `Pod`
readiness.

Readiness gates are determined by the current state of `status.conditions`
fields for the `Pod`. If Kubernetes cannot find such a condition in the
`status.conditions` field of a `Pod`, the status of the condition is defaulted
to `False`.

### Status for `Pod` Readiness

The `kubectl` `patch` command does not support patching object status. To set
these `status.conditions` for the `Pod`, applications and operators should use
the `PATCH` action. You can use a
[Kubernetes client library](https://kubernetes.io/docs/reference/using-api/client-libraries/)
to write code that sets custom `Pod` conditions for `Pod` readiness. For a
`Pod` that uses custom conditions, that `Pod` is evaluated to be ready only
when both the following statements apply:

- All `Container`s in the `Pod` are ready.
- All conditions specified in `readinessGates` are `True`.

When a `Pod`'s containers are `Ready` but at least one custom condition is
missing or `False`, the `kubelet` sets the `Pod`'s condition to
`ContainersReady`.

### `Pod` Network Readiness

After a `Pod` gets scheduled on a `Node`, it needs to be admitted by the
`kubelet` to have any required storage volumes mounted. Once these `phase`s are
complete, the `kubelet` works with a `Container` runtime to set up a runtime
sandbox and configure networking for the `Pod`. If the
`PodReadyToStartContainersCondition` feature gate is enabled (it is enabled by
default for Kubernetes 1.30), the `PodReadyToStartContainers` condition will
be added to the `status.conditions` field of a `Pod`.

The `PodReadyToStartContainers` condition is set to `False` by the `kubelet`
when it detects a `Pod` does not have a runtime sandbox with networking
configured. This occurs in the following scenarios:

- Early in the lifecycle of the `Pod`, when the `kubelet` has not yet begun to
  set up a sandbox for the `Pod` using the `Container` runtime.
- Later in the lifecycle of the `Pod`, when the `Pod` sandbox has been
  destroyed due to either:
  - the `Node` rebooting, without the `Pod` getting evicted
  - for `Container` runtimes that use virtual machines for isolation, the
    `Pod` sandbox virtual machine rebooting, which then requires creating a
    new sandbox and fresh `Container` network configuration.

The `PodReadyToStartContainers` condition is set to `True` by the `kubelet`
after the successful completion of sandbox creation and network configuration
for the `Pod` by the runtime plugin. The `kubelet` can start pulling
`Container` images and create `Container`s after `PodReadyToStartContainers`
condition has been set to `True`.

For a `Pod` with init containers, the `kubelet` sets the `Initialized`
condition to `True` after the init containers have successfully completed
(which happens after successful sandbox creation and network configuration by
the runtime plugin). For a `Pod` without init containers, the `kubelet` sets
the `Initialized` condition to `True` before sandbox creation and network
configuration starts.

## `Container` Probes

<mark>A `probe` is a diagnostic performed periodically by the `kubelet` on a
`Container`. To perform a diagnostic, the `kubelet` either executes code within
the `Container`, or makes a network request.</mark>

### Check Mechanisms

Each `probe` must define exactly one of these four mechanisms:

1. `exec`: Executes a specified command inside the `Container`. The diagnostic
   is considered successful if the command exits with a status code of `0`.
2. `grpc`: Performs a remote procedure call using `gRPC`. The target should
   implement `gRPC` health checks. The diagnostic is considered successful if
   the status of the response is `SERVING`.
3. `httpGet`: Performs an HTTP `GET` request against the `Pod`'s IP address
   on a specified `port` and `path`. The diagnostic is considered successful if
   the response has a status code >= `200` and < `400`.
4. `tcpSocket`: Performs a TCP check against the `Pod`'s IP address on a
   specified `port`. The diagnostic is considered successful if the `port` is
   open. If the remote system (the `Container`) closes the connection
   immediately after it opens, this counts as healthy.

### `Probe` Outcome

Each `probe` has one of three results:

- `Success`: The `Container` passed the diagnostic.
- `Failure`: The `Container` failed the diagnostic.
- `Unknown`: The diagnostic failed (no action should be taken, and the
  `kubelet` will make further checks).

### Types of `Probes`

The `kubelet` can optionally perform and react to three kinds of `Probe`s on
running `Container`s:

- `livenessProbe`: Indicates whether the `Container` is running. If the
  `livenessProbe` fails, the `kubelet` kills the `Container`, and is
  subjected to its `restartPolicy`. If a `Container` does not provide a
  `livenessProbe`, the default state is `Success`.
- `readinessProbe`: Indicates whether the `Container` is ready to respond to
  requests. If the `readinessProbe` fails, the endpoints controller removes the
  `Pod`'s IP address from the endpoints of all `Service`s that match the `Pod`.
  The default state of readiness before the initial delay is `Failure`. If a
  `Container` does not provide a `readinessProbe`, the default state is
  `Success`.
- `startupProbe`: Indicates whether the application within the `Container` is
  started. All other `Probe`s are disabled if a `startupProbe` is provided,
  until it succeeds. If the `startupProbe` fails, the `kubelet` kills the
  `Container`, and the `Container` is subjected to its `restartPolicy`. If a
  `Container` does not provide a `startupProbe`, the default state is
  `Success`.

**When to use `livenessProbe`?**

If the process in our `Container` is able to crash on its own whenever it
encounters an issue or becomes unhealthy, we don't necessarily need a
`livenessProbe`; the `kubelet` will automatically perform the correct action in
accordance with the `Pod`'s `restartPolicy`. If we want our `Container` to be
killed and restarted if `Probe` fails, then we specify a `livenessProbe` and
specify a `restartPolicy` of `Always` or `onFailure`.

**When to use `readinessProbe`?**

If we'd like to start sending traffic to a `Pod` only when a `Probe` succeeds,
we can specify a `readinessProbe`. In this case, the `readinessProbe` might be
the same as the `livenessProbe`, but the existence of the `readinessProbe` in
the `spec` means that the `Pod` will start without receiving any traffic and
only start receiving traffic after the `Probe` starts succeeding.

If we want our `Container` to be able to take itself down for maintenance, we
can specify a `readinessProbe` that checks an endpoint specific to readiness
that is different from the `livenessProbe`.

<mark>If our app has a strict dependency on back-end services, we can implement both
a `livenessProbe` and a `readinessProbe`. The `livenessProbe` passes when the
app itself is healthy, but the `readinessProbe` additionally checks that each
required back-end service is available. This helps avoid directing traffic to
`Pod`s that can only respond with error messages.</mark>

If we want to be able to drain requests when the `Pod` is deleted, we don't
necessarily need a `readinessProbe`; on deletion, the `Pod` automatically puts
itself into an unready state regardless of whether the `readinessProbe` exists.
The `Pod` remains in the unready state while it waits for the `Container`s in
the `Pod` to stop.

**When to use `startupProbe`?**

<mark>Startup `Probe`s are useful for `Pod`s that have `Container`s that
take a long time to come into service. Rather than set a long liveness
interval, we can configure a separate configuration for probing the
`Container` as it starts up, allowing a time longer than the liveness
interval would allow. If our `Container` needs to work on loading large
data, configuration files, or migrations during startup, we can use a
`startupProbe`.</mark>

If our `Container` usually starts in more than
`initialDelaySeconds + failureThreshold × periodSeconds`, we should specify a
`startupProbe` that checks the same endpoint as the `livenessProbe`. The
default for `periodSeconds` is 10s. We should then set its `failureThreshold`
high enough to allow the `Container` to start, without changing the default
values of the `livenessProbe`. This helps to protect against deadlocks.

## Termination of `Pod`s

K8s design aim is for the user to be able to request deletion and know when
processes terminate, but also be able to ensure that deletes eventually
complete. <mark>When we request deletion of a `Pod`, the cluster records and
tracks the intended grace period before the `Pod` is allowed to be
forcefully killed. With that forceful shutdown tracking in place, the
`kubelet` attempts graceful shutdown. The requests to stop the `Container`s
are processed by the `Container` runtime asynchronously, i.e, there is no
guarantee to the order of processing for these requests. Once the grace
period has expired, the `KILL` signal is sent to any remaining processes,
and the `Pod` is then deleted from the API Server. If the `kubelet` or the
`Container` runtime's management service is restarted while waiting for
processes to terminate, the cluster retries from the start including the
full original grace period.</mark>

`Pod` termination flow:

1. We use the `kubectl` tool to manually delete a specific `Pod`, with the
   default grace period (30 seconds).
2. The `Pod` object in the API server is updated with the time beyond which the
   `Pod` is considered "dead" along with the grace period. If we use `kubectl`
   describe to check the `Pod` we're deleting, it shows up as `Terminating`.
   On the `Node` where the `Pod` is running: as soon as the `kubelet` sees that
   a `Pod` has been marked as `Terminating` (a graceful shutdown duration has
   been set), the `kubelet` begins the local `Pod` shutdown process:
   1. If one of the `Pod`'s `Container`s has defined a `preStop` hook and the
      `terminationGracePeriodSeconds` in the `Pod` `spec` is not set to 0, the
      `kubelet` runs that hook inside of the `Container`. The default
      `terminationGracePeriodSeconds` setting is 30 seconds.

      If the `preStop` hook is still running after the grace period expires,
      the `kubelet` requests a small, one-off grace period extension of 2
      seconds. If the `preStop` hook needs longer to complete than the default
      grace period allows, we must modify `terminationGracePeriodSeconds` to
      suit this.
   2. The `kubelet` triggers the `Container` runtime to send a `TERM` signal to
      process 1 inside each `Container`. There is special ordering if the `Pod`
      has any sidecar `Container`s defined. Otherwise, the `Container`s in the
      `Pod` receive the `TERM` signal at different times and in an arbitrary
      order. If the order of shutdowns matters, we can use a `preStop` hook to
      synchronize (or switch to using sidecar `Container`s).
3. <mark>At the same time as the `kubelet` is starting graceful shutdown of the
   `Pod`, the `Control Plane` evaluates whether to remove that shutting-down
   `Pod` from `EndpointSlice` (and `Endpoints`) objects, where those objects
   represent a `Service` with a configured selector. `ReplicaSets` and other
   workload resources no longer treat the shutting-down `Pod` as a valid,
   in-service replica.</mark>

   <mark>Any `Endpoints` that represent the `Terminating` `Pod`s are not immediately
   removed from `EndpointSlices`, and a status indicating `Terminating` state
   is exposed from the `EndpointSlice` API (and the legacy `Endpoints` API).
   `Terminating` `Endpoints` always have their ready status as `false`, so
   load balancers will not use it for regular traffic.</mark>
4. The `kubelet` ensures the `Pod` is shut down and terminated:
   1. When the grace period expires, if there is still any `Container` running
      in the `Pod`, the `kubelet` triggers forcible shutdown. The `Container`
      runtime sends `SIGKILL` to any processes still running in any `Container`
      in the `Pod`. The `kubelet` also cleans up a hidden `pause` `Container`
      if that `Container` runtime uses one.
   2. The `kubelet` transitions the `Pod` into a terminal `Phase` (`Failed` or
      `Succeeded` depending on the end state of its `Container`s).
   3. The `kubelet` triggers forcible removal of the `Pod` object from the API
      server, by setting grace period to 0 (immediate deletion).
   4. The API server deletes the `Pod`'s API object, which is then no longer
      visible from any client.

### Forced Pod Termination

By default, all deletes are graceful within 30 seconds. The `kubectl` delete
command supports the `--grace-period=<seconds>` option which allows us to
override the default and specify our own value. Setting the grace period to 0
forcibly immediately deletes the `Pod` from the API server. If the `Pod` was
still running on a `Node`, that forcible deletion triggers the `kubelet` to
begin immediate cleanup. <mark>Using `kubectl`, we must specify an additional
flag `--force` along with `--grace-period=0` in order to perform force
deletions.</mark>

<mark>When a force deletion is performed, the API server does not wait for
confirmation from the `kubelet` that the `Pod` has been terminated on the
`Node` it was running on. It removes the `Pod` in the API immediately so a new
`Pod` can be created with the same name. On the `Node`, `Pod`s that are set to
terminate immediately will still be given a small grace period before being
force killed.</mark>

### `Pod` Shutdown and Sidecar `Container`s

<mark>If our `Pod` includes one or more sidecar `Container`s (init containers with
an `Always` `restartPolicy`), the `kubelet` will delay sending the `TERM`
signal to these sidecar `Container`s until the last main `Container` has fully
terminated. The sidecar `Container`s will be terminated in the reverse order
they are defined in the `Pod` `spec`. This ensures that sidecar `Container`s
continue serving the other `Container`s in the `Pod` until they are no longer
needed.</mark>

This means that slow termination of a main `Container` will also delay the
termination of the sidecar `Container`s. If the grace period expires before the
termination process is complete, the `Pod` may enter forced termination. In
this case, all remaining `Container`s in the `Pod` will be terminated
simultaneously with a short grace period.

### Garbage Collection of `Pod`s

<mark>For `Failed` `Pod`s, the API objects remain in the cluster's API until a
human or controller process explicitly removes them. The `Pod` garbage
collector (`PodGC`) is a `Controller` in the `Control Plane`, that cleans up
terminated `Pod`s (with a phase of `Succeeded` or `Failed`), when the number
of `Pod`s exceeds the configured threshold (determined by
`terminated-pod-gc-threshold` in the `kube-controller-manager`). This avoids
a resource leak as `Pod`s are created and terminated over time.</mark>

Additionally, `PodGC` cleans up any `Pod`s which satisfy any of the following
conditions:

- are orphan `Pod`s bound to a `Node` which no longer exists,
- are unscheduled terminating `Pod`s,
- are terminating `Pod`s, bound to a non-ready `Node` tainted with
  `node.kubernetes.io/out-of-service`, when the `NodeOutOfServiceVolumeDetach`
  feature gate is enabled.

When the `PodDisruptionConditions` feature gate is enabled, `PodGC` will also
mark them as failed if they are in a non-terminal `phase`. Also, `PodGC` adds a
[`Pod` disruption condition](https://kubernetes.io/docs/concepts/workloads/pods/disruptions#pod-disruption-conditions)
when cleaning up an orphan `Pod`.
