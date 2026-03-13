#!/bin/bash

echo 'Waiting for ksqlDB server...'
while ! curl -s http://ksqldb-server:8088/info > /dev/null; do 
    sleep 2
done
echo 'Creating stream...'
echo "CREATE STREAM IF NOT EXISTS recommendations_stream (
    item_id VARCHAR,
    recommendation_type VARCHAR,
    recommendation_score DOUBLE,
    product_count BIGINT,
    avg_price DOUBLE,
    generated_at VARCHAR
) WITH (
    KAFKA_TOPIC='product_recommendations',
    VALUE_FORMAT='JSON'
);" | ksql http://ksqldb-server:8088

sleep 3
echo 'Creating table...'
echo "CREATE TABLE IF NOT EXISTS latest_recommendations AS
    SELECT
        item_id,
        LATEST_BY_OFFSET(recommendation_type) AS recommendation_type,
        LATEST_BY_OFFSET(recommendation_score) AS score,
        LATEST_BY_OFFSET(product_count) AS product_count,
        LATEST_BY_OFFSET(avg_price) AS avg_price,
        LATEST_BY_OFFSET(generated_at) AS generated_at
    FROM recommendations_stream
    GROUP BY item_id
    EMIT CHANGES;" | ksql http://ksqldb-server:8088
echo 'Done!'

sleep 1

echo "CREATE STREAM IF NOT EXISTS products_stream (
    product_id VARCHAR,
    name VARCHAR,
    description VARCHAR,
    price STRUCT<amount DOUBLE, currency VARCHAR>,
    category VARCHAR,
    brand VARCHAR,
    stock STRUCT<available BIGINT, reserved BIGINT>,
    sku VARCHAR,
    created_at VARCHAR,
    updated_at VARCHAR,
    store_id VARCHAR
) WITH (
    KAFKA_TOPIC='source.shops_stock_accepted',
    VALUE_FORMAT='JSON'
);" | ksql http://ksqldb-server:8088

sleep 1
echo "CREATE TABLE IF NOT EXISTS category_stats AS
SELECT
    category,
    COUNT(*) AS product_count,
    AVG(price->amount) AS avg_price,
    SUM(stock->available) AS total_available_stock
FROM products_stream
GROUP BY category
EMIT CHANGES;" | ksql http://ksqldb-server:8088

sleep 1

echo "CREATE TABLE IF NOT EXISTS low_stock_products AS
SELECT
    product_id,
    LATEST_BY_OFFSET(name) AS name,
    LATEST_BY_OFFSET(category) AS category,
    LATEST_BY_OFFSET(stock->available) AS available_stock,
    LATEST_BY_OFFSET(price->amount) AS price
FROM products_stream
WHERE stock->available < 50
GROUP BY product_id
EMIT CHANGES;" | ksql http://ksqldb-server:8088

sleep 1

echo "CREATE TABLE IF NOT EXISTS premium_brands AS
SELECT
    brand,
    AVG(price->amount) AS avg_price,
    COUNT(*) AS product_count
FROM products_stream
GROUP BY brand
HAVING AVG(price->amount) > 5000
EMIT CHANGES;" | ksql http://ksqldb-server:8088