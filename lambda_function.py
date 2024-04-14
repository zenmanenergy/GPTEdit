import json
import requests

def lambda_handler(event, context):
    # Define the base URL for the server you want to pass requests to
    base_url = "http://web.schmon.org:81"

    # Extract HTTP method
    http_method = event['httpMethod']
    
    # Extract query string parameters and format them
    params = event.get('queryStringParameters', {})
    
    # Extract the body for POST requests and parse it if it's JSON
    

    # Determine URL and headers based on method
    headers = {'Content-Type': 'application/json'}  # Example header; adjust as necessary

    try:
        if http_method == 'GET':
            response = requests.get(base_url, params=params, headers=headers)
        elif http_method == 'POST':
            try:
                body = json.loads(event.get('body', '{}'))
            except json.JSONDecodeError:
                body = {}
            response = requests.post(base_url, json=body, headers=headers)
        

        # Return the response content and status code as a JSON object
        return {
            
            'statusCode': response.status_code,
            'body': response.text,
            'headers': {
                'Content-Type': response.headers.get('Content-Type')  # Ensure the response is treated as JSON
            }
        }
    
    except requests.RequestException as e:
        # Handle any exceptions that might occur
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
