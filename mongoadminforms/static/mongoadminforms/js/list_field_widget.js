/**
 * Created by itsmurfs on 17/08/14.
 */

if($===undefined)
    //Use the one provided by django admin
    $ = django.jQuery;

function listFieldAddButtonAddAction(button_add) {

    var row = $($('div.list_field div input')[0]).clone();

    //cleaning the row
    row.attr("value", "");

    button_add.click(function(){
        $('div.list_field div').append(row.clone());

        return false;
    });
}

$(document).ready(function(){

    button_add = $('.list_field button');

    if (button_add.length !== 0) {

        listFieldAddButtonAddAction(button_add)
    }

    $("form").submit(function() {

        list_hidden_input = $(".list_field input[type=hidden]");

        if (list_hidden_input.length !== 0){

            json_list = [];

            $(".list_field input[type!=hidden]").each(function(){

                if (this.value!=='')
                    json_list.push(this.value);
                $(this).remove();
            });

            $(list_hidden_input).attr("value", JSON.stringify(json_list));



        }

    });

});