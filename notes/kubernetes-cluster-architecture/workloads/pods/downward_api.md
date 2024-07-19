# [Downward API](https://kubernetes.io/docs/concepts/workloads/pods/downward-api/)

It is sometimes useful for a `Container` to have information about itself,
without being overly coupled to K8s. The downward API allows `Container`s to
consume information about themselves or the cluster without using the
K8s client or API server. There are two ways to expose `Pod` and `Container`
fields to a running `Container`:

- as environment variables
- as files in a `downwardAPI` volume

Together, these two ways of are called the downward API. Only [some K8s API
fields](https://kubernetes.io/docs/concepts/workloads/pods/downward-api/#available-fields) are available through the downward API.
