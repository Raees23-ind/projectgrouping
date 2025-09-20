from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'technologies', 'video', 'video_url', 'cluster', 'created_at']
        read_only_fields = ['cluster', 'created_at']

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video:
            try:
                url = obj.video.url
            except Exception:
                return None
            if request:
                return request.build_absolute_uri(url)
            return url
        return None