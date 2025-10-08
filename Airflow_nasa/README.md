## Project Overview
- Basically here in this project we are creating an ETL pipeline , the data we are taking from NASA API.
- We will transform the data load it into postgres database.
- The entire workflow will be orchestrated by Airflow , a platform that allows scheduling , monitoring and managing of workflows.
- The project leverages Docker to run Airflow and Postgres as services , ensuring an isolated and reproducible environment.
- We also utilize Airflow hooks and operators to handle the ETL process efficiently.
- Airflow Hooks is useful when we have to push some data to the Postgres SQL.


## Architecture
- API(Source)-------> Transformation(generic python code, python operator will be used --> will convert this into a json)-------> Load(In some kind of datasource)
- Till now we saw we were creating tasks using python operator , here we are reading the data from the API so we will see creation of a task where we are reading from an API and we will be using a different kind of operator over here(HTTP Operator).
- Why using HTTP operator ---> bcoz in most of the usecases we have to read our most of the data from API itself.
- Where are we going to run Postgres --> Inside our Docker Container.
- We will create another file in this Directory --> docker-compose.yml .
- docker-compose is important bcoz just by seeing the architecture we have this Postgres SQL , we have this API , Postgres SQL will be working or running on a different docker container , Airflow will be also running on a different docker container. So for both of these containers to interact we have to use docker-compose.

## Process
- 1. Extract (E): The SimpleHttpOperator is used to make HTTP GET requests to NASA's APOD API. The response is in JSON format , containing fields like the title of the picture , the explanation , and URL to the image.
- 2. Transform (T): The extracted JSON data is processed in the transform task using Airlfow's TaskFlow API (with the @task decorator). This stage involves extracting relevant fields like title , explanation , url , and date and ensuring that they are in correct format for the database.
- 3. Load (L): The transformed data is loaded into a Postgres table using PostgresHook(To load the data we are using Hooks , we have different kinds of Hooks like if cloud is S3 we have S3 hook ---> All these features are basically provided by Airflow). If the target table doesn't exist in the Postgres database , it is created automatically as part of the DAG using a create table task.