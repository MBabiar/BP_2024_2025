#!/bin/bash
set -e

run_notebooks() {
    echo "Starting data processing using Python script..."
    python /app/src/Data_Processing/run_notebooks.py
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: Data processing failed with exit code $exit_code"
        exit $exit_code
    fi
    
    echo "Data processing complete!"
}

seed_neo4j() {
    echo "Starting Neo4j database seeding..."
    
    if [ -f "/init_flag_neo4j/done" ]; then
        echo "Database already seeded. To reseed, remove init flag or volume."
    else
        python /app/src/db/neo4j/neo4j_seeder.py
        touch /init_flag_neo4j/done
        echo "Neo4j database seeding complete!"
    fi
}

show_usage() {
    echo "Usage: docker-compose run --rm catbase_data_processor_and_seeder [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  process    Run data processing notebooks"
    echo "  seed       Seed Neo4j database"
    echo "  all        Run both processing and seeding in sequence"
    echo ""
    echo "Example: docker-compose run --rm catbase_data_processor_and_seeder process"
}

case "$1" in
    process)
        run_notebooks
        ;;
    seed)
        seed_neo4j
        ;;
    all)
        run_notebooks
        seed_neo4j
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

if [ "$KEEP_RUNNING" = "true" ]; then
    echo "Keeping container running for debugging..."
    tail -f /dev/null
fi