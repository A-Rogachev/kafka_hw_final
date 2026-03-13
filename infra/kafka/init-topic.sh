#!/bin/bash
set -e

BOOTSTRAP_SERVER="kafka-1:9092"
COMMAND_CONFIG="/tmp/client.properties"

cat > ${COMMAND_CONFIG} <<EOF
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
ssl.truststore.location=/opt/kafka/secrets/clients/client.truststore.jks
ssl.truststore.password=kafka-secret
ssl.endpoint.identification.algorithm=
EOF

until kafka-topics.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} --list >/dev/null 2>&1; do
    echo "Waiting for Kafka..."
    sleep 2
done

echo "Kafka is ready. Creating topics..."

topics=(
    ${KAFKA_TOPIC_NAME_RAW}
    ${KAFKA_TOPIC_NAME}
    ${KAFKA_TOPIC_NAME_BANNED}
)

for topic in "${topics[@]}"; do
    kafka-topics.sh --bootstrap-server ${BOOTSTRAP_SERVER} \
    --command-config ${COMMAND_CONFIG} \
    --create --topic $topic \
    --partitions 3 --replication-factor 2 \
    --config retention.ms=259200000 \
    --config retention.bytes=10737418240 || true
done

echo "Topics created successfully!"
echo "Configuring ACLs..."

# ACL for producer (write to raw topic)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:producer \
    --operation Write --operation Describe --operation Create \
    --topic ${KAFKA_TOPIC_NAME_RAW}

# ACL for faust (read from raw, write to processed topics)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:faust \
    --operation Read --operation Describe \
    --topic ${KAFKA_TOPIC_NAME_RAW}

kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:faust \
    --operation Write --operation Describe --operation Create \
    --topic ${KAFKA_TOPIC_NAME}

kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:faust \
    --operation Write --operation Describe --operation Create \
    --topic ${KAFKA_TOPIC_NAME_BANNED}

# ACL for faust consumer group
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:faust \
    --operation Read --operation Describe \
    --group "*"

# ACL for kafka-connect (read from processed topic)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:client_api \
    --operation Read --operation Describe \
    --topic ${KAFKA_TOPIC_NAME}

kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:client_api \
    --operation Read --operation Describe \
    --group "*"

# ACL for internal topics (connect-*)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:client_api \
    --operation All \
    --topic "connect-" --resource-pattern-type prefixed

# ACL for faust internal topics (changelog, assignor, etc.)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:faust \
    --operation All \
    --topic "faust_app-" --resource-pattern-type prefixed

# ACL for Schema Registry (_schemas topic)
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:client_api \
    --operation All \
    --topic "_schemas"

echo "ACLs configured successfully!"