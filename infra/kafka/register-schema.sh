#!/bin/sh
set -e

echo "Waiting for Schema Registry to be ready..."
until curl -s http://schema-registry:8081/ >/dev/null 2>&1; do
    echo "Schema Registry not ready yet, waiting..."
    sleep 3
done

echo "Schema Registry is ready!"
sleep 2

# Register product schema (for shops_stock_* topics)
echo "==> Registering Product schema..."
SCHEMA_CONTENT=$(cat /opt/schemas/product-schema.json | jq -c .)
PAYLOAD=$(jq -n --argjson schema "$SCHEMA_CONTENT" '{schema: ($schema | tostring), schemaType: "JSON"}')

curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "$PAYLOAD" \
    http://schema-registry:8081/subjects/shops_stock_received-value/versions

echo ""
echo "Product schema registered for shops_stock_received-value"

curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "$PAYLOAD" \
    http://schema-registry:8081/subjects/shops_stock_accepted-value/versions

echo ""
echo "Product schema registered for shops_stock_accepted-value"

# Register user actions schema
echo "==> Registering UserAction schema..."
USER_ACTION_SCHEMA=$(cat /opt/schemas/user-actions-schema.json | jq -c .)
USER_ACTION_PAYLOAD=$(jq -n --argjson schema "$USER_ACTION_SCHEMA" '{schema: ($schema | tostring), schemaType: "JSON"}')

curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "$USER_ACTION_PAYLOAD" \
    http://schema-registry:8081/subjects/user_actions-value/versions

echo ""
echo "UserAction schema registered for user_actions-value"

# Register recommendations schema
echo "==> Registering Recommendations schema..."
RECOMMENDATIONS_SCHEMA=$(cat /opt/schemas/recommendations-schema.json | jq -c .)
RECOMMENDATIONS_PAYLOAD=$(jq -n --argjson schema "$RECOMMENDATIONS_SCHEMA" '{schema: ($schema | tostring), schemaType: "JSON"}')

curl -X POST \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    --data "$RECOMMENDATIONS_PAYLOAD" \
    http://schema-registry:8081/subjects/product_recommendations-value/versions

echo ""
echo "Recommendations schema registered for product_recommendations-value"

echo ""
echo "==> All schemas registered successfully!"
echo ""
echo "Listing all registered subjects:"
curl -s http://schema-registry:8081/subjects | jq '.'