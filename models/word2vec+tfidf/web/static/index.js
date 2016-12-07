// Apache server ip config

$(function(){
	$('#query_button').click(function(){
    
		$.ajax({
			url: '/query',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				for (i=0; i<response['sim_lyrics'].length; i++) {
					id_html = '<div>' + response['sim_lyrics'][i][0] + '</div>';
                    lyric_html = '<div>' + response['sim_lyrics'][i][1] + '</div>';
					$('.jumbotron').append(id_html+lyric_html);
					console.log(response['sim_lyrics'][i][1]);
				}
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
