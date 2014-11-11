"""This module provides the widgets for the non-rel mongoforms fields.

There are 3 kinds of widgets:

ListFieldWidget which renders a TextInput with a button add. You can insert multiple input by adding TextInput with that
button. You can change the TextInput with another input overriding the embedded_widget field of ListFieldWidget

EmbeddedModelFieldWidget which renders a div with the fields of the embedded model.

ListEmbeddedModelFieldWidget which renders the fields of the embedded model inside a table, one model per row. You can
change the wrapped elements overriding get_wrap_element and render_list_field which uses it.



"""


from django import forms
from django.forms import widgets

#Custom widget
from django.utils.html import format_html
from django.utils.safestring import mark_safe




class ListFieldWidget(widgets.HiddenInput):

    embedded_widget = forms.TextInput

    class Media:
        js= ('mongoadminforms/js/list_field_widget.js',)
        css= {'all':('mongoadminforms/css/list_field_widget.css',)}


    #Return the html components which will be used as button to add more embedded model's fields
    def get_add_button(self):

        return "<button id=id_add_{name}> Add </button>"

    def render_list_field(self,name, value, attrs=None):

        list_field_name = "list_field_{name}".format(name=name)

        list_fields = ""

        for val in value:
            list_fields += self.embedded_widget().render(list_field_name, val, self.attrs)

        return format_html('<div id="div_{}">{}</div>',list_field_name, mark_safe(list_fields))

    #Returns HTML for the widget, as a Unicode string.
    def render(self, name, value, attrs=None):
        html = super(ListFieldWidget, self).render(name, "")

        list_html = self.render_list_field(name,value,attrs)

        button_add = format_html(self.get_add_button(), name=name)

        return format_html('<div class="list_field"> {input} {fields} {button}  </div>', input=html, button=button_add, fields=mark_safe(list_html))


class EmbeddedModelFieldWidget(widgets.HiddenInput):

    class Media:
        js = ('mongoadminforms/js/embedded_model_field_widget.js',)
        css = {'all' : ('mongoadminforms/css/embedded_model_field_widget.css',)}

    def _render_subwidget(self, subwidget_name, subfield):
        #Here we propagate the "superwidget"'s attributes inside the subwidgets.
        #TODO: understand if this is the correct behavior
        return subfield.widget.render(subwidget_name, subfield.initial, self.attrs)

    def render_embedded_fields(self, name, value, attrs=None):
        embedded_id_template = '{super_field}_id_{field_name}'
        embedded_html = ""
        label = '<label for="{field_id}">{field_name}:</label>'
        for (k,v) in value.iteritems():
            field_id = embedded_id_template.format(super_field=name, field_name=k)
            embedded_html += format_html("<p>{label} {field}</p>",
                                         label=format_html(label,field_id=field_id,field_name=k),
                                         field=self._render_subwidget(k, v))

        return embedded_html

    #Returns HTML for the widget, as a Unicode string.
    def render(self, name, value, attrs=None):
        html = super(EmbeddedModelFieldWidget, self).render(name, "")

        embedded_html = self.render_embedded_fields(name,value,attrs)

        return format_html('<div class="embedded_fields"> {input}  {fields} </div>', input=html, fields=mark_safe(embedded_html))


class ListEmbeddedModelFieldWidget(widgets.HiddenInput):

    class Media:
        js= ('mongoadminforms/js/list_embedded_model_field_widget.js',)
        css= { 'all' : ('mongoadminforms/css/list_embedded_model_field_widget.css',)}


    #Return the wrap element with {list_field} as placeholder. It will be replaced with
    #the html of the embedded fields generated by render_list_field
    def get_wrap_element(self):
        return '<table class="list_embedded_fields"> <thead> {0} </thead> <tbody> {1} </tbody> </table>'

    #Return the html components which will be used as button to add more embedded model's fields
    def get_add_button(self):

        return "<button id=id_add_{name}> Add </button>"



    #Builds the list fields' html. We build a table in which each row represents an embedded model
    #returns a pair (head_rows, body_rows)
    def render_list_field(self, name, value, attrs=None):
        #Value is a list of dict. Each dict represents an embedded model fields.

        head_col_template = "<th> {label} </th>"
        row_template = "<tr> {0} </tr>"
        col_template = "<td> {input} </td>"

        rows_html = ""
        head_html = ""

        for count, v in enumerate(value):

            if count==0:
                #builds the thead
                for (k, l) in v.iteritems():
                    head_html += format_html(head_col_template, label=k)

                head_html = format_html(row_template, mark_safe(head_html))

            embedded_fields_html = self.render_embedded_fields(name, v, count, attrs)

            cols_html = ""

            for f in embedded_fields_html:
                cols_html += format_html(col_template, input=f)

            rows_html += format_html(row_template, mark_safe(cols_html))

        return (head_html, mark_safe(rows_html))

    def _render_subwidget(self, subwidget_name, subfield):
        #Here we propagate the "superwidget"'s attributes inside the subwidgets.
        #TODO: understand if this is the correct behavior
        return subfield.widget.render(subwidget_name, subfield.initial, self.attrs)

    #Returns a list of embedded field formatted as html inputs.
    def render_embedded_fields(self, name, value, count, attrs=None):

        embedded_html = []

        for (k,v) in value.iteritems():
            embedded_html.append(self._render_subwidget(k,v))

        return embedded_html


    #Returns HTML for the widget, as a Unicode string.
    def render(self, name, value, attrs=None):
        html = super(ListEmbeddedModelFieldWidget, self).render(name, "")

        wrap_element = self.get_wrap_element()
        embedded_html = format_html(wrap_element, *self.render_list_field(name,value,attrs))
        button_add = format_html(self.get_add_button(), name=name)

        return format_html('<div class="list_embedded_fields"> {input} {embedded} {button} </div>', input=html, embedded=embedded_html, button=button_add)


