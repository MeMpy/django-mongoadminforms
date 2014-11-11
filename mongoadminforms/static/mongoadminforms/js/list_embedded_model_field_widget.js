/**
 * Created by itsmurfs on 17/08/14.
 */

if($===undefined)
    //Use the one provided by django admin
    $ = django.jQuery;

function listEmbeddedModelFielAddButtonAddAction(button_add) {

    var row = $($('.list_embedded_fields tbody tr')[0]).clone();

    //cleaning the row
    row.find('input').each(function(){
        this.value  = "";
    });

    button_add.click(function(){
        $('.list_embedded_fields tbody').append(row.clone());

        return false;
    });
}


$(document).ready(function(){

    button_add = $('.list_embedded_fields button');

    if (button_add.length !== 0) {

        listEmbeddedModelFielAddButtonAddAction(button_add)
    }

    $("form").submit(function() {

        list_embedded_hidden_input = $(".list_embedded_fields input[type=hidden]");

        if (list_embedded_hidden_input.length !== 0){

            json_list = [];


            $(".list_embedded_fields tbody tr").each(function(){

                json = {};

                $(this).find('input').each(function () {

                    json[this.name] = this.value;
                    $(this).remove();

                });

                //TODO check if the json is empty
                json_list.push(json);
            });


            $(list_embedded_hidden_input).attr("value", JSON.stringify(json_list));



        }
    });

});