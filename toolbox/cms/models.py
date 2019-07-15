from django.db import models


class STLFile(models.Model):
	name = models.CharField(max_length=225)
	path = models.URLField()
	date_created = models.DateTimeField()
	date_updated = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
