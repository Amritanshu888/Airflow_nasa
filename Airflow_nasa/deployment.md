## Deployment in AWS
- Astronomer.io provides a entire cloud platform wherein u will be able to manage ur entire Airflow application. Postgres can be created in AWS , since everything is working in AWS u have to probably change the host. Postgres connection me jo host diya tha (basically ur docker container name on which postgres was running) ---> Wahi hai tumhara AWS host.
- From local when u will run all the info will get stored in the database which is on AWS.

- In deployment select AWS and then click 'Create Deployment'. Note: Template should be selected as ETL.

## Commands for deployment from CLI
- astro login ---> Then login successfully.(It will ask to press enter to open a browser). After u login it will show : ur device is now connected.
- astro deploy --> It will ask to select deployment project (number will be there) , press that number then press enter.
- Now ur project is deployed
- Astronomer does not provide a way to create a postgres sql over here. So we create Postgres SQL in AWS , for this we use RDS , search this in AWS Console , RDS basically means Managed Relational Database Service by AWS -----> In RDS click DB instances , and start creating a DB instance , click create database --> after that in Choose a database creation method select "Standard Create" , Select Postgres in engine options , then in Templates select "Free Tier", DB instance identifier will be there in settings , in credentials setting u will have Master username (write postgres as its in docker compose) , Credentials management select Self Managed , in credentials setting only we have master password (enter postgres as in docker compose) , same in confirm master passoword .
- In advanced setting set public access (make it public)  ------> Then click Create Database.
- Database will get created.
- When u go in the created database u will see under Connectivity and Security in security we have VPC security group , below this there is an id click this --> new page ----> again click the id ----> In Inbound rule u have a option called as Edit Inbound Rule ----> In Edit inbound rule u have to add a rule (type will be Postgres-SQL , port range : 5432, Source will be Custom , access : 0.0.0.0/0---> everybody will be able to access(This is IP from internet we will be able to access) , protocol should be TCP).
- In RDS go again inside the selected database instance ---> under connectivity and security in endpoint & port u will have a endpoint , copy the endpoint address bcoz this is what will get updated in Host section of Connection in Airflow which we did for postgres(while adding connection, instead of docker name we will add this).

- In deployments when u select the particular deployment and then u go in it on top right : Open Airflow option is there. Click on it.
- Here ur airflow is running in clouds.
- B4 opening airflow , in the deployments page u will still see the DAGs option along with deplyment option there , go to DAGs on the right side u will have a '+' icon asking it to run , run it .
- In admin run select connections here we have to edit connections (the host which we changed earlier in postgres that only). Rest all same as docker-compose , nasa api connection will be the same.

## To view the data
- Go to Dbeaver -> Setup the connection as done earlier , in there open SQL editor write the query , SELECT * from apod_data ---> U will get list of records.
- SQL Down arrow icon will be there on top below SQL editor and database option , select the datbase from there and then run the query.
