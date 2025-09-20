import os
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.conf import settings
from.models import Project
from.serializers import ProjectSerializer

import joblib
import torch
from sentence_transformers import SentenceTransformer

# Define ML model paths
ML_MODELS_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
SBERT_MODEL_PATH = os.path.join(ML_MODELS_DIR, 'sbert_model')
KM_PATH = os.path.join(ML_MODELS_DIR, 'kmeans.pkl')

# Global variables to hold loaded models
vectorizer = None
kmeans = None

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        cluster = self.request.query_params.get('cluster')
        if cluster is not None:
            queryset = queryset.filter(cluster=cluster)
        return queryset

    def perform_create(self, serializer):
        global vectorizer, kmeans
        # Lazily load models only when needed
        if kmeans is None:
            try:
                # Load the S-BERT model for vectorization
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                vectorizer = SentenceTransformer(SBERT_MODEL_PATH, device=device)
                
                # Load the KMeans model for clustering
                kmeans = joblib.load(KM_PATH)
            except Exception as e:
                print('Error loading ML models:', e)
                vectorizer = None
                kmeans = None
                
        project = serializer.save()

        # Predict cluster using pre-trained models if available
        try:
            if vectorizer and kmeans:
                # BADLAV: technologies ko hata diya gaya hai
                text = f"{project.title} {project.description}"
                
                # Use S-BERT to create a dense vector
                X = vectorizer.encode([text])
                
                # Predict cluster using KMeans
                cluster = int(kmeans.predict(X))
                project.cluster = cluster
                project.save()
        except Exception as e:
            print('ML prediction failed:', e)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        instance = Project.objects.latest('created_at')
        out_ser = ProjectSerializer(instance, context={'request': request})
        return Response(out_ser.data, status=status.HTTP_201_CREATED, headers=headers)