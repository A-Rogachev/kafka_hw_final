FROM confluentinc/cp-kafka-connect:7.6.0

USER root


RUN confluent-hub install --no-prompt confluentinc/kafka-connect-elasticsearch:15.1.1

USER appuser