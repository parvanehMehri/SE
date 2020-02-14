$(document).ready(function () {
    const course_id = $('input[name="course_id"]').val();
    $('input[name="rating"]').each(function (index, value) {
        $(value).on('change', function (event) {
            const rate = $(this).val();
            $.post('/rate_video', {rate: rate, course_id:course_id}, function (result) {
                $('#avg_rate').text('avg rate : ' + result);
            })
        })
    })
    const rated_value = $('input[name="temp_rate"]').val();
    $('input[name="rating"][value="' + rated_value + '"]').prop("checked", true);
});