$(function () {
    $('#add_field_btn').click(function () {
        var field_count=$('#field_count').val();
        ++field_count;
        $('#query_field_container').append(
            '<div class="row my-2"><div class="col p-0 mx-1"><div class="input-group">' +
            '<div class="input-group-prepend">'+
            '<select class="input-group-text" name="query_field_'+field_count+'">'+
            $('#query_field_select').html()+
            '</select> </div>'+
            '<input name="query_text_'+field_count+'" type="text" class="form-control">'+
            '</div></div></div>');
        $('#field_count').attr('value',field_count)
    });

    var frm=$("#query_form");

    frm.submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        console.log('my submit');

        $.ajax({
            method: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(), // serializes the form's elements.
            success: function(data)
            {
                //console.log(data);
                var obj=JSON.parse(data);
                $('#result_count').text('('+obj['result_count']+')');
                $('#table_content').empty();
                var query_result=obj['query_result'];
                for(var i=0;i<query_result.length;++i) {
                    item=query_result[i];
                    var row=$(document.createElement("tr"));
                    for(var j=0;j<item.length;++j ) {
                        row.append('<td><a class="text-black" href="detail/?pub_id="' + item[2] + '">'+item[j]+'</a></td>');
                    }
                    $('#table_content').append(row);
                }
                if(!obj['has_next']){
                    $('#next_btn').addClass('disabled');
                }
                cur_page=obj['page'];
                $('#cur_page').text(cur_page);
                if(cur_page<=1){
                    $('#previous_btn').addClass('disabled');
                }

                //$('#query_show_div').append(data);
                //$('#result_header').text('查询结果('+$('#result_count').text()+')');

            }
        });

    });
});