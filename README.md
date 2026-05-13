# Mundo Tenis

A fullstack web application for managing a tennis club — players, courts, and users — built with Flask following an MVC architecture using Blueprints.

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate
- **Database:** MySQL
- **API:** REST with OpenAPI 3.0 documentation (Swagger UI)
- **Frontend:** HTML, CSS, Jinja2
- **Other:** Flask-Caching, Flask-SocketIO, Flask-CORS

## Features

- Full CRUD for players, courts and users
- Role-based authentication (admin / user)
- REST API documented with Swagger
- Pagination, image uploads and thumbnail generation
- Database seeders for initial data

## Getting Started

1. Clone the repo and navigate into the folder:
   ```bash
   git clone https://github.com/mateogdr/mundo-tenis.git
   cd mundo-tenis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment:
   ```bash
   cp .env.example .env
   # Fill in your credentials in .env
   ```

4. Run migrations and seed the database:
   ```bash
   flask db upgrade
   flask seed
   ```

5. Start the server:
   ```bash
   python app/app.py
   ```

App available at `http://127.0.0.1:5000`
