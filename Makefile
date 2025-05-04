.PHONY: help clean setup first-run dashboard dashboard-reset run-postgres run-neo4j process-data seed-neo4j run-dashboard process-and-seed stop

default: help

help:
	@echo "Available commands:"
	@echo "  make help            		- Show this help message"
	@echo "  make clean           		- Remove all containers and volumes"
	@echo "  make setup           		- Setup the project (build containers)"
	@echo ""
	@echo "Main workflow commands:"
	@echo "  make first-run       		- Complete initial setup (postgres, process data, seed neo4j, run dashboard)"
	@echo "  make dashboard       		- Start Neo4j (if not running) and run dashboard app"
	@echo "  make dashboard-reset 		- Start Neo4j database and restart dashboard app"
	@echo ""
	@echo "Individual steps:"
	@echo "  make run-postgres    		- Start and initialize PostgreSQL database"
	@echo "  make run-neo4j       		- Stop existing Neo4j container and restart Neo4j database"
	@echo "  make process-data    		- Run data processing notebooks"
	@echo "  make seed-neo4j      		- Seed Neo4j database"
	@echo "  make run-dashboard   		- Start the dashboard app"
	@echo "  make process-and-seed 		- Process data and seed Neo4j in one step"
	@echo "  make reset-neo4j     		- Reset Neo4j database and seed it again"
	@echo "  make reset-neo4j_volume 	- Reset Neo4j database including volume data and seed it again"
	@echo ""
	@echo "Utility commands:"
	@echo "  make stop            		- Stop all running containers"

clean:
	@echo "Removing all containers and volumes..."
	docker-compose down -v

setup:
	@echo "Building Docker containers..."
	docker-compose build


first-run: clean setup run-postgres run-neo4j process-and-seed run-dashboard
	@echo "First run complete! Dashboard is now running."

dashboard:
	@echo "Checking if Neo4j is running..."
	@docker-compose ps -q neo4j || docker-compose up -d neo4j
	@echo "Starting dashboard app..."
	@docker-compose up -d catbase_dashboard_app
	@echo "Dashboard is now running!"

dashboard-reset: reset-neo4j
	@echo "Stopping dashboard app..."
	@docker-compose stop catbase_dashboard_app
	@echo "Removing dashboard app container..."
	@docker-compose rm -f catbase_dashboard_app
	@echo "Rebuilding dashboard app..."
	@docker-compose build catbase_dashboard_app
	@echo "Starting dashboard app..."
	@docker-compose up -d catbase_dashboard_app
	@echo "Dashboard app has been reset and is now running!"

run-postgres:
	@echo "Starting PostgreSQL database..."
	docker-compose up -d postgres_original_db
	@echo "Initializing PostgreSQL database..."
	docker-compose up -d postgres_original_db_init
	@echo "PostgreSQL is initializing..."
	@while docker ps --filter "name=postgres_original_db_init" --quiet | grep -q .; do sleep 1; done
	@echo "PostgreSQL database initialization complete."
	docker-compose rm -f postgres_original_db_init

run-neo4j:
	@echo "Starting Neo4j database..."
	docker-compose down neo4j
	docker-compose up -d neo4j

process-data:
	@echo "Running data processing..."
	docker-compose run --rm catbase_data_processor_and_seeder process

seed-neo4j:
	@echo "Seeding Neo4j database..."
	docker-compose run --rm catbase_data_processor_and_seeder seed

reset-neo4j:
	@echo "Resetting Neo4j database..."
	docker-compose down neo4j
	docker-compose up -d neo4j

reset-neo4j_volume:
	@echo "Resetting Neo4j database..."
	docker-compose down neo4j
	docker volume rm -f catbase_neo4j_data || true
	docker-compose up -d neo4j
	docker-compose run --rm catbase_data_processor_and_seeder seed

run-dashboard:
	@echo "Starting dashboard application..."
	docker-compose up -d catbase_dashboard_app

process-and-seed:
	@echo "Processing data and seeding Neo4j..."
	docker-compose run --rm catbase_data_processor_and_seeder all

stop:
	@echo "Stopping all containers..."
	docker-compose stop