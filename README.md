# To Run with Docker (Recommended)  
## Steps:  
In the directory where README.md is located, run:  

`docker-compose -f ./compose.yml up`  

Then go to your favourite browser and access  
`http://localhost:5000`  

## Requirements  

Docker  

# To Run without Docker  
## Requires:  
PostgreSQL  
Python 3.8  
MarkupSafe==1.1.1  
Jinja2==2.10  
Flask==1.0.2  
Werkzeug==0.14.1  
itsdangerous==1.1.0  
click==7.0  
psycopg2==2.8.5  
requests==2.24.0  

## Steps to run withou Docker  
Set environment variable:  
$POSTGRES_HOST  
$POSTGRES_PASSWORD   
$POSTGRES_DB  
$BACKEND_URL = "http://localhost:5001"  
Initialize PostgreSQL with init.sql  
