"""This is the module of the mongoforms fields. There are 3 kinds of fields:

EmbeddedModelFormField is the field for an EmbeddedModel

ListFormField is the field for a ListField

ListEmbeddedModelFormField is the field for the ListField(EmbeddedModelField

Each field has its own widget

Each field can handle prepare_value to pass correctly the value to the widget.
Each field can handle to_python which converts the json inputs into a python structure using json.loads
Each field implements the clean method using the embedded field model if necessary.

The embedded fields are contained inside ListEmbeddedModelFormField and EmbeddedModelFormField. This fields are
genereted using fields_for_model, the model is passed to the field using "initial" attribute. This attribute is setted
inside the model field.

"""
from django.core.exceptions import ValidationError
from django.forms import TextInput

from mongoadminforms.widgets import EmbeddedModelFieldWidget, ListEmbeddedModelFieldWidget, ListFieldWidget
import json
from django import forms
from django.forms.models import fields_for_model
import copy


class EmbeddedModelFormField(forms.Field):

    widget = EmbeddedModelFieldWidget

    #Initial is the model class encapsulated inside the EmbeddedModel. We need it to retrieve the embedded_fields
    def __init__(self, required=True, widget=None, label=None, initial=None,
                 help_text=None, error_messages=None, show_hidden_initial=False,
                 validators=[], localize=False):

        self.embedded_fields = fields_for_model(initial)
        initial=None

        super(EmbeddedModelFormField, self).__init__(required, widget, label, initial,
                 help_text, error_messages, show_hidden_initial,
                 validators, localize)

    #This func converts the value FROM the MODEL TO the WIDGET
    #The value returned is passed eventually to the widget's render function
    def prepare_value(self, value):

        #Value is not None when we open the form in edit mode or when there is a validation error.
        #If value is not none we have to insert the initial value for each embedded field
        if value is not None:
            #it can be a json unicode string of the object or the object itself
            if isinstance(value,unicode):
                fields_value_as_dict = json.loads(value)
                fields = copy.deepcopy(self.embedded_fields)
                for (k,v) in fields.iteritems():
                    v.initial = fields_value_as_dict[k]

            elif isinstance(value, dict): #This case handles the ListEmbeddedModelFormField caller
                fields_value_as_dict = value
                fields = copy.deepcopy(self.embedded_fields)
                for (k,v) in fields.iteritems():
                    v.initial = fields_value_as_dict[k]

            else:
                fields= fields_for_model(value)
                for (k,v) in fields.iteritems():
                    v.initial = getattr(value,k)

            return fields

        else:
            #We have to do a deepcopy because embedded_fields is a dict whose values are Field references.
            return copy.deepcopy(self.embedded_fields)

    #This func converts the value FROM the WIDGET TO the MODEL
    #It coerces the value to correct data type and raises ValidationError if that is not possible.
    #It should take a json (from the hidden input value) and converts it into the embedded model's dict.
    def to_python(self, value):
        if not value:
            return {}

        #This is necessary when it is used a ListEmbeddedModelFormField because the conversion happens there.
        if isinstance(value, dict):
            return  value
        return json.loads(value)

    #We call the cleans of all embedded field in order to validate all the field of the embedded model
    #If a validation error occurs all the embedded form filed will be
    def clean(self, value):

        if self.required:
            #Runs normal behavior
            value = super(EmbeddedModelFormField, self).clean(value)
            for (k,v) in self.embedded_fields.iteritems():
                    value[k] = v.clean(value[k])
        else:
            #If not required runs the validator only if some field is filled
            if not self._is_all_embedded_fields_empty(value):
                for (k,v) in self.embedded_fields.iteritems():
                    value[k] = v.clean(value[k])

        return value


    def _is_all_embedded_fields_empty(self,value):

        #This statement builds the list of all dict values not empty. If it builds an empty list return false
        #which means that all values inside the dict are empty.
        #We can suppose that an empty value is an empty string because it is jsonified by javascript before submit
        return not bool([a for a in value.itervalues() if a!=''])

    def validate(self, value):

        super(EmbeddedModelFormField, self).validate(value)

        if self._is_all_embedded_fields_empty(value):
            raise ValidationError(self.error_messages['required'])


class ListFormField(forms.Field):

    widget = ListFieldWidget

    #This field is a special case in fact it returns both from model to widget and from html to model the values array
    #loaded from a json array. This happens because both the db and the html dials with a json while the python code
    #needs to dial with a python list.
    def prepare_value(self, value):

        if not value:
            return [""] #this can be useful in order to reuse the foreach inside the render function

        if isinstance(value, str):
            return json.loads(value)
        else:
            #it' s a list
            return value

    def to_python(self, value):
        if not value:
            return []
        return json.loads(value)


#A simple text form field
#Thanks to https://gist.github.com/jonashaag/1200165
#This can be useful when you want to change the behavior of your field inside the html page using some js plugin
class SimpleListFormField(forms.CharField):

    def prepare_value(self, value):
        return ', '.join(value)

    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


class ListEmbeddedModelFormField(forms.Field):

    widget = ListEmbeddedModelFieldWidget

    def __init__(self, required=True, widget=None, label=None, initial=None,
                 help_text=None, error_messages=None, show_hidden_initial=False,
                 validators=[], localize=False):

        self.embeddedModelFormField = EmbeddedModelFormField(initial=initial, required=required)
        initial=None

        super(ListEmbeddedModelFormField, self).__init__(required, widget, label, initial,
                 help_text, error_messages, show_hidden_initial,
                 validators, localize)

    #Value can be None or a list of EmbeddedModel or a list of string. In the last two case we call iteratively
    #prepare_value of the embeddedModelFormField
    def prepare_value(self, value):

        result = []

        if value is not None:
            if isinstance(value, list) and len(value)>0:
                for v in value:
                    result.append(self.embeddedModelFormField.prepare_value(v))
            elif isinstance(value, unicode):
                for v in json.loads(value): #v is an embedded model fields dict
                    result.append(self.embeddedModelFormField.prepare_value(v))

        if not result: #default case
            result = [self.embeddedModelFormField.prepare_value(None)]

        return result



    #This func converts the value FROM the WIDGET TO the MODEL
    #It coerces the value to correct data type and raises ValidationError if that is not possible.
    #It should take a list of json (from the hidden input value) and converts it into a list of embedded model's dict.
    def to_python(self, value):
        if not value:
            return []
        return json.loads(value)

    #We call the cleans of all embedded models fields in order to validate all the field of all embedded models
    #If a validation error occurs all the embedded form filed will be
    def clean(self, value):
        value = super(ListEmbeddedModelFormField, self).clean(value)
        result = []
        for e in value:
            result.append(self.embeddedModelFormField.clean(e))
        return result
