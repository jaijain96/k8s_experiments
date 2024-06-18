# [`Controller`s](https://kubernetes.io/docs/concepts/architecture/controller/)

In robotics and automation, a control loop is a non-terminating loop that
regulates the state of a system. In Kubernetes, `Controller`s are control
loops that watch the state of your cluster, then make or request changes where
needed. Each `Controller` tries to move the current cluster state closer to the
desired state.

A `Controller` tracks at least one Kubernetes resource type. These objects have
a `spec` field that represents the desired state. The `Controller`(s) for that
resource are responsible for making the current state come closer to that
desired state.

The `Controller` might carry the action out itself; more commonly, in
Kubernetes, a `Controller` will send messages to the API server that have
useful side effects.

## Control via API Server

The `Job` `Controller` is an example of a Kubernetes built-in controller.
Built-in `Controller`s manage state by interacting with the cluster API server.
`Job` is a Kubernetes resource that runs a `Pod`, or perhaps several `Pod`s, to
carry out a task and then stop. When the `Job` `Controller` sees a new task it
makes sure that, somewhere in your cluster, the `kubelet`s on a set of `Nodes`
are running the right number of `Pod`s to get the work done. The `Job`
`Controller` does not run any `Pod`s or `Container`s itself. Instead, the `Job`
`Controller` tells the API server to create or remove `Pod`s. Other components
in the `Control Plane` act on the new information (there are new `Pod`s to
schedule and run), and eventually the work is done.

## Direct Control

Some `Controller`s need to make changes to things outside of your cluster. For
example, if you use a control loop to make sure there are enough `Node`s in
your cluster, then that `Controller` needs something outside the current
cluster to set up new `Node`s when needed. `Controller`s that interact with
external state find their desired state from the API server, then communicate
directly with an external system to bring the current state closer in line.

## Design

Kubernetes uses lots of `Controller`s that each manage a particular aspect of
cluster state. A particular `Controller` uses one kind of resource as its
desired state, and has a different kind of resource that it manages to make
that desired state happen. For example, a `Controller` for `Job`s tracks `Job`
objects (to discover new work) and `Pod` objects (to run the `Job`s, and then
to see when the work is finished). In this case something else creates the
`Job`s, whereas the `Job` controller creates `Pod`s.

It's useful to have simple `Controller`s rather than one, monolithic set of
control loops that are interlinked. `Controller`s can fail, so Kubernetes is
designed to allow for that.

## Ways of running `Controller`s

Kubernetes comes with a set of built-in `Controller`s that run inside the
`kube-controller-manager`. These built-in `Controller`s provide important core
behaviors.
