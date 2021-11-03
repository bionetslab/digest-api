from django.db import models


# ------------------------------
# ID mappings
# ------------------------------


class Gene(models.Model):
    entrez = models.CharField(max_length=128, unique=True, primary_key=True)
    ensembl = models.CharField(max_length=128, default='')
    symbol = models.CharField(max_length=128, default='')
    uniprot = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.entrez


class Disease(models.Model):
    mondo = models.CharField(max_length=128, unique=True, primary_key=True)
    omim = models.CharField(max_length=128, default='')
    snomedct = models.CharField(max_length=128, default='')
    umls = models.CharField(max_length=128, default='')
    orpha = models.CharField(max_length=128, default='')
    mesh = models.CharField(max_length=128, default='')
    doid = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.mondo


class ICD10(models.Model):
    icd10 = models.CharField(max_length=128, unique=True, primary_key=True)

    def __str__(self):
        return self.icd10


class DiseaseToICD10(models.Model):
    mondo = models.ForeignKey('Disease', on_delete=models.CASCADE)
    icd10 = models.ForeignKey('ICD10', on_delete=models.CASCADE)


# ------------------------------
# Attribute mappings
# ------------------------------


class DiseaseToAttributes(models.Model):
    mondo = models.ForeignKey('Disease', on_delete=models.CASCADE)
    genes_list = models.CharField(default='')
    snps_list = models.CharField(default='')
    pathways = models.CharField(default='')
    