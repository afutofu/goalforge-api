# GoalForge API

Open source repository developing the REST API for [GoalForge](https://github.com/afutofu/goalforge).

## Current features

- CRUD functionality for tasks
- CRUD functionality for categories
- CRUD functionality for activity logs
- Protected routes using JWT
- OAuth sign in / sign up with Google

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

1 **Clone the repository**

```bash
git clone https://github.com/afutofu/goalforge-api.git
```

2 **Navigate to the project directory**

```bash
cd goalforge-api
```

3 **Create a virtual environment**

```bash
python -m venv venv
```

4 **Activate the virtual environment**

- **On Windows**

```bash
.\venv\Scripts\activate
```

- **On Unix or MacOS:**

```bash
source venv/bin/activate
```

5 **Install the required packages using requirements.txt**

```bash
pip install -r requirements.txt
```

6 **Create a google OAuth client secret and save it as "client-secret.json"**

The following link provides a comprehensive guide: https://developers.google.com/identity/protocols/oauth2

7 **Create a .env file in the root directory**

```bash
touch .env
```

8 **Fill the following variables with your own data**

The following is an example of a few of the variables used in the local environment

```bash
JWT_SECRET_KEY=""
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:5000"
GOOGLE_CLIENT_ID=""
SESSION_SECRET_KEY=""
GOOGLE_CLIENT_SECRET_PATH="./client-secret.json"
ENCRYPTION_KEY=""
HMAC_KEY=""

DB_DRIVER="postgres"
DB_USER="postgres"
DB_PASSWORD="example_password"
DB_NAME="goalforge"
DB_HOST="localhost"
DB_PORT="5432"
```

9 **Run the application**

```bash
python app.py
```

## Built With

- Flask
- SQLAlchemy
- Boto3

## Authors

- Afuza - Design and implement API and Database
