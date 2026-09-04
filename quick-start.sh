#!/bin/bash

# Quick Start Script for AI Resume-Based Interview Platform

echo "========================================="
echo "Interview Platform - Quick Start"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and set your configuration"
    echo ""
else
    echo "✅ .env file exists"
    echo ""
fi

# Create storage directory
echo "Creating storage directory..."
mkdir -p storage
echo "✅ Storage directory created"
echo ""

# Start services
echo "Starting services with Docker Compose..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo ""
echo "Checking service health..."
docker-compose ps

echo ""
echo "Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "🌐 Application URL: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔐 Default Admin: admin@example.com / change-this-admin-password"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Restart services: docker-compose restart"
echo "3. Access the application at http://localhost:8000"
echo ""
echo "To view logs: docker-compose logs -f backend"
echo "To stop services: docker-compose down"
echo ""
