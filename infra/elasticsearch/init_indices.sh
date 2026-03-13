#!/bin/bash
set -e

echo "Waiting for Elasticsearch to be ready..."
until curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
    echo "Waiting for Elasticsearch..."
    sleep 2
done

echo "Elasticsearch is ready!"

echo "Creating index template for products..."
curl -X PUT "http://elasticsearch:9200/_index_template/products_template" \
    -H 'Content-Type: application/json' \
    -d @/tmp/index_template.json

echo ""
echo "Index template created successfully!"

echo "Creating initial index..."
curl -X PUT "http://elasticsearch:9200/shops_stock_accepted" \
    -H 'Content-Type: application/json' \
    -d '{
        "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
        }
    }'

echo ""
echo "Elasticsearch initialization complete!"