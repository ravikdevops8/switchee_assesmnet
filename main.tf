provider "aws" {
  region = "us-west-2"
}

resource "aws_dynamodb_table" "weather_data" {
  name           = "WeatherData"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "property_id"
  range_key      = "date"

  attribute {
    name = "property_id"
    type = "N"
  }

  attribute {
    name = "date"
    type = "S"
  }
}

resource "aws_lambda_function" "weather_lambda" {
  filename         = "lambda_function_payload.zip"
  function_name    = "WeatherLambda"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("lambda_function_payload.zip")
  runtime          = "python3.9"
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.weather_data.name
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "lambda_exec_policy" {
  name = "lambda_exec_policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:*",
          "dynamodb:*"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_sqs_queue" "weather_queue" {
  name = "weather_queue"
}

resource "aws_lambda_event_source_mapping" "sqs_lambda_trigger" {
  event_source_arn = aws_sqs_queue.weather_queue.arn
  function_name    = aws_lambda_function.weather_lambda.arn
  enabled          = true
}
