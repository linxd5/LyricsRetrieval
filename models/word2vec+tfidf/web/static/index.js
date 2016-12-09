// Apache server ip config

$(function () {
    $('#query_button').click(query);

    $('input').keypress(function (event) {
        if (event.which == 13) {
            event.preventDefault();
            query();
        }
    });

    function query() {
        $.ajax({
            url: '/query',
            // 将表单元素序列化为字符串，以便用于 Ajax 提交。
            data: $('form').serialize(),
            type: 'POST',
            success: function (response) {
                console.log(response);
                $('#songs_container').remove();
                sim_songs = '<div id="songs_container">';
                for (i = 0; i < response['sim_lyrics'].length; i++) {
                    id_html = '<div><a href="' + 'http://music.163.com/#/song?id=' + response['sim_lyrics'][i][0]
                        + '">'+ response['songs_info'][i]['name'] + ' - ' + response['songs_info'][i]['artists'] + '</a></div>';
                    lyric_html = '<div>' + response['sim_lyrics'][i][1] + '</div>';
                    pic_html = '<div class="img_container"> <img src="' + response['songs_info'][i]['picUrl'] +
                        '" alt="song_pic" height="150" width="150" /> </div>';
                    lyric_container = '<div class="lyric_container">' + id_html + lyric_html + '</div>';
                    sim_songs += '<div class="song_container">' + pic_html + lyric_container + '</div>';
                }
                sim_songs += '</div>';
                $('.jumbotron').append(sim_songs);
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
});
