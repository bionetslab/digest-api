from django.db import models


# ------------------------------
# ID mappings
# ------------------------------


class Example(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True)
    count = models.IntegerField()

    def __str__(self):
        return f'{self.name}-{self.count}'

    class Example:
        unique_together = ('name', 'count')


class Gene(models.Model):
    entrez = models.CharField(max_length=128, unique=True, primary_key=True)
    ensembl = models.CharField(max_length=128, default='')
    symbol = models.CharField(max_length=128, default='')
    uniprot = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.entrez


class SNP(models.Model):
    snp_id = models.CharField(max_length=128, unique=True, primary_key=True)

    def __str__(self):
        return self.snp_id


class Pathway(models.Model):
    kegg_id = models.CharField(max_length=128, unique=True, primary_key=True)

    def __str__(self):
        return self.kegg_id


class GO(models.Model):
    go_id = models.CharField(max_length=128, unique=True, primary_key=True)
    go_type = models.CharField(max_length=128)

    def __str__(self):
        return self.go_id


class Disorder(models.Model):
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


class DisorderToICD10(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    mondo = models.ForeignKey('Disorder', on_delete=models.CASCADE)
    icd10 = models.ForeignKey('ICD10', on_delete=models.CASCADE)


# ------------------------------
# Attribute mappings
# ------------------------------


class DisorderToGene(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    disorder_id = models.ForeignKey('Disorder', on_delete=models.CASCADE)
    gene_id = models.ForeignKey('Gene', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('disorder_id', 'gene_id')

    def __str__(self):
        return f'{self.disorder_id}-{self.gene_id}'


class DisorderToSNP(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    disorder_id = models.ForeignKey('Disorder', on_delete=models.CASCADE)
    snp_id = models.ForeignKey('SNP', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('disorder_id', 'snp_id')

    def __str__(self):
        return f'{self.disorder_id}-{self.snp_id}'


class DisorderToPathway(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    disorder_id = models.ForeignKey('Disorder', on_delete=models.CASCADE)
    pathway_id = models.ForeignKey('Pathway', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('disorder_id', 'pathway_id')

    def __str__(self):
        return f'{self.disorder_id}-{self.pathway_id}'


class GeneToGO(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    gene_id = models.ForeignKey('Gene', on_delete=models.CASCADE)
    go_id = models.ForeignKey('GO', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('gene_id', 'go_id')

    def __str__(self):
        return f'{self.gene_id}-{self.go_id}'


class GeneToPathway(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    gene_id = models.ForeignKey('Gene', on_delete=models.CASCADE)
    pathway_id = models.ForeignKey('Pathway', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('gene_id', 'pathway_id')

    def __str__(self):
        return f'{self.gene_id}-{self.pathway_id}'

