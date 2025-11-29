import json
import asyncio
from recrawl import recrawl_due_sites

def lambda_handler(event, context):
    """
    AWS Lambda handler for scheduled recrawl.

    Triggered by EventBridge on schedule.
    """
    try:
        # Run async recrawl function
        results = asyncio.run(recrawl_due_sites())

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Recrawl completed',
                'results': results
            })
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
