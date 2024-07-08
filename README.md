# Historical Weather Data Retrieval

## Overview

This project implements an AWS Lambda function to retrieve historical weather data from the Open Meteo API and store it in DynamoDB. The function is triggered by messages in an SQS queue.

## Implementation Details

1. **Lambda Function**: The Lambda function retrieves weather data, aggregates it, and saves it to DynamoDB.
2. **DynamoDB**: Stores the aggregated weather data.
3. **SQS**: Queue to trigger the Lambda function.
4. **Terraform**: Used to deploy the entire infrastructure.

## Files

- `lambda_function.py`: The Lambda function code.
- `main.tf`: Terraform configuration file.
- `README.md`: Documentation.

## Deployment

1. Zip the Lambda function code:
   ```bash
   zip lambda_function_payload.zip lambda_function.py
