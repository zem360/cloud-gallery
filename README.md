# Art Pipeline - Daily Art Showcase

A serverless data pipeline that fetches artwork from the Art Institute of Chicago API daily and displays them on a static website hosted on AWS S3.

## Architecture

The pipeline uses the following AWS services:
- **EventBridge**: Daily scheduling (cron-based triggers)
- **Step Functions**: Workflow orchestration
- **Lambda Functions**: Data processing and API interactions
- **DynamoDB**: Metadata storage
- **S3**: Static website hosting
- **SNS**: Notifications
- **CloudWatch**: Monitoring and logging

## Project Structure

```
art-pipeline/
├── .github/workflows/     # GitHub Actions CI/CD
├── terraform/            # Infrastructure as Code
├── src/                 # Lambda function source code
├── tests/               # Unit and integration tests
├── scripts/             # Deployment and utility scripts
└── templates/           # HTML templates
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Python 3.9+
- GitHub account with Actions enabled

## Quick Start

1. Clone the repository
2. Copy `terraform.tfvars.example` to `terraform.tfvars`
3. Update variables in `terraform.tfvars`
4. Run deployment script: `./scripts/deploy.sh`

## Deployment

### Manual Deployment
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Automated Deployment
Push to main branch triggers GitHub Actions deployment.

## Free Tier Compliance

This project is designed to stay within AWS Free Tier limits:
- Lambda: 1M requests/month, 400,000 GB-seconds
- DynamoDB: 25GB storage, 25 RCU/WCU
- S3: 5GB storage, 20,000 GET requests
- EventBridge: 14M events/month (way more than 1 daily)

## Development

### Local Testing
```bash
python -m pytest tests/
```

### Lambda Function Testing
```bash
# Test individual functions locally
cd src/lambda_functions/fetch_art
python lambda_function.py
```

## Monitoring

- CloudWatch Dashboard: Monitor pipeline health
- SNS Notifications: Get alerts on failures
- Logs: Available in CloudWatch Logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details