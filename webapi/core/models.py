from django.db import models


class BaseModel(models.Model):
    """公共字段"""

    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True


# Create your models here.
class Category(BaseModel):
    """分类表"""

    name = models.CharField(max_length=128)

    class Meta:
        db_table = 't_category'

    def __str__(self):
        return self.name


class Product(BaseModel):
    """产品表"""

    name = models.CharField(
        max_length=128,
    )
    category = models.ForeignKey(
        Category,
        null=True,
        default=None,
        on_delete=models.SET(None),
        db_constraint=False,
    )

    class Meta:
        db_table = 't_product'

    def __str__(self):
        return self.name
