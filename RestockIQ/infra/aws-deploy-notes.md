# AWS deployment notes for RestockIQ

Recommended production layout:
- React frontend on S3 + CloudFront or AWS Amplify
- FastAPI backend on ECS/Fargate or AWS App Runner
- PostgreSQL on Amazon RDS
- Container images in Amazon ECR
- Secrets stored in AWS Secrets Manager

High-level steps:
1. Build and push backend and frontend images to ECR.
2. Provision an RDS PostgreSQL instance.
3. Deploy backend container to App Runner or ECS/Fargate.
4. Deploy static frontend assets to S3 + CloudFront or use Amplify.
5. Point `VITE_API_URL` to the backend endpoint.
6. Connect Tableau to the reporting view in PostgreSQL.
