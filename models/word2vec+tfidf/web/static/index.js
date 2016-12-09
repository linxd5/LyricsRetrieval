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
            data: $('form').serialize(),
            type: 'POST',
            success: function (response) {
                $('#lyrics_container').remove();
                sim_lyrics = '<div id="lyrics_container">';
                for (i = 0; i < response['sim_lyrics'].length; i++) {
                    id_html = '<div><a href="' + 'http://music.163.com/#/song?id=' + response['sim_lyrics'][i][0]
                        + '">' + response['sim_lyrics'][i][0] + '</a></div>';
                    console.log(id_html);
                    lyric_html = '<div>' + response['sim_lyrics'][i][1] + '</div>';
                    sim_lyrics += '<div id="lyric_container">' + id_html + lyric_html + '</div>' + '<br /><br />';
                }
                sim_lyrics += '</div>';
                $('.jumbotron').append(sim_lyrics);
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
});
