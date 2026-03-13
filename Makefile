.DEFAULT_GOAL := start

.PHONY: help start check stop

help:   ## - Выводит список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

start:  ## - Запускает все контейнеры
	sudo docker compose --env-file env.example up -d

check:  ## - Псевдоним для команды просмотра запущенных контейнеров в docker compose
	sudo docker compose --env-file env.example ps -a

stop:  ## - Удаляет все контейнеры
	sudo docker compose --env-file env.example down -v --remove-orphans

analytics-logs: ## - Показывает логи аналитической системы
	sudo docker compose --env-file env.example logs -f analytics

health: ## - Проверяет здоровье всех сервисов
	@echo "Checking services health..."
	@echo "\n==> Kafka UI:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8080 || echo "Not available"
	@echo "\n==> Client API:"
	@curl -s http://localhost:8000/health | jq '.' || echo "Not available"
	@echo "\n==> Elasticsearch:"
	@curl -s http://localhost:9200 | jq '.version.number' || echo "Not available"
	@echo "\n==> Prometheus:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:9090 || echo "Not available"
	@echo "\n==> Grafana:"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3001 || echo "Not available"

monitor: ## - Выводит информацию о том, как получить доступ к интерфейсам Grafana, Prometheus и Kafka UI
	@echo "Grafana: http://localhost:3001 (admin/kafka)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Kafka UI: http://localhost:8080"

crash_broker: ## - Имитирует краш одного из Kafka брокеров (kafka-1)
	sudo docker compose stop kafka-1