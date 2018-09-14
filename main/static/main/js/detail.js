$(function () {
    var pub_id=$('#pub_id_input').val();
    $('#change_btn').click(function () {
        $('input[name!="pub_id"]').removeAttr('readonly');
        $('textarea').removeAttr('readonly');
        $('select').removeAttr('disabled');
        $('#submit_btn').removeAttr('hidden');
    });
    $('#del_confirm_btn').click(function () {
        $.ajax({
            method: 'post',
            url: DEL_URL,
            data: {
                pub_id:$('#pub_id_input').val(),
                csrfmiddlewaretoken: window.CSRF_TOKEN
            }, // serializes the form's elements.
            success: function(data)
            {
                $('#delModal').modal('hide');
                console.log(data);
                var obj=JSON.parse(data);
                if(obj['success']==1)
                    $('#del_info_text').text("删除成功，请关闭此页面");
                else
                    $('#del_info_text').text("删除失败，请检查公开号");
                $('#delInfoModal').modal();
            },
            error:function (data) {
                $('#del_info_text').text("请求失败，请检查网络连接");
                $('#delInfoModal').modal();
            }
        });

    })
});