$(function() {
	$('#exampleLinks a').click(function(e) {
		var code_file = $(e.target).data('code');
		var input_file = $(e.target).data('input');

		$.get('/static/example-code/' + code_file, function(code) {
			visualizer.code = code;
		});

		if(typeof(input_file) !== 'undefined') {
			$.get('/static/example-code/' + input_file, function(stdin) {
				visualizer.stdin = stdin;
			});
		} else {
			visualizer.stdin = '';
		}

		return false;
	});

	$('#exampleLinks .default').click();
});

