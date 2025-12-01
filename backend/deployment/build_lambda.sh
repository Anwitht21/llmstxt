#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Building Lambda deployment package..."

rm -rf deployment/package deployment/lambda-deployment.zip

echo "Installing dependencies..."
pip install -r requirements.txt -t deployment/package/

echo "Copying application code..."
cp deployment/lambda_handler.py deployment/package/
for file in *.py; do
    [ -f "$file" ] && cp "$file" deployment/package/
done
cp -r crawler/ deployment/package/ 2>/dev/null || true
cp -r llm_processor/ deployment/package/ 2>/dev/null || true

echo "Creating deployment package..."
cd deployment/package
zip -r ../lambda-deployment.zip .
cd ../..

echo "Lambda deployment package created: deployment/lambda-deployment.zip"
echo "Size: $(du -h deployment/lambda-deployment.zip | cut -f1)"
