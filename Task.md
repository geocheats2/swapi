Project Overview
Build a RESTful API that interacts with the Star Wars API (SWAPI) to provide information
about Star Wars characters, films, and starships, and allows you to vote for your favourite
ones. The API should be built using a Python framework (such as FastAPI, Flask or Django),
include database models, handle errors gracefully, and be well-tested.
SWAPI URL: https://swapi.dev/
Requirements
1. Environment Setup
- Use Python 3.x.
- Choose a web framework: FastAPI, Flask or Django.
- Use a SQL database (SQLite, PostgreSQL, etc.).
- Utilize virtual environments for dependency management.
2. API Endpoints
- Create endpoints to:
- Fetch and store Star Wars characters, films, and starships in the database.
- Retrieve stored characters, films, and starships with pagination.
- Search characters, films, and starships by name.
3. Database Models
- Define models for Characters, Films, and Starships.
- Use appropriate relationships between models (e.g., many-to-many between Characters
and Films).
4. External API Integration
- Integrate with the SWAPI to fetch data.
- Store the fetched data in the database.
5. Error Handling
- Handle errors such as external API failures, database errors, and invalid input gracefully.
- Return meaningful HTTP status codes and error messages.
6. Unit Testing
- Write unit tests for the API endpoints.
- Mock external API calls in tests.
- Ensure a minimum of 80% code coverage.
7. Documentation
- Provide API documentation using Swagger or similar tools.
- Include instructions on how to set up the environment, run the application, and run tests.
Tasks
1. Environment Setup and Initialization
- Set up a virtual environment and install necessary packages.
- Initialize a FastAPI/Flask/Django project.
2. Database Models
- Define and migrate database models for Characters, Films, and Starships.
3. External API Integration
- Create a service to fetch data from SWAPI.
- Populate the database with fetched data.
4. API Endpoints
- Implement endpoints for fetching, storing, retrieving, and searching data.
5. Error Handling
- Add error handling for external API calls, database operations, and input validation.
6. Unit Testing
- Write and run unit tests for all implemented features.
- Ensure external API calls are mocked.
7. Documentation
- Document the API using Swagger or a similar tool.
- Write a README with setup, run, and test instructions.