## About 


## Deploy to Cloud Run 
This explanation is for public internet access if you want to deploy it on the private network consult the documentation.
```
export PROJECT_ID='set_your_project_id'
export REGION=''
export REPO_NAME="trend-review-repo"
export SERVICE_NAME="trend-review-app"
gcloud auth login
gcloud config set project $PROJECT_ID && gcloud auth application-default set-quota-project $PROJECT_ID
gcloud artifacts repositories create $REPO_NAME     --repository-format=docker     --location=$REGION     --description="Docker repository for trend review app"
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}
gcloud run deploy $SERVICE_NAME  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest --platform managed     --region $REGION     --allow-unauthenticated
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
```
