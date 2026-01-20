aws s3api create-bucket --bucket testing-resume-auto-terraform-state --region us-east-1

aws s3api put-bucket-versioning --bucket testing-resume-auto-terraform-state --versioning-configuration Status=Enabled

aws s3api put-public-access-block --bucket testing-resume-auto-terraform-state --public-access-block-configuration                                     BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true       
                                                                                 
  Add these in GitHub:                                            
  - Path: Repo → Settings → Secrets and variables → Actions → New repository secret
  - Secrets to add:
      - AWS_ACCESS_KEY_ID = your IAM user access key
      - AWS_SECRET_ACCESS_KEY = your IAM user secret
      - OPENAI_API_KEY = OpenAI key

Push code to GitHub main to trigger deployment


