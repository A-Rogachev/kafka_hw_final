#!/bin/bash
set -e

BOOTSTRAP_SERVER="kafka-4-mirror:9092"
COMMAND_CONFIG="/tmp/client-mirror.properties"

cat > ${COMMAND_CONFIG} <<EOF
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="admin-secret";
ssl.truststore.location=/opt/kafka/secrets/clients/client.truststore.jks
ssl.truststore.password=kafka-secret
ssl.endpoint.identification.algorithm=
EOF

until kafka-topics.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} --list >/dev/null 2>&1; do
    echo "Waiting for mirror Kafka..."
    sleep 2
done

echo "Mirror Kafka is ready. Creating topics..."

topics=(
    ${KAFKA_ANALYTICS_TOPIC_NAME_RECOMMENDATIONS}
    ${KAFKA_ANALYTICS_TOPIC_NAME_USER_ACTIONS}
)

for topic in "${topics[@]}"; do
    kafka-topics.sh --bootstrap-server ${BOOTSTRAP_SERVER} \
        --command-config ${COMMAND_CONFIG} \
        --create --topic "${topic}" \
        --partitions 3 --replication-factor 2 \
        --config retention.ms=259200000 \
        --config retention.bytes=10737418240 || true
done

echo "Topics created successfully on mirror cluster."
echo "Configuring ACLs on mirror cluster..."

# ACL для client_api (пишет в user_actions)
echo "Setting ACLs for client_api user on Mirror cluster..."
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:client_api \
    --operation Write --operation Describe --operation Create \
    --topic user_actions

# ACL для analytics (читает из shops_stock_accepted и user_actions, пишет в product_recommendations)
echo "Setting ACLs for analytics user on Mirror cluster..."
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:analytics \
    --operation Read --operation Describe \
    --topic source.shops_stock_accepted

kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:analytics \
    --operation Read --operation Describe \
    --topic user_actions

kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:analytics \
    --operation Write --operation Describe --operation Create \
    --topic product_recommendations

# ACL для analytics consumer group
kafka-acls.sh --bootstrap-server ${BOOTSTRAP_SERVER} --command-config ${COMMAND_CONFIG} \
    --add --allow-principal User:analytics \
    --operation Read --operation Describe \
    --group "*"

echo "ACLs configured successfully on mirror cluster!"