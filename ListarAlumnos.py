import boto3
import pymysql
import os
from botocore.exceptions import ClientError

def get_secret(secret_name):
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    
    secret = get_secret_value_response['SecretString']
    return secret

def lambda_handler(event, context):
    SSM_host = os.environ['DB_HOST']
    user = os.environ['DB_USER']
    SSM_password = os.environ['DB_PASSWORD']
    database = os.environ['DB_NAME']

    host = get_secret(SSM_host)
    password = get_secret(SSM_password)

    try:
        connection = pymysql.connect(
            host=host, #
            user=user,
            password=password, #
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")  # Ajusta el nombre de la tabla según tu caso
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()