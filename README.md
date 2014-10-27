django-mongoadminforms
======================

A simple and easy way to add a form implementation to the mongodb django model's fields

This application contains three layers: 

- the models layer
- the fields layer
- javascript layer

You need both in order to have an implemented forms widget inside the admin form.

## The Models Layer ##

The models layer  consist of the follows:

- ListFieldWithForm
- ListFieldWithSimpleForm
- EmbeddedModelFieldWithForm
- ListEmbeddedModelFieldWithForm

As you can see there are the same model's fields of `django-nonrel` but here they come with a form attached. For now it is a little bit redundant because there is a 1 on 1 correspondance between the form's field and the model's field. Maybe I will fix it later :) 

These model's fields will be used to pass the needed information to the form's fields. Using `formfield`[(link)](https://docs.djangoproject.com/en/dev/howto/custom-model-fields/#specifying-the-form-field-for-a-model-field) method we attach the right form's field to the model's field and in some case additional informations are passed within the *initial* argument that will be parsed inside the form's field in order to know how to render the widget.

Example:

In this case we just attach the right form's field:

	class ListFieldWithForm(ListField):
	
	    def formfield(self, **kwargs):
	        return models.Field.formfield(self, ListFormField, **kwargs)

Here, instead, we have to inform the form's field which kind of embedded model the model's field is handling:
	
	class EmbeddedModelFieldWithForm(EmbeddedModelField):
	
	    def formfield(self, **kwargs):
	        kwargs['initial'] = self.embedded_model
	        return models.Field.formfield(self, EmbeddedModelFormField, **kwargs)

These additional data are parsed as follows:

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

`fields_for_model`*[(link)](https://github.com/django/django/blob/master/django/forms/models.py#L155)* is a django utility method that, given a model class, returns an OrderedDict containing form fields for the model.

As you can see the *initial* argument is overriden by the model so, for now, the use of this model field's option isn't possible (for the *EmbeddedModelFieldWithForm* and for the *ListEmbeddedModelFieldWithForm*). You can still use all the other options.

## The Fields Layer ##

There are 4 kinds of fields:

- EmbeddedModelFormField is the field for an EmbeddedModel 
- ListFormField is the field for a ListField
- ListEmbeddedModelFormField is the field for the ListField(EmbeddedModelField)
- SimpleListFormField is the simplest field for a ListField. (Taken from [here](https://gist.github.com/jonashaag/1200165)) 

Each field has its own widget

Each field can handle `prepare_value` to pass correctly the value to the widget.
Each field can handle `to_python` which converts the json inputs into a python structure using json.loads
Each field implements the `clean` method using the embedded field model if necessary.

The embedded fields are used inside *ListEmbeddedModelFormField* and *EmbeddedModelFormField*. These fields are genereted using `fields_for_model`, the model is passed to the field using *initial* argument.

### The `prapare_value` and `to_python` functions ###

These two methods are the clue between the widget, the javascript layer and the models layer.

`prapare_value` converts the value FROM the MODEL to the WIDGET. It can be a json unicode string or an instance of the embedded object.

`to_python` converts the value FROM the WIDGET to the MODEL. It coerces the valure to correct data type and raise `ValidationErorr` if that is not possible. It should take a json (from the javascript layer) and converts it into the embedded model's dict.

### The `clean` function ###
It is rewritten for the two fields that handle an embedded model: *ListEmbeddedModelFormField* and *EmbeddedModelFormField*. Here we call the cleans of all embedded models fields in order to validate all the field of all embedded models. If a validation error occurs all the embedded form filed will be rejected


### The widgets ###
For now each field come with its own widget. As for the model's field this is a 1 on 1 correspondence but I hope to make this mechanism more DRY in the future. The widgets are the follows:

- *ListFieldWidget* which renders a `TextInput` with an add button. You can insert multiple input by adding others `TextInput` with that
button. You can change the `TextInput` with another input overriding the `embedded_widget` field of ListFieldWidget

- *EmbeddedModelFieldWidget* which renders a div with the fields of the embedded model.

- *ListEmbeddedModelFieldWidget* which renders the fields of the embedded model inside a table, one model per row. You can
change the wrapped elements overriding `get_wrap_element` and `render_list_field` which uses it.

Each widget imports its own javascript and its own css using the Media class. Again I know that it can be more dry importing only one js and only one css, maybe one day :D

## The javascript layer ##
This layer provide the conversions FROM the USER INPUTS to the JSON. In other words, when the user fill the widget and submit the form the javascript layer catch the event and builds the json of the input provided inside the widget. This json is passed to the server using the hidden input of the widget. 
In addition in some case it provides some dynamicity to the widgets.

N.B: This layer use JQuery. It isn't necessary for you to install it if you use `mongoadminforms` inside djang admin because this layer is smart enough to reuse the jquery loaded by django.


## Setup ##

Simply clone the repository and add it to your django project and to your INSTALLED_APP


## Usage ##
Every time you need a nonrel model's field with a form's field attached you have to declare the model's field using ones provided by **mongoadminsform** instead of the standard provided by django-nonrel. The correspondence is the follows:

- **ListFieldWithForm** or **ListFieldWithSimpleForm** instead of *ListField*
- **EmbeddedModelFieldWithForm** instead of *EmbeddedModelField*
- **ListEmbeddedModelFieldWithForm** instead of *ListField(EmbeddedModelFiled)*

# Example #

