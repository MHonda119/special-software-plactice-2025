# sandbox-special-software-plactice

hogehoge
Repository for KSU special software practice 

# Lecture

This project is a lecture management system built with the following technologies:

- **Frontend**: React
- **Backend**: Django
- **Database**: PostgreSQL

## Project Structure

The project is organized as follows:

```
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── lecture_system/        
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── core/                  # 最小アプリ
│       ├── __init__.py
│       ├── apps.py
│       └── views.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.jsx
│       └── main.jsx
├── ollama/
│   ├── Dockerfile
│   └── entrypoint.sh           #ローカルモデル起動用
├── docker-compose.yml
└── .env.example       
```

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository:

   ```
   git clone <repository-url>
   cd special-software-plactice-2025
   ```

2. Build and run the containers:

   ```
   docker-compose up --build
   ```

3. You can access the frontend at `http://localhost:3000` and the backend at `http://localhost:8000`.

4. First, access te backend admin panel (`http://localhost:8000/admin/`admin/password) and submit local llm in Llms model at side var.
  - Name : hogehoge (free name but required)
  - Model : gemma3:270m (required)

5. You can select model in menu (:3000) and chat!



### Backend

The backend is a Django application. The `requirements.txt` file contains all necessary dependencies. The `Dockerfile` is used to build the Docker image for the backend service.

### Frontend

The frontend is a React application. The `package.json` file defines the dependencies and scripts for the React app. The `Dockerfile` is used to build the Docker image for the frontend service.

### Database

PostgreSQL is used as the database for this application. Configuration for the database can be found in the `settings.py` file of the Django backend.

## Usage

After setting up the application, you can manage lectures through the frontend interface, which communicates with the Django backend to perform CRUD operations on the database.

## License

This project is licensed under the MIT License.