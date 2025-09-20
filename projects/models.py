from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    technologies = models.CharField(max_length=500)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    cluster = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.title} (cluster={self.cluster})"