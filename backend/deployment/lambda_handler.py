import json
import os
import urllib.request

def lambda_handler(event, context):
    api_url = os.environ.get('API_URL', 'https://llmstxt-backend.leap-cc.com')
    cron_secret = os.environ.get('CRON_SECRET')

    if not cron_secret:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'CRON_SECRET not configured'})
        }

    try:
        req = urllib.request.Request(
            f"{api_url}/internal/cron/recrawl",
            method='POST',
            headers={'X-Cron-Secret': cron_secret}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Recrawl triggered successfully',
                'result': result
            })
        }
    except Exception as e:
        print(f"Error triggering recrawl: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
