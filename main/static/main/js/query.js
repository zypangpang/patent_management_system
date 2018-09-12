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
    })
});