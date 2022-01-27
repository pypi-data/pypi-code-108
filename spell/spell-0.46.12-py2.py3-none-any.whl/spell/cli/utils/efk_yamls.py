# HACK: Suppress E501 Line Too Long across this file
# flake8: noqa

# See https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-deploy-elasticsearch.html
# with PVC updates from https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-volume-claim-templates.html
# and performance updates from https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-virtual-memory.html
elasticsearch_yaml = """
---
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: serverlogs
  namespace: elastic-system
spec:
  version: 7.9.2
  nodeSets:
  - name: default
    count: 1
    config:
      node.master: true
      node.data: true
      node.ingest: true
      xpack.security.authc:
        anonymous:
          username: anonymous
          roles: superuser
          authz_exception: false
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 50Gi
    podTemplate:
      spec:
        initContainers:
        - name: sysctl
          securityContext:
            privileged: true
          command: ['sh', '-c', 'sysctl -w vm.max_map_count=262144']
"""

# See https://www.elastic.co/guide/en/cloud-on-k8s/current/k8s-deploy-kibana.html
kibana_yaml = """
---
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: serverlogs
  namespace: elastic-system
spec:
  version: 7.9.3
  count: 1
  elasticsearchRef:
    name: serverlogs
"""

# Elasticsearch 7.0 uses msec timestamps by default. The @timestamp field must be
# explicitly configured to use nsec resolution
fluentd_elasticsearch_plugin_yaml = """
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-elasticsearch-plugin-config
  namespace: elastic-system
data:
  time-nano-template.json: |
    {
      "index_patterns": ["logstash-*"],
      "template": {
        "mappings": {
          "properties": {
            "@timestamp": {
              "type": "date_nanos" 
            }
          }
        }
      }
    }
"""

# See https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/fluentd-daemonset-elasticsearch.yaml
# for daemon set yaml source
# See https://medium.com/kubernetes-tutorials/cluster-level-logging-in-kubernetes-with-fluentd-e59aa2b6093a
# for RBAC and custom configmap updates
# See .conf file documentation inline below
fluentd_configmap_yaml = """
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: elastic-system
data:
  kubernetes.conf: |
    ## Copied from https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/templates/conf/kubernetes.conf.erb

    <label @FLUENT_LOG>
        <match fluent.**>
        @type null
        @id ignore_fluent_logs
        </match>
    </label>

    <source>
        @type tail
        @id in_tail_container_logs
        path /var/log/containers/*.log
        pos_file /var/log/fluentd-containers.log.pos
        tag "#{ENV['FLUENT_CONTAINER_TAIL_TAG'] || 'kubernetes.*'}"
        exclude_path "#{ENV['FLUENT_CONTAINER_TAIL_EXCLUDE_PATH'] || use_default}"
        read_from_head true
        <parse>
        @type "#{ENV['FLUENT_CONTAINER_TAIL_PARSER_TYPE'] || 'json'}"
        time_format %Y-%m-%dT%H:%M:%S.%NZ
        </parse>
    </source>

    <filter kubernetes.**>
        @type kubernetes_metadata
        @id filter_kube_metadata
        kubernetes_url "#{ENV['FLUENT_FILTER_KUBERNETES_URL'] || 'https://' + ENV.fetch('KUBERNETES_SERVICE_HOST') + ':' + ENV.fetch('KUBERNETES_SERVICE_PORT') + '/api'}"
        verify_ssl "#{ENV['KUBERNETES_VERIFY_SSL'] || true}"
        ca_file "#{ENV['KUBERNETES_CA_FILE']}"
        skip_labels "#{ENV['FLUENT_KUBERNETES_METADATA_SKIP_LABELS'] || 'false'}"
        skip_container_metadata "#{ENV['FLUENT_KUBERNETES_METADATA_SKIP_CONTAINER_METADATA'] || 'false'}"
        skip_master_url "#{ENV['FLUENT_KUBERNETES_METADATA_SKIP_MASTER_URL'] || 'false'}"
        skip_namespace_metadata "#{ENV['FLUENT_KUBERNETES_METADATA_SKIP_NAMESPACE_METADATA'] || 'false'}"
    </filter>

  fluent.conf: |
    ## Can see the source under case 'elasticsearch7' in
    ## https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/templates/conf/fluent.conf.erb

    @include kubernetes.conf

    # Remove Prometheus GET metric requests. These come in two flavors:
    # GET /metrics 1.1 307 - - Prometheus/2.20.0
    # GET / 1.1 200 580 http://10.0.70.222:8000/metrics Prometheus/2.20.0
    <filter **>
        @type grep

        <exclude>
            key log
            pattern /.*GET \/metrics .*|.*GET \/metrics\/ .*|.*GET \/ .*/
        </exclude>
    </filter>

    # Rate limit
    <filter kubernetes.**>
        @type throttle

        group_key               pod_name
        group_bucket_period_s   1
        group_bucket_limit      1000
        group_reset_rate_s      -1
        group_warning_delay_s   60
    </filter>

    # forward relevant serving logs to the spell elasticsearch
    # the format of the regexp comes from the tail filter in kubernetes.conf
    # to get a match for pod PODNAME-PODHASH in namespace NAMESPACE, use the regexp
    # /^kubernetes.var.log.containers.PODNAME-.+_NAMESPACE_.*/
    # in the match expressiong
    <match /^kubernetes.var.log.containers.model-serving-.+_serving_.*/ /^kubernetes.var.log.containers.model-serving-.+_spell-serving_.*/ /^kubernetes.var.log.containers.ambassador-.+_ambassador_.*/>
        @type elasticsearch
        @id out_es
        @log_level info
        include_tag_key true
        host "#{ENV['FLUENT_ELASTICSEARCH_HOST']}"
        port "#{ENV['FLUENT_ELASTICSEARCH_PORT']}"
        path "#{ENV['FLUENT_ELASTICSEARCH_PATH']}"
        scheme "#{ENV['FLUENT_ELASTICSEARCH_SCHEME'] || 'http'}"
        ssl_verify "#{ENV['FLUENT_ELASTICSEARCH_SSL_VERIFY'] || 'true'}"
        ssl_version "#{ENV['FLUENT_ELASTICSEARCH_SSL_VERSION'] || 'TLSv1_2'}"
        user "#{ENV['FLUENT_ELASTICSEARCH_USER'] || use_default}"
        password "#{ENV['FLUENT_ELASTICSEARCH_PASSWORD'] || use_default}"
        reload_connections "#{ENV['FLUENT_ELASTICSEARCH_RELOAD_CONNECTIONS'] || 'false'}"
        reconnect_on_error "#{ENV['FLUENT_ELASTICSEARCH_RECONNECT_ON_ERROR'] || 'true'}"
        reload_on_failure "#{ENV['FLUENT_ELASTICSEARCH_RELOAD_ON_FAILURE'] || 'true'}"
        log_es_400_reason "#{ENV['FLUENT_ELASTICSEARCH_LOG_ES_400_REASON'] || 'false'}"
        logstash_prefix "#{ENV['FLUENT_ELASTICSEARCH_LOGSTASH_PREFIX'] || 'logstash'}"
        logstash_dateformat "#{ENV['FLUENT_ELASTICSEARCH_LOGSTASH_DATEFORMAT'] || '%Y.%m.%d'}"
        logstash_format "#{ENV['FLUENT_ELASTICSEARCH_LOGSTASH_FORMAT'] || 'true'}"
        index_name "#{ENV['FLUENT_ELASTICSEARCH_LOGSTASH_INDEX_NAME'] || 'logstash'}"
        type_name "#{ENV['FLUENT_ELASTICSEARCH_LOGSTASH_TYPE_NAME'] || 'fluentd'}"
        include_timestamp "#{ENV['FLUENT_ELASTICSEARCH_INCLUDE_TIMESTAMP'] || 'false'}"
        template_name default
        template_file /elasticsearch-plugin/time-nano-template.json
        template_overwrite "#{ENV['FLUENT_ELASTICSEARCH_TEMPLATE_OVERWRITE'] || use_default}"
        sniffer_class_name "#{ENV['FLUENT_SNIFFER_CLASS_NAME'] || 'Fluent::Plugin::ElasticsearchSimpleSniffer'}"
        request_timeout "#{ENV['FLUENT_ELASTICSEARCH_REQUEST_TIMEOUT'] || '5s'}"
        suppress_type_name "#{ENV['FLUENT_ELASTICSEARCH_SUPPRESS_TYPE_NAME'] || 'true'}"
        enable_ilm "#{ENV['FLUENT_ELASTICSEARCH_ENABLE_ILM'] || 'false'}"
        ilm_policy_id "#{ENV['FLUENT_ELASTICSEARCH_ILM_POLICY_ID'] || use_default}"
        ilm_policy "#{ENV['FLUENT_ELASTICSEARCH_ILM_POLICY'] || use_default}"
        ilm_policy_overwrite "#{ENV['FLUENT_ELASTICSEARCH_ILM_POLICY_OVERWRITE'] || 'false'}"
        <buffer>
        flush_thread_count "#{ENV['FLUENT_ELASTICSEARCH_BUFFER_FLUSH_THREAD_COUNT'] || '8'}"
        flush_interval "#{ENV['FLUENT_ELASTICSEARCH_BUFFER_FLUSH_INTERVAL'] || '5s'}"
        chunk_limit_size "#{ENV['FLUENT_ELASTICSEARCH_BUFFER_CHUNK_LIMIT_SIZE'] || '2M'}"
        queue_limit_length "#{ENV['FLUENT_ELASTICSEARCH_BUFFER_QUEUE_LIMIT_LENGTH'] || '32'}"
        retry_max_interval "#{ENV['FLUENT_ELASTICSEARCH_BUFFER_RETRY_MAX_INTERVAL'] || '30'}"
        retry_forever true
        </buffer>
    </match>
"""

fluentd_yaml = """
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: elastic-system

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
  namespace: elastic-system
rules:
  - apiGroups:
      - ""
    resources:
      - pods
      - namespaces
    verbs:
      - get
      - list
      - watch

---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: fluentd
roleRef:
  kind: ClusterRole
  name: fluentd
  apiGroup: rbac.authorization.k8s.io
subjects:
  - kind: ServiceAccount
    name: fluentd
    namespace: elastic-system

---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: elastic-system
  labels:
    k8s-app: fluentd-logging
    version: v1
spec:
  selector:
    matchLabels:
      k8s-app: fluentd-logging
      version: v1
  template:
    metadata:
      labels:
        k8s-app: fluentd-logging
        version: v1
    spec:
      serviceAccount: fluentd
      serviceAccountName: fluentd
      containers:
        - name: fluentd
          image: fluent/fluentd-kubernetes-daemonset:v1.11.4-debian-elasticsearch7-1.0
          command:
            - /bin/sh
          args:
            - -c
            - gem install fluent-plugin-s3 fluent-plugin-throttle && echo hi && tini -- /fluentd/entrypoint.sh
          env:
            - name: FLUENT_ELASTICSEARCH_HOST
              value: "serverlogs-es-default"
            - name: FLUENT_ELASTICSEARCH_PORT
              value: "9200"
            - name: FLUENT_ELASTICSEARCH_SCHEME
              value: "https"
            - name: FLUENT_ELASTICSEARCH_SSL_VERIFY
              value: "false"
            - name: FLUENT_ELASTICSEARCH_SSL_VERSION
              value: "TLSv1_2"
            - name: FLUENT_ELASTICSEARCH_USER
              value: "elastic"
            - name: FLUENT_ELASTICSEARCH_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: serverlogs-es-elastic-user
                  key: elastic
          resources:
            limits:
              memory: 200Mi
            requests:
              cpu: 100m
              memory: 200Mi
          volumeMounts:
            - name: config-elasticsearch
              mountPath: /elasticsearch-plugin
            - name: config-volume
              mountPath: /fluentd/etc
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
        - name: config-elasticsearch
          configMap:
            defaultMode: 420
            name: fluentd-elasticsearch-plugin-config
        - name: config-volume
          configMap:
            name: fluentd-config
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
"""


curator_yaml = """
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: curator-config
  namespace: elastic-system
data:
  action_file.yml: |-
    ---
    actions:
      1:
        action: delete_indices
        description: >-
          Delete indices when the cluster disk space has exceeded 80% usage (40 of 50 GB).
          The first filter makes sure we do not delete the .kibana index which is used by
          kibana to store display info like what field to use as the timestamp.
          Ignore the error if the filter does not result in an actionable list of indices
          (ignore_empty_list) and exit cleanly.
        options:
          ignore_empty_list: True
          timeout_override:
          continue_if_exception: False
          disable_action: False
        filters:
        - filtertype: pattern
          kind: prefix
          value: logstash-
        - filtertype: space
          disk_space: 40
          use_age: True
          source: creation_date

  config.yml: |
    client:
      hosts:
        -  serverlogs-es-default
      port: 9200
      use_ssl: True
      ssl_no_validate: True
      http_auth: ${ES_AUTH}
---
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: elasticsearch-curator
  namespace: elastic-system
spec:
  # Scheduled hourly
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: elasticsearch-curator
        spec:
          volumes:
            - name: config-volume
              configMap:
                name: curator-config
          restartPolicy: Never
          containers:
            - name: elasticsearch-curator
              image: "bitnami/elasticsearch-curator:5.8.1"
              imagePullPolicy: IfNotPresent
              volumeMounts:
                - name: config-volume
                  mountPath: /etc/es-curator
              command: ["curator"]
              args:
                [
                  "--config",
                  "/etc/es-curator/config.yml",
                  "/etc/es-curator/action_file.yml",
                ]
              env:
                - name: ES_PASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: serverlogs-es-elastic-user
                      key: elastic
                - name: ES_AUTH
                  value: elastic:$(ES_PASSWORD)
"""
