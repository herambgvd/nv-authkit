#!/bin/bash

# FastAPI User Management System - Docker Deployment Script
# This script handles deployment of the application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
COMPOSE_PROD_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
ENV_PROD_FILE=".env.prod"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}FastAPI User Management Deployment${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  dev         Start development environment"
    echo "  prod        Start production environment"
    echo "  build       Build Docker images"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        Show logs"
    echo "  clean       Clean up containers and volumes"
    echo "  backup      Backup database"
    echo "  restore     Restore database from backup"
    echo "  migrate     Run database migrations"
    echo "  init        Initialize RBAC system"
    echo "  superuser   Create superuser"
    echo "  health      Check service health"
    echo ""
    echo "Options:"
    echo "  --build     Force rebuild images"
    echo "  --verbose   Verbose output"
    echo "  --help      Show this help message"
}

check_requirements() {
    echo -e "${BLUE}🔍 Checking requirements...${NC}"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Requirements satisfied${NC}"
}

setup_environment() {
    local env_type=$1

    echo -e "${BLUE}🔧 Setting up ${env_type} environment...${NC}"

    if [ "$env_type" = "production" ]; then
        if [ ! -f "$ENV_PROD_FILE" ]; then
            echo -e "${YELLOW}⚠️  Production .env file not found${NC}"
            echo -e "${YELLOW}💡 Creating from template...${NC}"
            cp .env.example "$ENV_PROD_FILE"
            echo -e "${RED}❗ Please update $ENV_PROD_FILE with production values${NC}"
            exit 1
        fi
        export ENV_FILE="$ENV_PROD_FILE"
        export COMPOSE_FILE="$COMPOSE_PROD_FILE"
    else
        if [ ! -f "$ENV_FILE" ]; then
            echo -e "${YELLOW}⚠️  Development .env file not found${NC}"
            echo -e "${YELLOW}💡 Creating from template...${NC}"
            cp .env.example "$ENV_FILE"
            echo -e "${RED}❗ Please update $ENV_FILE with your configuration${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}✅ Environment configured${NC}"
}

build_images() {
    local force_build=$1

    echo -e "${BLUE}🏗️  Building Docker images...${NC}"

    if [ "$force_build" = "true" ]; then
        docker-compose -f "$COMPOSE_FILE" build --no-cache
    else
        docker-compose -f "$COMPOSE_FILE" build
    fi

    echo -e "${GREEN}✅ Images built successfully${NC}"
}

start_services() {
    local env_type=$1
    local build_flag=$2

    echo -e "${BLUE}🚀 Starting $env_type services...${NC}"

    if [ "$build_flag" = "--build" ]; then
        docker-compose -f "$COMPOSE_FILE" up -d --build
    else
        docker-compose -f "$COMPOSE_FILE" up -d
    fi

    echo -e "${GREEN}✅ Services started${NC}"

    # Wait for services to be healthy
    echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
    sleep 10

    check_health
}

stop_services() {
    echo -e "${BLUE}🛑 Stopping services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

restart_services() {
    echo -e "${BLUE}🔄 Restarting services...${NC}"
    docker-compose -f "$COMPOSE_FILE" restart
    echo -e "${GREEN}✅ Services restarted${NC}"
}

show_logs() {
    local service=$1

    if [ -z "$service" ]; then
        docker-compose -f "$COMPOSE_FILE" logs -f
    else
        docker-compose -f "$COMPOSE_FILE" logs -f "$service"
    fi
}

clean_up() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"

    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down -v

    # Remove unused images
    docker image prune -f

    # Remove unused volumes
    docker volume prune -f

    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

backup_database() {
    echo -e "${BLUE}💾 Creating database backup...${NC}"

    # Create backup directory
    mkdir -p backups

    # Generate backup filename
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"

    # Create backup
    docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U fastapi_user fastapi_users > "$BACKUP_FILE"

    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
}

restore_database() {
    local backup_file=$1

    if [ -z "$backup_file" ]; then
        echo -e "${RED}❌ Please specify backup file${NC}"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found: $backup_file${NC}"
        exit 1
    fi

    echo -e "${BLUE}📥 Restoring database from $backup_file...${NC}"

    # Restore backup
    docker-compose -f "$COMPOSE_FILE" exec -T db psql -U fastapi_user -d fastapi_users < "$backup_file"

    echo -e "${GREEN}✅ Database restored${NC}"
}

run_migrations() {
    echo -e "${BLUE}🔄 Running database migrations...${NC}"

    docker-compose -f "$COMPOSE_FILE" exec api python -m alembic upgrade head

    echo -e "${GREEN}✅ Migrations completed${NC}"
}

init_rbac() {
    echo -e "${BLUE}🔑 Initializing RBAC system...${NC}"

    docker-compose -f "$COMPOSE_FILE" exec api python scripts/init_rbac.py

    echo -e "${GREEN}✅ RBAC system initialized${NC}"
}

create_superuser() {
    echo -e "${BLUE}👤 Creating superuser...${NC}"

    docker-compose -f "$COMPOSE_FILE" exec api python scripts/create_superuser.py

    echo -e "${GREEN}✅ Superuser created${NC}"
}

check_health() {
    echo -e "${BLUE}🏥 Checking service health...${NC}"

    # Check API health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is healthy${NC}"
    else
        echo -e "${RED}❌ API is not healthy${NC}"
    fi

    # Check database health
    if docker-compose -f "$COMPOSE_FILE" exec db pg_isready -U fastapi_user > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database is healthy${NC}"
    else
        echo -e "${RED}❌ Database is not healthy${NC}"
    fi

    # Check Redis health
    if docker-compose -f "$COMPOSE_FILE" exec redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis is healthy${NC}"
    else
        echo -e "${RED}❌ Redis is not healthy${NC}"
    fi
}

main() {
    print_header

    case "$1" in
        "dev")
            check_requirements
            setup_environment "development"
            start_services "development" "$2"
            ;;
        "prod")
            check_requirements
            setup_environment "production"
            start_services "production" "$2"
            ;;
        "build")
            check_requirements
            build_images "$2"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$2"
            ;;
        "clean")
            clean_up
            ;;
        "backup")
            backup_database
            ;;
        "restore")
            restore_database "$2"
            ;;
        "migrate")
            run_migrations
            ;;
        "init")
            init_rbac
            ;;
        "superuser")
            create_superuser
            ;;
        "health")
            check_health
            ;;
        "--help"|"-h"|"help")
            print_usage
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"