from django.db import models

# Create your models here.
from djangotoolbox.fields import ListField, EmbeddedModelField
from mongoadminforms.fields import ListFormField, EmbeddedModelFormField, ListEmbeddedModelFormField, SimpleListFormField


class ListFieldWithForm(ListField):

    def formfield(self, **kwargs):
        return models.Field.formfield(self, ListFormField, **kwargs)


class ListFieldWithSimpleForm(ListField):

    def formfield(self, **kwargs):
        return models.Field.formfield(self, SimpleListFormField, **kwargs)


class EmbeddedModelFieldWithForm(EmbeddedModelField):

    def formfield(self, **kwargs):
        kwargs['initial'] = self.embedded_model
        return models.Field.formfield(self, EmbeddedModelFormField, **kwargs)


class ListEmbeddedModelFieldWithForm(ListField):

    def formfield(self, **kwargs):
        kwargs['initial'] = self.item_field.embedded_model
        return models.Field.formfield(self, ListEmbeddedModelFormField, **kwargs)

