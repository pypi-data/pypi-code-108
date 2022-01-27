# HACK: Suppress E501 Line Too Long across this file
# flake8: noqa

fluentd_configmap_yaml_runs = """
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
    <filter /^kubernetes.var.log.containers.model-serving-.+_serving_.*/ /^kubernetes.var.log.containers.model-serving-.+_spell-serving_.*/>
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

    # Rewrites the tag from Runs to `spell.user.**`, blocks below reflect this new tag
    # The spell.user prefix is required so the spell stack's runlog can send runlogs to the correct kafka topic
    <match /^kubernetes.var.log.containers.spell-run-.+_spell-run_.*/>
      @type rewrite_tag_filter
      <rule>
        key     log
        pattern /(.+)/
        tag spell.user.${tag}
      </rule>
    </match>

    # Note: For easy testing, pipe logs to stdout and tail the logs of the fluentd pods (in elastic-system)
    # <match spell.user.**>
    #  @type stdout
    # </match>

    # rewrite fields of spell.user logs
    <filter spell.user.**>
      @type record_modifier
      <record>
        run_id ${record.dig("kubernetes", "labels", "run_id")}
        container_name ${record.dig("kubernetes", "container_name")}
        log ${record["log"].rstrip}
      </record>
      remove_keys docker,kubernetes
    </filter>

    # filter out nuisance logs from Argo workflow wait containers
    <filter spell.user.**>
      @type grep
      <exclude>
        key container_name
        pattern /wait/
      </exclude>
    </filter>

    # send processed spell run logs to Spell via autossh
    <match spell.user.**>
      @type forward
      heartbeat_type none
      <buffer>
        @type memory
        flush_interval 1s
      </buffer>
      <server>
        host autossh.spell-run.svc.cluster.local
        port 24224
      </server>
    </match>

    # forward relevant serving logs to the spell elasticsearch
    # the format of the regexp comes from the tail filter in kubernetes.conf
    # to get a match for pod PODNAME-PODHASH in namespace NAMESPACE, use the regexp
    # /^kubernetes.var.log.containers.PODNAME-.+_NAMESPACE_.*/
    # in the match expression
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

    ## Throw away all unmatched logs. We only keep `model-serving-*`, `spell-model-serving-*` and `spell-run-*`
    <match **>
      @type null
    </match>
"""

autossh_yaml = """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autossh
  labels:
    k8s-app: spell
spec:
  replicas: 2
  selector:
    matchLabels:
      name: autossh
      k8s-app: spell
  template:
    metadata:
      labels:
        name: autossh
        k8s-app: spell
    spec:
      containers:
      - name: autossh
        image: spellrun/autossh{}
        ports:
        - protocol: TCP
          containerPort: 24224
          name: logs
        - protocol: TCP
          containerPort: 24225
          name: ws-logs
        - protocol: TCP
          containerPort: 29193
          name: metrics-local
        - protocol: TCP
          containerPort: 32190
          name: metrics1
        - protocol: TCP
          containerPort: 32191
          name: metrics2
        - protocol: TCP
          containerPort: 32192
          name: metrics3
        env:
        - name: KAFKA_BROKER_PORTS
          value: "{}"
        - name: TCPPROXY_HOST
          value: "{}"
        - name: SSH_BASTION_HOST
          valueFrom:
            secretKeyRef:
              name: autossh
              key: ssh_bastion_host
        - name: SSH_BASTION_PORT
          valueFrom:
            secretKeyRef:
              name: autossh
              key: ssh_bastion_port
        - name: SSH_PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: autossh
              key: ssh_private_key
---
apiVersion: v1
kind: Service
metadata:
  name: autossh
  labels:
    k8s-app: spell
spec:
  selector:
    name: autossh
    k8s-app: spell
  ports:
    - protocol: TCP
      port: 24224
      name: logs
    - protocol: TCP
      port: 24225
      name: ws-logs

    # TunnelKafkaBrokers for LOCAL
    - protocol: TCP
      port: 29193
      name: metrics-local

    # TunnelKafkaBrokers for DEV/PROD
    - protocol: TCP
      port: 32190
      name: metrics1
    - protocol: TCP
      port: 32191
      name: metrics2
    - protocol: TCP
      port: 32192
      name: metrics3
---
"""
