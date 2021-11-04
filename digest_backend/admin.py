from django.contrib import admin

from digest_backend import models

admin.site.register(models.Gene)
admin.site.register(models.SNP)
admin.site.register(models.Pathway)
admin.site.register(models.GO)
admin.site.register(models.Disorder)
admin.site.register(models.ICD10)
admin.site.register(models.DisorderToICD10)
admin.site.register(models.DisorderToGene)
admin.site.register(models.DisorderToSNP)
admin.site.register(models.DisorderToPathway)
admin.site.register(models.GeneToGO)
admin.site.register(models.GeneToPathway)