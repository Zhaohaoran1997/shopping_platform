# Shopping Platform

A full-stack e-commerce platform built with Django and Vue.js.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Redis

## Project Structure

```
shopping_platform/
├── backend/         # Django backend
├── frontend/        # Vue.js frontend
├── docs/           # Documentation
└── venv/           # Python virtual environment
```

## Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database and other configurations
```

4. Configure Database:
   - Create a MySQL database named `shopping_platform`
   - Database configuration is located in `backend/backend/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'shopping_platform',
           'USER': 'root',
           'PASSWORD': '123456',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
   - Update the database credentials according to your MySQL setup

5. Run database migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

## Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173`

## Development Workflow

1. Start Redis server (required for session management and caching):
```bash
redis-server
```

2. Start both servers in separate terminal windows:
   - Backend: `python manage.py runserver`
   - Frontend: `npm run dev`

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Additional Commands

### Backend
- Run tests: `python manage.py test`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`

### Frontend
- Build for production: `npm run build`
- Preview production build: `npm run preview`
- Lint code: `npm run lint`

## Environment Variables

Make sure to set up the following environment variables in your `.env` file:

- `DEBUG`: Set to True for development
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: MySQL database connection string
- `REDIS_URL`: Redis connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

This project is licensed under the MIT License.
