#!/bin/bash
set -e

echo "Building Lambda deployment package..."

# Clean previous builds
rm -rf package lambda-deployment.zip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -t package/

# Copy application code
echo "Copying application code..."
cp -r *.py package/
cp -r crawler/ package/ 2>/dev/null || true
cp -r llm_processor/ package/ 2>/dev/null || true

# Create deployment package
echo "Creating deployment package..."
cd package
zip -r ../lambda-deployment.zip .
cd ..

echo "Lambda deployment package created: lambda-deployment.zip"
echo "Size: $(du -h lambda-deployment.zip | cut -f1)"
