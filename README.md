# Todo List Application

A simple and modern web-based todo list application built with Python Flask.

## Features

- Add new todos with title and description
- Mark todos as completed/pending
- Delete todos
- Clean and responsive UI
- SQLite database for data persistence

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- Backend: Python Flask
- Database: SQLite
- Frontend: HTML, CSS, Bootstrap 5
- Additional: Flask-SQLAlchemy, Gunicorn

## Deployment Instructions

1. Create a new Web Service on Render:
   - Go to [Render](https://render.com)
   - Click "New +" and select "Web Service"
   - Choose "GitHub" as the source
   - Connect your GitHub repository
   - Select the branch you want to deploy
   
2. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - `SECRET_KEY`: Your secret key (optional)
   - Database URL: SQLite will be used by default
   
3. Click "Create Web Service"
4. Wait for the deployment to complete
5. Once deployed, you'll get a URL like: https://your-app-name.onrender.com/

## Note
The application uses SQLite database which will be stored in the Render environment. The database will persist between deployments.
