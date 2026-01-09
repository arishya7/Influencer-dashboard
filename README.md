# Influencer Dashboard

A full-stack web application for managing and tracking influencer data, built with FastAPI, Streamlit, and MySQL.

## Features

- User authentication and login system
- Interactive dashboard for viewing influencer data
- Add, edit, and update influencer information
- Export influencer data to CSV
- Manage mentions and creator details
- Responsive UI with custom styling

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - SQL toolkit and ORM
- MySQL 8.0 - Database
- PyMySQL - MySQL driver
- Python-Jose - JWT authentication
- Bcrypt - Password hashing

**Frontend:**
- Streamlit - Interactive web application framework
- Pandas - Data manipulation
- Requests - HTTP library

**Infrastructure:**
- Docker & Docker Compose - Containerization

## Prerequisites

- Docker and Docker Compose installed
- Python 3.12 (if running locally without Docker)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/arishya7/Influencer-dashboard.git
cd Influencer-dashboard
```

2. Create a `.env` file in the root directory with your environment variables:
```env
DATABASE_URL=mysql+pymysql://root:MMDb@ccess123!@db:3306/mminfluencer_db
SECRET_KEY=your-secret-key-here
```

3. Start the application:
```bash
docker-compose up -d
```

4. Access the application:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - MySQL: localhost:3307

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
Influencer-dashboard/
├── backend/           # FastAPI backend
│   ├── main.py       # Main API application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # Streamlit frontend
│   ├── app.py       # Main UI application
│   ├── api_client.py # API client functions
│   ├── Dockerfile
│   └── requirements.txt
├── database/         # Database utilities
├── data/            # Data files
├── docker-compose.yml
├── .env             # Environment variables
└── README.md
```

## Usage

1. Log in with your credentials on the login page
2. View and manage influencer data in the dashboard
3. Add new influencers or update existing ones
4. Export data to CSV for external use
5. Manage mentions and track creator information

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

arishya7, yijun 