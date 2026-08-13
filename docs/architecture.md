# Architecture

## Application flow

```mermaid
flowchart LR
    Manager[Manager browser] -->|HTTP :80| Nginx
    Nginx -->|static files| React[React application]
    Nginx -->|/api/v1| API[FastAPI]
    API --> ORM[SQLAlchemy]
    ORM --> DB[(PostgreSQL)]
```

The browser holds filter UI state. FastAPI validates it and PostgreSQL performs all candidate matching. Only matching candidate summaries are returned.

## Minimal AWS deployment

```mermaid
flowchart TB
    Internet[Manager via public IP] --> SG[EC2 security group: TCP 80]
    SG --> EC2[EC2 in default VPC/default subnet]
    subgraph EC2Host[Single EC2 instance]
      N[Nginx + React]
      F[FastAPI]
      P[(PostgreSQL volume)]
      N --> F --> P
    end
    EC2 --> EC2Host
```

Terraform uses the account's default VPC. Because this AWS account has no remaining default subnets, it creates one public subnet inside that VPC, then creates a security group, an IAM role for Systems Manager, one private S3 deployment-artifact bucket, and one EC2 instance. The bucket is only a source-transfer mechanism because this workspace has no remote Git repository; it does not participate at runtime. No custom VPC, load balancer, domain, TLS certificate, RDS, or public database port is introduced.

PostgreSQL runs on the EC2 instance because this is a simple demonstration. A longer-lived internal application should move it to RDS.
