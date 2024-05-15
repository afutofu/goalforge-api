# GoalForge API

Open source repository to develop the REST API for [GoalForge](https://github.com/afutofu/goalforge).

## Current features

- CRUD functionality for tasks
- CRUD functionality for activity logs
- Protected routes using JWT
- OAuth sign in / sign up with Google

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing

1 **Clone the repository**

```bash
git clonehttps://github.com/afutofu/goalforge-api.git
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

## Built With

- Flask
- Boto3

## Authors

- Afuza - Design and implement API and Database
