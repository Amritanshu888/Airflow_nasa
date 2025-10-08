from airflow import DAG ## PythonOperator is basically for executing a python function
from airflow.providers.http.operators.http import HttpOperator ## For reading data from API.
## We have different operators for different task --> For eg. for sending an email we have a different operator.
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook ## Search for Airflow Hooks(around 200 hooks are there,hooks are used for loading data)
## PostgresHook is basically used for pushing the data to the Postgres database.
from datetime import datetime,timedelta
import json

## Define the DAG
with DAG(
    dag_id = 'nasa_apod_postgres',
    start_date = datetime.now() - timedelta(days=1), ## Basically its saying that everyday try to run this DAG
    schedule = '@daily',
    catchup = False
) as dag:
    ## Step 1 : Create the table if it doesn't exists
    @task
    def create_table():
        ## Initialize PostgresHook(library we are using to interact with the Postgres SQL)
        postgres_hook = PostgresHook(postgres_conn_id="my_postgres_connection") ## This id we have to create , this is the id of the Postgres SQL that u have to create.

        ## SQL query to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS apod_data (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            explanation TEXT,
            url TEXT,
            date DATE,
            media_type VARCHAR(50)
        );
        
        """
        ## These fields will be coming from a particular API that we are going to use.
        ## Execute the table creation query
        postgres_hook.run(create_table_query)
        ## We will be running our Postgres SQL in docker
        ## And Airflow in another docker , now both these two dockers are 
        ## running seperately , but at the end of the day my entire Airflow application has to communicate with the Postgres.
        ## So two docker containers will be interacting with each other -----> Then we write all the configurations in the docker-compose.yml file.
        ## Whenever u have two docker containers and two applications are running in different docker containers and they really want to interact with each other. Then only we can use docker-compose.yml file.




    ## Step 2 : Extract the NASA API Data(APOD Data) --> APOD basically means Astronomy Picture of the Day.[Creating ur Extract Pipeline]
    ## Getting the API : https://api.nasa.gov --> generate the API from here.
    extract_apod = HttpOperator(
        task_id = 'extract_apod',
        http_conn_id = 'nasa_api', ## Connection ID Defined In Airflow For NASA API
        endpoint = 'planetary/apod',  ## Hit this URL : https://api.nasa.gov/planetary/apod?api_key=ur_api_key  --> It will show that ur api key is working. This is nothing but NASA API endpoint for APOD(Artronomy Picture of the Day)
        method = 'GET',
        data = {"api_key":"{{conn.nasa_api.extra_dejson.api_key}}"}, ## conn is nothing but connection that we setup in airflow. This is basically using the API Key from the connection.
        response_filter = lambda response:response.json(), ## Convert response to json
    ) ## Responsible for hitting the API and getting the information
    ## This was Task 2 to do the API request and get the response in form of json.


    ## Step 3 : Transform the data(Pick the information that i need to save)
    @task
    def transform_apod_data(response):
        apod_data = {
            'title': response.get('title',''),  ## Here if the keys are not available then it will give a blank ''
            'explanation': response.get('explanation',''),
            'url': response.get('url',''),
            'date': response.get('date',''),
            'media_type': response.get('media_type','')
        } ## Creating in form of key-value pair and then returning the data itself.
        return apod_data


    ## Step 4 : Load the data into Postgres SQL
    @task
    def load_data_to_postgres(apod_data):
        ## Initialize the PostgresHook
        postgres_hook = PostgresHook(postgres_conn_id='my_postgres_connection') ## Why we are creating it ?? So that i can load the entire data into the Postgres

        ## Define the SQL Insert Query
        insert_query = """
        INSERT INTO apod_data (title, explanation, url, date, media_type)
        VALUES (%s, %s, %s, %s, %s);
        """
        ## These values will be coming from apod_data.

        ## Execute the SQL Query
        postgres_hook.run(insert_query,parameters=(
            apod_data['title'],
            apod_data['explanation'],
            apod_data['url'],
            apod_data['date'],
            apod_data['media_type']
        ))
        ## When u execute this data will get uploaded in the Postgres




    ## Step 5 : Verify the data by DBViewer(It is another tool which will actually help u to connect with any type of database like Postgres , MySQL or any other type of database.)


    ## Step 6 : Define the task dependencies
    ## All the connections we have created above need to be created in the Airflow container itself.
    ## Extract
    create_table_task = create_table()
    api_response = extract_apod.output
    ## Transform
    transformed_data = transform_apod_data(api_response)
    ## Load
    load_task = load_data_to_postgres(transformed_data) ## This will push the Data to the PostgresSQL
    # Set up the correct dependencies
    create_table_task >> extract_apod >> transformed_data >> load_task ## Not necessarily required as functions are already getting executed in order(But is best practice).


## Setting up the connection after writing the code.
## Command to run : astro dev start
## In the sidebar under admins u will have connections
## Without connections it would not work , here we have to add 2 different connections
## Go to connections and click add connection
## Enter connection name , first connection is http_conn_id = 'nasa_api' in the Task 2 , enter connection name 'nasa_api'
## In connection types it support multiple connection types : we will select HTTP
## Then it will ask for host : there we will give the same API we were calling : https://api.nasa.gov/
## In the extra field we will have to give our API key : 
## {
##       "api_key": "ur_api_key"   ----> This should be the format its in json
##  }
## After this my first connection will be created
## 2nd connection : my_postgres_connection (used earlier in code)
## In docker compose my in environment variables my Postgres username , db and password is named as postgres
## Click add connection , then enter name "my_postgres_connection" , in connection type : Select postgres
## What host should we select for Postgres ??
## Go inside ur Docker Desktop(Note: Docker should be running in Background b4 all this) , u will see postgres is running inisde ur docker as a container.
## Click on that docker container on which postgres is running : At the top u will get the name of the Postgres Container , that name u have to enter in Host while adding the connection for postgres.
## Then while entering ur Database , Login , Password all will be "postgres" as entered in docker-compose.yml file.
## Provide the port : 5432 same as in docker-compose file .
## Xcom me u will be able to see the information which is retrieved from API ---> because we used task decorator.
## Data will be available in tasks extract_apod and transform_apod_data in Xcom.
## Postgres is running in docker container , inorder to see the data in postgres install dbviewer(Dbeaver).
## Download dbeaver , open it , click on database ----> best thing about dbeaver is that it will allow u to onnect to different 
## different kinds of database.
## In database select postgres(after clicking on new database connection)
## In postgres host should be localhost and port : 5432 (by default it will come). Same port will make it interact to docker container.
## In username and password give : postgres , postgres as we have in docker compose. Database name also postgres.
## Then click test the connection , it will show connected , then click finish.
## In SQL editor there u can run the query on database also.
## Stop it : astro dev stop


