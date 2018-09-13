$(function () {
    $('#change_btn').click(function () {
        $('input[name!="pub_id"]').removeAttr('readonly');
        $('textarea').removeAttr('readonly');
        $('select').removeAttr('disabled');
        $('#submit_btn').removeAttr('hidden');
    });
});