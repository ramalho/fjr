from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ['name']

    def flag(self):
        if self.country:
            return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in self.country.upper())
        return ''

    flag.short_description = 'country'

    def __str__(self):
        if f := self.flag():
            return f'{f} {self.name}'
        return self.name


class RollingStock(models.Model):
    LOCOMOTIVE = 'L'
    COACH = 'C'
    FREIGHT = 'V'
    TYPE_CHOICES = [
        (LOCOMOTIVE, 'Locomotive'),
        (COACH, 'Coach'),
        (FREIGHT, 'Freight car'),
    ]

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    era = models.CharField(max_length=5, blank=True)
    dcc_address = models.PositiveSmallIntegerField(null=True, blank=True)
    acquired = models.CharField(max_length=7, blank=True)
    prototype = models.CharField(max_length=200, blank=True)
    product_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['type', 'brand', 'code']
        verbose_name = 'Rolling Stock'
        verbose_name_plural = 'Rolling Stock'

    def __str__(self):
        return f'{self.brand} {self.code} — {self.description}'
