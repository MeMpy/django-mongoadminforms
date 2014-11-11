/**
 * Created by itsmurfs on 17/08/14.
 */

if($===undefined)
    //Use the one provided by django admin
    $ = django.jQuery;

$(document).ready(function(){

    $("form").submit(function() {

        embedded_hidden_input = $(".embedded_fields input[type=hidden]");

        if (embedded_hidden_input.length !== 0) {

            json = {};

            $(".embedded_fields input[type!=hidden]").each(function () {

                json[this.name] = this.value;
                $(this).remove();

            });

            $(embedded_hidden_input).attr("value", JSON.stringify(json));
        }


    });

});