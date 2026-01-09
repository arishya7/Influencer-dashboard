# Frontend - Influencer Dashboard

A Streamlit-based web application for managing and analyzing influencer profiles across multiple social media platforms.

## Overview

The Influencer Dashboard provides a user-friendly interface for tracking, filtering, and managing influencer data. It features authentication, advanced filtering capabilities, profile management, and CSV export functionality.

## Tech Stack

- **Framework**: Streamlit 1.37+
- **Language**: Python 3.10+
- **Data Processing**: Pandas, NumPy
- **HTTP Client**: Requests
- **Containerization**: Docker

## Features

### Authentication
- Secure login system with token-based authentication
- User session management
- Protected routes and API calls

### Influencer Analytics
- **Advanced Filtering**:
  - Platform (TikTok, Rednote, Instagram)
  - Country (Singapore, China, Malaysia, United States, Others)
  - Primary and Secondary Categories
  - Follower Tier (Seeder, Nano, Micro, Macro, Celebrity)
  - Minimum followers, child age, and number of children
  - Influencer/Brand toggle

- **Data Management**:
  - Paginated results (50 profiles per page)
  - Real-time profile editing
  - Add custom columns dynamically
  - Add new influencer rows
  - Save changes to database
  - Profile saving/bookmarking

### Saved Profiles
- View all saved/bookmarked profiles
- Edit saved profile details
- Remove profiles from saved list
- Export profiles to CSV (role-based access)

### Categories

**Primary Categories**:
- Parenting + Lifestyle
- General Audience Brands
- Parenting + Beauty & Fashion
- Core Parenting & Family
- Parenting + Travel
- Mompreneurs / Dadpreneurs
- Family-Focused Brands & Services
- Parenting + Food
- Parenting + Health & Wellness

**Secondary Categories**:
- Lifestyle Mom / Dad
- Mom Style / Beauty
- Mom / Dad Blogger
- Home & Living Family Blogger
- Family Travel Blogger
- Parenting Expert
- Baby / Kids' Products
- Family Food Blogger
- Founder / Entrepreneur
- Family Fitness & Health
- And more...

## Project Structure

```
frontend/
├── app.py              # Main Streamlit application
├── api_client.py       # API client for backend communication
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── saved_profiles.csv # Local saved profiles storage
```

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Access to the backend API

### Local Development

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t influencer-dashboard-frontend .
```

2. Run the container:
```bash
docker run -p 8501:8501 influencer-dashboard-frontend
```

## Configuration

### API Endpoints

Update the API URL in [api_client.py](api_client.py:8) to point to your backend:

```python
INFLUENCER = "http://api:8000/influencers"
API_URL = "http://api:8000"
```

### Session State

The application uses Streamlit session state to manage:
- User authentication tokens
- Filter preferences
- Pagination state
- Custom columns
- Added rows

## API Client Functions

The [api_client.py](api_client.py) module provides the following functions:

- `fetch_influencers(params)` - Retrieve influencer data with filters
- `login_user(username, password)` - Authenticate user
- `add_influencer_column(column_name)` - Add custom column
- `add_influencer_row(row_data)` - Insert new influencer
- `update_creator(creator_id, update_data)` - Update influencer details
- `save_added_columns(rows)` - Save dynamic column data
- `update_mentions(creator_id, mentions_list)` - Update mentions
- `export_influencers_csv(username)` - Export data to CSV

## Usage

### Login
1. Enter your username and password on the login screen
2. Click "Login" to authenticate

### Filtering Influencers
1. Use the sidebar filters to narrow down results
2. Apply multiple filters simultaneously
3. Click "Reset Filters" to clear all selections
4. Toggle "Show All Profiles" to bypass pagination

### Managing Profiles
1. Edit profile data directly in the table
2. Click the "Save" checkbox to bookmark profiles
3. Use "Add Column" to create custom fields
4. Use "Add Row" to insert new influencers
5. Click "Save All Changes" to persist modifications

### Saving & Exporting
1. Checked profiles are saved to [saved_profiles.csv](saved_profiles.csv)
2. View saved profiles in the "Saved Profiles" tab
3. Export functionality available for authorized users

## Styling

The application features a custom dark theme with:
- Dark blue background (#13192A)
- Accent color (#C990B8)
- Card-based layouts with shadows
- Responsive design for various screen sizes

## Security Notes

- Passwords are transmitted to the backend API
- Authentication tokens are stored in session state


### Connection Issues
- Verify the backend API is running
- Check API_URL configuration in [api_client.py](api_client.py)
- Ensure network connectivity between frontend and backend


## License

Part of the Influencer Dashboard project.
