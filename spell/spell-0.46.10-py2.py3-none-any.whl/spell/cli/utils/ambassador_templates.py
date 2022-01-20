# HACK: Suppress E501 Line Too Long across this file
# flake8: noqa

# YAML files for deploying the Ambassador Edge Stack onto EKS/GKE Model Serving
# First pulled from Ambassador Aug 17 2020

# Custom resources defined by the ambassador edge stack
# https://www.getambassador.io/yaml/aes-crds.yaml
aes_crds_yaml = r"""
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: authservices.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: AuthService
    listKind: AuthServiceList
    plural: authservices
    singular: authservice
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: AuthService is the Schema for the authservices API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: AuthServiceSpec defines the desired state of AuthService
          properties:
            add_auth_headers:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            add_linkerd_headers:
              type: boolean
            allow_request_body:
              type: boolean
            allowed_authorization_headers:
              items:
                type: string
              type: array
            allowed_request_headers:
              items:
                type: string
              type: array
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            auth_service:
              type: string
            failure_mode_allow:
              type: boolean
            include_body:
              properties:
                allow_partial:
                  type: boolean
                max_bytes:
                  type: integer
              required:
              - allow_partial
              - max_bytes
              type: object
            path_prefix:
              type: string
            proto:
              enum:
              - http
              - grpc
              type: string
            status_on_error:
              description: Why isn't this just an int??
              properties:
                code:
                  type: integer
              type: object
            timeout_ms:
              type: integer
            tls:
              oneOf:
              - type: string
              - type: boolean
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: consulresolvers.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: ConsulResolver
    listKind: ConsulResolverList
    plural: consulresolvers
    singular: consulresolver
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: ConsulResolver is the Schema for the ConsulResolver API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: ConsulResolver tells Ambassador to use Consul to resolve services.
            In addition to the AmbassadorID, it needs information about which Consul
            server and DC to use.
          properties:
            address:
              type: string
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            datacenter:
              type: string
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: hosts.getambassador.io
spec:
  additionalPrinterColumns:
  - JSONPath: .spec.hostname
    name: Hostname
    type: string
  - JSONPath: .status.state
    name: State
    type: string
  - JSONPath: .status.phaseCompleted
    name: Phase Completed
    type: string
  - JSONPath: .status.phasePending
    name: Phase Pending
    type: string
  - JSONPath: .metadata.creationTimestamp
    name: Age
    type: date
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: Host
    listKind: HostList
    plural: hosts
    singular: host
  scope: Namespaced
  subresources:
    status: {}
  validation:
    openAPIV3Schema:
      description: Host is the Schema for the hosts API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: HostSpec defines the desired state of Host
          properties:
            acmeProvider:
              description: Specifies whether/who to talk ACME with to automatically
                manage the $tlsSecret.
              properties:
                authority:
                  description: Specifies who to talk ACME with to get certs. Defaults
                    to Let's Encrypt; if "none" (case-insensitive), do not try to
                    do ACME for this Host.
                  type: string
                email:
                  type: string
                privateKeySecret:
                  description: LocalObjectReference contains enough information to
                    let you locate the referenced object inside the same namespace.
                  properties:
                    name:
                      description: 'Name of the referent. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names
                        TODO: Add other useful fields. apiVersion, kind, uid?'
                      type: string
                  type: object
                registration:
                  description: This is normally set automatically
                  type: string
              type: object
            ambassadorId:
              description: A compatibility alias for "ambassador_id"; because Host
                used to be specified with protobuf, and jsonpb allowed either "ambassador_id"
                or "ambassadorId", and even though we didn't tell people about "ambassadorId"
                it's what the web policy console generated because of jsonpb.  So
                Hosts with 'ambassadorId' exist in the wild.
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            ambassador_id:
              description: Common to all Ambassador objects (and optional).
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            hostname:
              description: Hostname by which the Ambassador can be reached.
              type: string
            previewUrl:
              description: Configuration for the Preview URL feature of Service Preview.
                Defaults to preview URLs not enabled.
              properties:
                enabled:
                  description: Is the Preview URL feature enabled?
                  type: boolean
                type:
                  description: What type of Preview URL is allowed?
                  enum:
                  - path
                  type: string
              type: object
            requestPolicy:
              description: Request policy definition.
              properties:
                insecure:
                  properties:
                    action:
                      enum:
                      - Redirect
                      - Reject
                      - Route
                      type: string
                    additionalPort:
                      type: integer
                  type: object
              type: object
            selector:
              description: Selector by which we can find further configuration. Defaults
                to hostname=$hostname
              properties:
                matchExpressions:
                  description: matchExpressions is a list of label selector requirements.
                    The requirements are ANDed.
                  items:
                    description: A label selector requirement is a selector that contains
                      values, a key, and an operator that relates the key and values.
                    properties:
                      key:
                        description: key is the label key that the selector applies
                          to.
                        type: string
                      operator:
                        description: operator represents a key's relationship to a
                          set of values. Valid operators are In, NotIn, Exists and
                          DoesNotExist.
                        type: string
                      values:
                        description: values is an array of string values. If the operator
                          is In or NotIn, the values array must be non-empty. If the
                          operator is Exists or DoesNotExist, the values array must
                          be empty. This array is replaced during a strategic merge
                          patch.
                        items:
                          type: string
                        type: array
                    required:
                    - key
                    - operator
                    type: object
                  type: array
                matchLabels:
                  additionalProperties:
                    type: string
                  description: matchLabels is a map of {key,value} pairs. A single
                    {key,value} in the matchLabels map is equivalent to an element
                    of matchExpressions, whose key field is "key", the operator is
                    "In", and the values array contains only "value". The requirements
                    are ANDed.
                  type: object
              type: object
            tls:
              description: TLS configuration.  It is not valid to specify both `tlsContext`
                and `tls`.
              properties:
                alpn_protocols:
                  type: string
                ca_secret:
                  type: string
                cacert_chain_file:
                  type: string
                cert_chain_file:
                  type: string
                cert_required:
                  type: boolean
                cipher_suites:
                  items:
                    type: string
                  type: array
                ecdh_curves:
                  items:
                    type: string
                  type: array
                max_tls_version:
                  type: string
                min_tls_version:
                  type: string
                private_key_file:
                  type: string
                redirect_cleartext_from:
                  type: integer
                sni:
                  type: string
              type: object
            tlsContext:
              description: Name of the TLSContext the Host resource is linked with.
                It is not valid to specify both `tlsContext` and `tls`.
              properties:
                name:
                  description: 'Name of the referent. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names
                    TODO: Add other useful fields. apiVersion, kind, uid?'
                  type: string
              type: object
            tlsSecret:
              description: Name of the Kubernetes secret into which to save generated
                certificates.  If ACME is enabled (see $acmeProvider), then the default
                is $hostname; otherwise the default is "".  If the value is "", then
                we do not do TLS for this Host.
              properties:
                name:
                  description: 'Name of the referent. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names
                    TODO: Add other useful fields. apiVersion, kind, uid?'
                  type: string
              type: object
          type: object
        status:
          description: HostStatus defines the observed state of Host
          properties:
            errorBackoff:
              type: string
            errorReason:
              description: errorReason, errorTimestamp, and errorBackoff are valid
                when state==Error.
              type: string
            errorTimestamp:
              format: date-time
              type: string
            phaseCompleted:
              description: phaseCompleted and phasePending are valid when state==Pending
                or state==Error.
              enum:
              - NA
              - DefaultsFilled
              - ACMEUserPrivateKeyCreated
              - ACMEUserRegistered
              - ACMECertificateChallenge
              type: string
            phasePending:
              description: phaseCompleted and phasePending are valid when state==Pending
                or state==Error.
              enum:
              - NA
              - DefaultsFilled
              - ACMEUserPrivateKeyCreated
              - ACMEUserRegistered
              - ACMECertificateChallenge
              type: string
            state:
              enum:
              - Initial
              - Pending
              - Ready
              - Error
              type: string
            tlsCertificateSource:
              enum:
              - Unknown
              - None
              - Other
              - ACME
              type: string
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: kubernetesendpointresolvers.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: KubernetesEndpointResolver
    listKind: KubernetesEndpointResolverList
    plural: kubernetesendpointresolvers
    singular: kubernetesendpointresolver
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: KubernetesEndpointResolver is the Schema for the kubernetesendpointresolver
        API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: KubernetesEndpointResolver tells Ambassador to use Kubernetes
            Endpoints resources to resolve services. It actually has no spec other
            than the AmbassadorID.
          properties:
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: kubernetesserviceresolvers.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: KubernetesServiceResolver
    listKind: KubernetesServiceResolverList
    plural: kubernetesserviceresolvers
    singular: kubernetesserviceresolver
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: KubernetesServiceResolver is the Schema for the kubernetesserviceresolver
        API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: KubernetesServiceResolver tells Ambassador to use Kubernetes
            Service resources to resolve services. It actually has no spec other than
            the AmbassadorID.
          properties:
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: logservices.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: LogService
    listKind: LogServiceList
    plural: logservices
    singular: logservice
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: LogService is the Schema for the logservices API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: LogServiceSpec defines the desired state of LogService
          properties:
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            driver:
              enum:
              - tcp
              - http
              type: string
            driver_config:
              properties:
                additional_log_headers:
                  items:
                    properties:
                      during_request:
                        type: boolean
                      during_response:
                        type: boolean
                      during_trailer:
                        type: boolean
                      header_name:
                        type: string
                    type: object
                  type: array
              type: object
            flush_interval_byte_size:
              type: integer
            flush_interval_time:
              type: integer
            grpc:
              type: boolean
            service:
              type: string
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: mappings.getambassador.io
spec:
  additionalPrinterColumns:
  - JSONPath: .spec.prefix
    name: Prefix
    type: string
  - JSONPath: .spec.service
    name: Service
    type: string
  - JSONPath: .status.state
    name: State
    type: string
  - JSONPath: .status.reason
    name: Reason
    type: string
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: Mapping
    listKind: MappingList
    plural: mappings
    singular: mapping
  scope: Namespaced
  subresources:
    status: {}
  validation:
    openAPIV3Schema:
      description: Mapping is the Schema for the mappings API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: MappingSpec defines the desired state of Mapping
          properties:
            add_linkerd_headers:
              type: boolean
            add_request_headers:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
                - type: object
              type: object
            add_response_headers:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
                - type: object
              type: object
            allow_upgrade:
              description: "A case-insensitive list of the non-HTTP protocols to allow\
                \ \"upgrading\" to from HTTP via the \"Connection: upgrade\" mechanism[1].\
                \  After the upgrade, Ambassador does not interpret the traffic, and\
                \ behaves similarly to how it does for TCPMappings. \n [1]: https://tools.ietf.org/html/rfc7230#section-6.7\
                \ \n For example, if your upstream service supports WebSockets, you\
                \ would write \n    allow_upgrade:    - websocket \n Or if your upstream\
                \ service supports upgrading from HTTP to SPDY (as the Kubernetes\
                \ apiserver does for `kubectl exec` functionality), you would write\
                \ \n    allow_upgrade:    - spdy/3.1"
              items:
                type: string
              type: array
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            auto_host_rewrite:
              type: boolean
            bypass_auth:
              type: boolean
            case_sensitive:
              type: boolean
            circuit_breakers:
              items:
                properties:
                  max_connections:
                    type: integer
                  max_pending_requests:
                    type: integer
                  max_requests:
                    type: integer
                  max_retries:
                    type: integer
                  priority:
                    enum:
                    - default
                    - high
                    type: string
                type: object
              type: array
            cluster_idle_timeout_ms:
              type: integer
            cluster_tag:
              type: string
            connect_timeout_ms:
              type: integer
            cors:
              properties:
                credentials:
                  type: boolean
                exposed_headers:
                  items:
                    type: string
                  oneOf:
                  - type: string
                  - type: array
                headers:
                  items:
                    type: string
                  oneOf:
                  - type: string
                  - type: array
                max_age:
                  type: string
                methods:
                  items:
                    type: string
                  oneOf:
                  - type: string
                  - type: array
                origins:
                  items:
                    type: string
                  oneOf:
                  - type: string
                  - type: array
              type: object
            enable_ipv4:
              type: boolean
            enable_ipv6:
              type: boolean
            envoy_override:
              description: UntypedDict is non-functional as a Go type, but it gets
                controller-gen to spit out the correct schema.
              type: object
            grpc:
              type: boolean
            headers:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            host:
              type: string
            host_redirect:
              type: boolean
            host_regex:
              type: boolean
            host_rewrite:
              type: string
            idle_timeout_ms:
              type: integer
            keepalive:
              properties:
                idle_time:
                  type: integer
                interval:
                  type: integer
                probes:
                  type: integer
              type: object
            labels:
              additionalProperties: {}
              description: 'Python: MappingLabels = Dict[str, Union[str,''MappingLabels'']]'
              type: object
            load_balancer:
              properties:
                cookie:
                  properties:
                    name:
                      type: string
                    path:
                      type: string
                    ttl:
                      type: string
                  required:
                  - name
                  type: object
                header:
                  type: string
                policy:
                  enum:
                  - round_robin
                  - ring_hash
                  - maglev
                  - least_request
                  type: string
                source_ip:
                  type: boolean
              required:
              - policy
              type: object
            method:
              type: string
            method_regex:
              type: boolean
            modules:
              items:
                description: UntypedDict is non-functional as a Go type, but it gets
                  controller-gen to spit out the correct schema.
                type: object
              type: array
            outlier_detection:
              type: string
            path_redirect:
              type: string
            precedence:
              type: integer
            prefix:
              type: string
            prefix_exact:
              type: boolean
            prefix_regex:
              type: boolean
            priority:
              type: string
            query_parameters:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            regex_headers:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            regex_query_parameters:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            regex_rewrite:
              additionalProperties:
                oneOf:
                - type: string
                - type: boolean
              type: object
            remove_request_headers:
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            remove_response_headers:
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            resolver:
              type: string
            retry_policy:
              properties:
                num_retries:
                  type: integer
                per_try_timeout:
                  type: string
                retry_on:
                  enum:
                  - 5xx
                  - gateway-error
                  - connect-failure
                  - retriable-4xx
                  - refused-stream
                  - retriable-status-codes
                  type: string
              type: object
            rewrite:
              type: string
            service:
              type: string
            shadow:
              type: boolean
            timeout_ms:
              type: integer
            tls:
              oneOf:
              - type: string
              - type: boolean
            use_websocket:
              description: 'use_websocket is deprecated, and is equivlaent to setting
                `allow_upgrade: ["websocket"]`'
              type: boolean
            weight:
              type: integer
          type: object
        status:
          description: MappingStatus defines the observed state of Mapping
          properties:
            reason:
              type: string
            state:
              enum:
              - ''
              - Inactive
              - Running
              type: string
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: modules.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: Module
    listKind: ModuleList
    plural: modules
    singular: module
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: "A Module defines system-wide configuration.  The type of module\
        \ is controlled by the .metadata.name; valid names are \"ambassador\" or \"\
        tls\". \n https://www.getambassador.io/docs/latest/topics/running/ambassador/#the-ambassador-module\
        \ https://www.getambassador.io/docs/latest/topics/running/tls/#tls-module-deprecated"
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          properties:
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            config:
              description: UntypedDict is non-functional as a Go type, but it gets
                controller-gen to spit out the correct schema.
              type: object
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: ratelimitservices.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: RateLimitService
    listKind: RateLimitServiceList
    plural: ratelimitservices
    singular: ratelimitservice
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: RateLimitService is the Schema for the ratelimitservices API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: RateLimitServiceSpec defines the desired state of RateLimitService
          properties:
            ambassador_id:
              description: Common to all Ambassador objects.
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            domain:
              type: string
            service:
              type: string
            timeout_ms:
              type: integer
            tls:
              oneOf:
              - type: string
              - type: boolean
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: tcpmappings.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: TCPMapping
    listKind: TCPMappingList
    plural: tcpmappings
    singular: tcpmapping
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: TCPMapping is the Schema for the tcpmappings API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: TCPMappingSpec defines the desired state of TCPMapping
          properties:
            address:
              type: string
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            circuit_breakers:
              items:
                properties:
                  max_connections:
                    type: integer
                  max_pending_requests:
                    type: integer
                  max_requests:
                    type: integer
                  max_retries:
                    type: integer
                  priority:
                    enum:
                    - default
                    - high
                    type: string
                type: object
              type: array
            cluster_tag:
              type: string
            enable_ipv4:
              type: boolean
            enable_ipv6:
              type: boolean
            host:
              type: string
            idle_timeout_ms:
              description: 'Surely this should be an ''int''?'
              type: string
            port:
              type: integer
            resolver:
              type: string
            service:
              type: string
            tls:
              oneOf:
              - type: string
              - type: boolean
            weight:
              type: integer
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: tlscontexts.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: TLSContext
    listKind: TLSContextList
    plural: tlscontexts
    singular: tlscontext
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: TLSContext is the Schema for the tlscontexts API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: TLSContextSpec defines the desired state of TLSContext
          properties:
            alpn_protocols:
              type: string
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            ca_secret:
              type: string
            cacert_chain_file:
              type: string
            cert_chain_file:
              type: string
            cert_required:
              type: boolean
            cipher_suites:
              items:
                type: string
              type: array
            ecdh_curves:
              items:
                type: string
              type: array
            hosts:
              items:
                type: string
              type: array
            max_tls_version:
              enum:
              - v1.0
              - v1.1
              - v1.2
              - v1.3
              type: string
            min_tls_version:
              enum:
              - v1.0
              - v1.1
              - v1.2
              - v1.3
              type: string
            private_key_file:
              type: string
            redirect_cleartext_from:
              type: integer
            secret:
              type: string
            secret_namespacing:
              type: boolean
            sni:
              type: string
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations:
    controller-gen.kubebuilder.io/version: v0.3.1-0.20200517180335-820a4a27ea84
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: tracingservices.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: TracingService
    listKind: TracingServiceList
    plural: tracingservices
    singular: tracingservice
  scope: Namespaced
  validation:
    openAPIV3Schema:
      description: TracingService is the Schema for the tracingservices API
      properties:
        apiVersion:
          description: 'APIVersion defines the versioned schema of this representation
            of an object. Servers should convert recognized schemas to the latest
            internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
          type: string
        kind:
          description: 'Kind is a string value representing the REST resource this
            object represents. Servers may infer this from the endpoint the client
            submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
          type: string
        metadata:
          type: object
        spec:
          description: TracingServiceSpec defines the desired state of TracingService
          properties:
            ambassador_id:
              description: "AmbassadorID declares which Ambassador instances should\
                \ pay attention to this resource.  May either be a string or a list\
                \ of strings.  If no value is provided, the default is: \n    ambassador_id:\
                \    - \"default\""
              items:
                type: string
              oneOf:
              - type: string
              - type: array
            config:
              properties:
                access_token_file:
                  type: string
                collector_cluster:
                  type: string
                collector_endpoint:
                  type: string
                service_name:
                  type: string
                shared_span_context:
                  type: boolean
                trace_id_128bit:
                  type: boolean
              type: object
            driver:
              enum:
              - lightstep
              - zipkin
              - datadog
              type: string
            sampling:
              properties:
                client:
                  type: integer
                overall:
                  type: integer
                random:
                  type: integer
              type: object
            service:
              type: string
            tag_headers:
              items:
                type: string
              type: array
          type: object
      type: object
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: filterpolicies.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: FilterPolicy
    plural: filterpolicies
    shortNames:
    - fp
    singular: filterpolicy
  scope: Namespaced
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1beta2
    served: true
    storage: false
  - name: v1beta1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: filters.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: Filter
    plural: filters
    shortNames:
    - fil
    singular: filter
  scope: Namespaced
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1beta2
    served: true
    storage: false
  - name: v1beta1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: ratelimits.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: RateLimit
    plural: ratelimits
    shortNames:
    - rl
    singular: ratelimit
  scope: Namespaced
  version: null
  versions:
  - name: v2
    served: true
    storage: true
  - name: v1beta2
    served: true
    storage: false
  - name: v1beta1
    served: true
    storage: false
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: projectcontrollers.getambassador.io
spec:
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: ProjectController
    plural: projectcontrollers
    singular: projectcontroller
  scope: Namespaced
  subresources:
    status: {}
  version: null
  versions:
  - name: v2
    served: true
    storage: true
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: projects.getambassador.io
spec:
  additionalPrinterColumns:
  - JSONPath: .spec.prefix
    name: Prefix
    type: string
  - JSONPath: .spec.githubRepo
    name: Repo
    type: string
  - JSONPath: .metadata.creationTimestamp
    name: Age
    type: date
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: Project
    plural: projects
    singular: project
  scope: Namespaced
  subresources:
    status: {}
  version: null
  versions:
  - name: v2
    served: true
    storage: true
---
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  annotations: {}
  labels:
    app.kubernetes.io/name: ambassador
    product: aes
  name: projectrevisions.getambassador.io
spec:
  additionalPrinterColumns:
  - JSONPath: .spec.project.name
    name: Project
    type: string
  - JSONPath: .spec.ref
    name: Ref
    type: string
  - JSONPath: .spec.rev
    name: Rev
    type: string
  - JSONPath: .status.phase
    name: Status
    type: string
  - JSONPath: .metadata.creationTimestamp
    name: Age
    type: date
  group: getambassador.io
  names:
    categories:
    - ambassador-crds
    kind: ProjectRevision
    plural: projectrevisions
    singular: projectrevision
  scope: Namespaced
  subresources:
    status: {}
  version: null
  versions:
  - name: v2
    served: true
    storage: true
"""

ambassador_edge_stack_yaml = r"""
######################################################################
# 'ambassador' namespace.
---
apiVersion: v1
kind: Namespace
metadata:
  name: ambassador
  labels:
    product: aes

######################################################################
# RBAC
# NB: ClusterRoles and ClusterRoleBindings are not namespaced
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ambassador
  namespace: ambassador
  labels:
    product: aes


# Edge Stack mostly needs the same permissions as Ambassador OSS,
# but:
#  1. It needs extra permissions ("update"/"patch"/"create"/"delete")
#     for getambassador.io resources.
#  2. It needs extra permissions ("create"/"update") for secrets.
#  3. It needs permission to "create" events.
#  4. It needs permission to "get"/"create"/"update" Leases (or
#     Endpoints, if on Kubernetes <1.12).
#
# Note: If you edit this, be sure to also edit the pytest
# `manifests/rbac_*_scope.yaml` files.
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  name: ambassador
  labels:
    product: aes
rules:
- apiGroups: [ "apiextensions.k8s.io" ]
  resources: [ "customresourcedefinitions" ]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: [ "namespaces", "services", "pods" ]
  verbs: ["get", "list", "watch"]
- apiGroups: [ "getambassador.io" ]
  resources: [ "*" ]
  verbs: ["get", "list", "watch", "update", "patch", "create", "delete" ]
- apiGroups: [ "networking.internal.knative.dev" ]
  resources: [ "clusteringresses", "ingresses" ]
  verbs: ["get", "list", "watch"]
- apiGroups: [ "networking.internal.knative.dev" ]
  resources: [ "ingresses/status", "clusteringresses/status" ]
  verbs: ["update"]
- apiGroups: [ "extensions", "networking.k8s.io" ]
  resources: [ "ingresses" ]
  verbs: ["get", "list", "watch"]
- apiGroups: [ "extensions", "networking.k8s.io" ]
  resources: [ "ingresses/status" ]
  verbs: ["update"]
- apiGroups: [""]
  resources: [ "secrets" ]
  verbs: ["get", "list", "watch", "create", "update"]
- apiGroups: [""]
  resources: [ "events" ]
  verbs: ["get", "list", "watch", "create"]
- apiGroups: ["coordination.k8s.io"]
  resources: [ "leases" ]
  verbs: ["get", "create", "update"]
- apiGroups: [""]
  resources: [ "endpoints" ]
  verbs: ["get", "list", "watch", "create", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: ambassador
  labels:
    product: aes
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ambassador
subjects:
- kind: ServiceAccount
  name: ambassador
  namespace: ambassador

######################################################################
# Project RBAC
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRole
metadata:
  name: ambassador-projects
  labels:
    product: aes
rules:
- apiGroups: [""]
  resources: [ "secrets", "services" ]
  verbs: [ "get", "list", "create", "patch", "delete", "watch" ]
- apiGroups: ["apps"]
  resources: [ "deployments" ]
  verbs: [ "get", "list", "create", "patch", "delete", "watch" ]
- apiGroups: ["batch"]
  resources: [ "jobs" ]
  verbs: [ "get", "list", "create", "patch", "delete", "watch" ]
- apiGroups: [""]
  resources: [ "pods" ]
  verbs: [ "get", "list", "watch" ]
- apiGroups: [""]
  resources: [ "pods/log" ]
  verbs: [ "get" ]
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: ambassador-projects
  labels:
    product: aes
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ambassador-projects
subjects:
- kind: ServiceAccount
  name: ambassador
  namespace: ambassador

######################################################################
# Redis
---
apiVersion: v1
kind: Service
metadata:
  name: ambassador-redis
  namespace: ambassador
  labels:
    product: aes
spec:
  type: ClusterIP
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    service: ambassador-redis
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ambassador-redis
  namespace: ambassador
  labels:
    product: aes
spec:
  replicas: 1
  selector:
    matchLabels:
      service: ambassador-redis
  template:
    metadata:
      labels:
        service: ambassador-redis
    spec:
      containers:
      - name: redis
        image: redis:5.0.1
      restartPolicy: Always

######################################################################
# Configure Ambassador Edge Stack.
---
apiVersion: getambassador.io/v2
kind: RateLimitService
metadata:
  name: ambassador-edge-stack-ratelimit
  namespace: ambassador
  labels:
    product: aes
spec:
  service: "127.0.0.1:8500"
---
apiVersion: getambassador.io/v2
kind: AuthService
metadata:
  name: ambassador-edge-stack-auth
  namespace: ambassador
  labels:
    product: aes
spec:
  proto: grpc
  status_on_error:
    code: 504
  auth_service: "127.0.0.1:8500"
  allow_request_body: false # setting this to 'true' allows Plugin and External filters to access the body, but has performance overhead
---
apiVersion: v1
kind: Secret
metadata:
  name: ambassador-edge-stack
  namespace: ambassador
data:
  license-key: "" # This secret is just a placeholder, it is mounted as a volume and refreshed when changed

######################################################################
# Configure DevPortal
---
apiVersion: getambassador.io/v2
kind: Mapping
metadata:
  # This Mapping name is referenced by convention, it's important to leave as-is.
  name: ambassador-devportal
  namespace: ambassador
  labels:
    product: aes
spec:
  prefix: /docs/
  rewrite: "/docs/"
  service: "127.0.0.1:8500"
---
apiVersion: getambassador.io/v2
kind: Mapping
metadata:
  # This Mapping name is referenced by convention, it's important to leave as-is.
  name: ambassador-devportal-api
  namespace: ambassador
  labels:
    product: aes
spec:
  prefix: /openapi/
  rewrite: ""
  service: "127.0.0.1:8500"

######################################################################
# Create the 'ambassador' and 'ambassador-admin' Services.
---
apiVersion: v1
kind: Service
metadata:
  name: ambassador
  namespace: ambassador
  labels:
    product: aes
    app.kubernetes.io/component: ambassador-service
  annotations:
{annotations}
spec:
  type: LoadBalancer
  ports:
  - name: http
    port: 80
    targetPort: http
  - name: https
    port: 443
    targetPort: https
  selector:
    service: ambassador
---
apiVersion: v1
kind: Service
metadata:
  labels:
    service: ambassador-admin
    product: aes
  name: ambassador-admin
  namespace: ambassador
spec:
  type: ClusterIP
  ports:
  - name: ambassador-admin
    port: 8877
    targetPort: admin
  selector:
    service: ambassador

######################################################################
# Create the Deployment backing the 'ambassador' and
# 'ambassador-admin' Services.
---
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    product: aes
  name: ambassador
  namespace: ambassador
spec:
  replicas: 1
  selector:
    matchLabels:
      service: ambassador
  template:
    metadata:
      annotations:
        consul.hashicorp.com/connect-inject: 'false'
        sidecar.istio.io/inject: 'false'
      labels:
        app.kubernetes.io/managed-by: getambassador.io
        service: ambassador
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchLabels:
                  service: ambassador
              topologyKey: kubernetes.io/hostname
            weight: 100
      containers:
      - env:
        - name: AMBASSADOR_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: REDIS_URL
          value: ambassador-redis:6379
        - name: AMBASSADOR_URL
          value: https://ambassador.ambassador.svc.cluster.local
        - name: POLL_EVERY_SECS
          value: '0'
        - name: AMBASSADOR_INTERNAL_URL
          value: https://127.0.0.1:8443
        - name: AMBASSADOR_SINGLE_NAMESPACE
          value: ''
        image: docker.io/datawire/aes:1.6.2
        livenessProbe:
          httpGet:
            path: /ambassador/v0/check_alive
            port: 8877
          periodSeconds: 3
        name: aes
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8443
          name: https
        - containerPort: 8877
          name: admin
        readinessProbe:
          httpGet:
            path: /ambassador/v0/check_ready
            port: 8877
          periodSeconds: 3
        resources:
          limits:
            cpu: 1000m
            memory: 600Mi
          requests:
            cpu: 200m
            memory: 300Mi
        securityContext:
          allowPrivilegeEscalation: false
        volumeMounts:
        - mountPath: /tmp/ambassador-pod-info
          name: ambassador-pod-info
        - mountPath: /.config/ambassador
          name: ambassador-edge-stack-secrets
          readOnly: true
      restartPolicy: Always
      securityContext:
        runAsUser: 8888
      serviceAccountName: ambassador
      terminationGracePeriodSeconds: 0
      volumes:
      - downwardAPI:
          items:
          - fieldRef:
              fieldPath: metadata.labels
            path: labels
        name: ambassador-pod-info
      - name: ambassador-edge-stack-secrets
        secret:
          secretName: ambassador-edge-stack
"""

ambassador_host_yaml = r"""
apiVersion: getambassador.io/v2
kind: Host
metadata:
  name: spell-default
  namespace: ambassador
spec:
  hostname: {spell_domain_name}
  acmeProvider:
    authority: none
  tlsSecret:
    name: ambassador-certs
  requestPolicy:
    insecure:
      action: Route
"""

lets_encrypt_yaml = r"""
---
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    email: eng@spell.ml
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt
    solvers:
    - http01:
        ingress:
          class: nginx
      selector: {{}}
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: ambassador-certs
  namespace: ambassador
spec:
  secretName: ambassador-certs
  issuerRef:
    name: letsencrypt
    kind: ClusterIssuer
  dnsNames:
  - {spell_domain_name}
---
apiVersion: getambassador.io/v2
kind: Mapping
metadata:
  name: acme-challenge-mapping
  namespace: ambassador
spec:
  prefix: /.well-known/acme-challenge/
  rewrite: ""
  service: acme-challenge-service
---
apiVersion: v1
kind: Service
metadata:
  name: acme-challenge-service
  namespace: ambassador
spec:
  ports:
  - port: 80
    targetPort: 8089
  selector:
    acme.cert-manager.io/http01-solver: "true"
"""


def generate_ambassador_host_yaml(spell_domain_name):
    """
    Creates a 'host' resource that broadcasts configuration settings to ambassador.
    spell_domain_name: spell.services entry in Route 53 for this model server
    """
    return ambassador_host_yaml.format(spell_domain_name=spell_domain_name)


def generate_cert_manager_yaml(spell_domain_name):
    """Uses cert-manager to get letsencrypt TLS cert via the HTTP01 ACME challenge
    https://cert-manager.io/docs/configuration/acme/http01/
    https://www.getambassador.io/docs/latest/howtos/cert-manager/#http-01-challenge

    The cert is stored as a kube secret 'ambassador-certs'

    spell_domain_name: spell.services entry in Route 53 for this model server
    """

    return lets_encrypt_yaml.format(spell_domain_name=spell_domain_name)


def generate_main_ambassador_yaml(provider, is_external):
    """Configures provider-dependent settings for the Ambassdador Edge Stack."""
    if provider == "AWS" and is_external:
        service_annotations = r"""
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    """
    elif provider == "AWS" and not is_external:
        service_annotations = r"""
    service.beta.kubernetes.io/aws-load-balancer-internal: 0.0.0.0/0
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    """
    elif provider == "GCP" and is_external:
        service_annotations = ""
    elif provider == "GCP" and not is_external:
        service_annotations = r"""
    cloud.google.com/load-balancer-type: "Internal"
    """
    else:
        raise Exception("Unknown cloud provider {}".format(provider))

    return ambassador_edge_stack_yaml.format(annotations=service_annotations)
