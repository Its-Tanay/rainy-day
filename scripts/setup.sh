#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Trip Planner - Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo -e "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo -e "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}Docker is installed${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists. Skipping creation.${NC}"
else
    echo -e "${BLUE}Creating .env file from .env.example...${NC}"
    cp .env.example .env

    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-secret-key-here/$JWT_SECRET/" .env
        else
            # Linux
            sed -i "s/your-secret-key-here/$JWT_SECRET/" .env
        fi
        echo -e "${GREEN}Generated JWT secret key${NC}"
    else
        echo -e "${YELLOW}OpenSSL not found. Please manually update JWT_SECRET_KEY in .env${NC}"
    fi
fi

if [ -f "client/.env" ]; then
    echo -e "${YELLOW}client/.env file already exists. Skipping creation.${NC}"
else
    echo -e "${BLUE}Creating client/.env file from client/.env.example...${NC}"
    cp client/.env.example client/.env
    echo -e "${GREEN}Created client/.env${NC}"
fi

echo -e "\n${BLUE}Building and starting Docker containers...${NC}"
echo -e "${YELLOW}This may take a few minutes on first run...${NC}\n"

docker-compose up -d --build

echo -e "\n${BLUE}Waiting for services to start...${NC}"
sleep 10

echo -e "${BLUE}Checking backend health...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend failed to start${NC}"
        echo -e "${YELLOW}Run 'docker-compose logs backend' to see errors${NC}"
        exit 1
    fi
    sleep 2
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup Complete${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${BLUE}Your application is running at:${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3001${NC}"
echo -e "  Backend:  ${GREEN}http://localhost:3000${NC}"
echo -e "  Health:   ${GREEN}http://localhost:3000/health${NC}\n"

echo -e "${BLUE}To seed the database with sample data:${NC}"
echo -e "  ${YELLOW}make db-seed${NC}\n"

echo -e "${BLUE}Useful commands:${NC}"
echo -e "  ${YELLOW}make dev${NC}       - Start development environment"
echo -e "  ${YELLOW}make stop${NC}      - Stop all containers"
echo -e "  ${YELLOW}make logs${NC}      - View container logs"
echo -e "  ${YELLOW}make help${NC}      - Show all available commands\n"
