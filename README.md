# Trip Planner

A full-stack trip planning application that generates personalized itineraries based on your preferences, budget, and accessibility needs.

## Features

- Personalized itinerary generation based on budget and preferences
- Accessibility-aware activity recommendations
- Cuisine preferences and food recommendations
- Save and revisit past itineraries
- Secure JWT-based authentication
- Responsive design for mobile and desktop

## Quick Start (Docker)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

### Setup

```bash
# Clone the repository
git clone https://github.com/Its-Tanay/trip-planner.git
cd trip-planner

# Run the automated setup script
./scripts/setup.sh

# Or use Make
make setup
```

The setup script will:
- Copy environment files
- Generate secure JWT secret
- Build Docker containers
- Start all services (database, backend, frontend)

### Access the Application

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:3000
- **Health Check:** http://localhost:3000/health

### Seed Sample Data (Optional)

```bash
make db-seed
```

This populates the database with sample cities (Mumbai, Delhi) with activities and food options.

### Common Commands

```bash
make dev         # Start development environment
make stop        # Stop all containers
make logs        # View container logs
make restart     # Restart all containers
make clean       # Remove all containers and volumes
make help        # Show all available commands
```

## Quick Start (Manual Setup)

If you prefer not to use Docker:

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+

### Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp ../.env.example .env
# Edit .env with your database credentials and JWT secret

# Run the server
python main.py
```

Backend will run on http://localhost:3000

### Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm start
```

Frontend will run on http://localhost:3001

### Database Setup

You have three options for database setup:

#### Option 1: Docker PostgreSQL
```bash
docker-compose up db -d
```

#### Option 2: Local PostgreSQL
```bash
# Install PostgreSQL and create database
createdb trip_planner

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trip_planner
```

## Tech Stack

### Frontend
- **React** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **Tanstack Query** - Server state management
- **React Router** - Client-side routing

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **PostgreSQL** - Database

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration

## Project Structure

```
trip-planner/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── api/           # API client
│   │   └── lib/           # Utilities
│   ├── Dockerfile
│   └── package.json
├── server/                # Flask backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── database/     # Database models
│   │   └── utils/        # Utilities
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── docker-compose.yml     # Development orchestration
├── Makefile              # Common commands
└── scripts/
    └── setup.sh          # Automated setup
```

## Configuration

### Environment Variables

#### Backend (.env)
```bash
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@db:5432/trip_planner
JWT_SECRET_KEY=your-secret-key-here
```

#### Frontend (client/.env)
```bash
REACT_APP_BASE_URL_DEV=http://localhost:3000/
```

### Generate Secure JWT Secret

```bash
openssl rand -hex 32
```

## API Documentation

### Authentication

#### Sign Up
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { "id": 1, "email": "user@example.com", "name": "John Doe" }
}
```

### Itinerary

#### Generate Itinerary
```http
POST /api/itinerary/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "cityId": 1,
  "days": 3,
  "budget": "medium",
  "accessibility": true,
  "cuisinePreferences": ["Italian", "Indian"]
}
```

#### Get User Itineraries
```http
GET /api/itinerary/user
Authorization: Bearer <token>
```

#### Delete Itinerary
```http
DELETE /api/itinerary/:id
Authorization: Bearer <token>
```

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "trip-planner-api"
}
```
### Quick Contribution Workflow

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/trip-planner.git
cd trip-planner

# Set up development environment
./scripts/setup.sh

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and test
make dev

# Commit your changes
git commit -m "Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a Pull Request
```

## Architecture & Design

### High Level Architecture

The application follows a client-server architecture with three main components:

1. **Frontend (React SPA)** - Single Page Application with client-side routing
2. **Backend (Flask API)** - RESTful API with JWT authentication
3. **Database (PostgreSQL)** - Relational database for data persistence

### Database Schema

![Database Schema](https://github.com/user-attachments/assets/7f83be88-897a-4464-ac8d-48c3d2275c8c)

The schema includes:
- **Users** - Authentication and profile
- **Cities** - Destination information
- **Activities** - Things to do with ratings, budget, accessibility
- **Food** - Restaurant/food options with cuisine types
- **Itineraries** - Saved trip plans
- **Categories** - Activity categorization
- **Cuisines** - Food categorization

### Algorithm Overview

The itinerary generation algorithm:

1. Filters activities and food based on user preferences (budget, accessibility, cuisine)
2. Ranks options using a rating system that balances popularity with personalization
3. Distributes activities across days to create a balanced itinerary
4. Considers meal times and activity types for optimal scheduling

![Algorithm](https://github.com/user-attachments/assets/334a89b5-a9da-44bd-9a86-343965e84b96)

### Why These Technology Choices?

#### PostgreSQL over NoSQL
- Relational data structure with many-to-many relationships
- Data consistency is crucial for the algorithm
- Better development experience with SQLAlchemy ORM

#### Flask as Framework
- Lightweight and unopinionated for smaller applications
- Flexibility for custom architecture decisions
- No unnecessary overhead from features we don't need

#### Algorithm over AI/ML
- Structured algorithm on well-modeled data is more efficient
- Predictable, explainable results
- No dependency on expensive ML infrastructure
- Can be enhanced with ML in the future if needed

#### React for Frontend
- Unidirectional data flow (top to bottom)
- Large ecosystem and community support
- Excellent TypeScript integration

## Challenges Faced

1. **Activity Ranking** - Implemented a rating system to balance popular choices with user preferences
2. **Schema Design** - Open-ended requirements required iterative schema refinement
3. **Deployment** - Overcame WSGI deployment issues with Gunicorn configuration
4. **Data Collection** - Manually gathered and structured data from various sources

## Implementation Nuances

1. **Accessibility Support** - Algorithm filters based on accessibility requirements
2. **Extensible Categories** - Separate tables for categories and cuisines enable scalability
3. **Factory Pattern** - Backend uses app factory pattern for flexible configuration
4. **Itinerary Collections** - Past itineraries are saved and can be revisited

## Future Scope

1. **Server-Driven UI** - Dynamic category interpretations based on geographical location
2. **Admin Portal** - Streamlined data entry interface
3. **Geocoding Integration** - Shortest path sorting between activities with navigation support
4. **Data Pipelines** - Automated data collection and modeling workflows
5. **ML Enhancement** - Personalized recommendations based on user history
6. **Multi-City Trips** - Support for itineraries across multiple cities
7. **Real-time Updates** - Live activity availability and pricing

## Links

- **GitHub Repository:** [https://github.com/Its-Tanay/trip-planner](https://github.com/Its-Tanay/trip-planner)
- **Report Issues:** [GitHub Issues](https://github.com/Its-Tanay/trip-planner/issues)

---

Made by [Tanay Tiwari](https://github.com/Its-Tanay)
