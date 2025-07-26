#!/bin/bash

# Force Kubernetes Pod to Pull New Voice Cloning Image
# ===================================================

NAMESPACE="dev"
DEPLOYMENT_NAME="voice-cloning"

echo "🔄 Forcing Kubernetes pod to pull new voice-cloning image"
echo "========================================================"
echo "Namespace: $NAMESPACE"
echo "Deployment: $DEPLOYMENT_NAME"
echo ""

# Method 1: Restart the deployment
echo "📋 Restarting deployment to pull new image..."
kubectl rollout restart deployment/$DEPLOYMENT_NAME -n $NAMESPACE

if [ $? -eq 0 ]; then
    echo "✅ Deployment restart initiated"
else
    echo "❌ Failed to restart deployment"
    exit 1
fi

# Wait for rollout to complete
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=300s

if [ $? -eq 0 ]; then
    echo "✅ Rollout completed successfully"
else
    echo "❌ Rollout failed or timed out"
    exit 1
fi

# Check pod status
echo "🔍 Checking pod status..."
kubectl get pods -n $NAMESPACE | grep $DEPLOYMENT_NAME

echo ""
echo "🎉 Pod update completed!"
echo "Check the logs to see if Coqui TTS is now working properly." 