/*

Online Python Tutor
https://github.com/pgbovine/OnlinePythonTutor/

Copyright (C) 2010-2012 Philip J. Guo (philip@pgbovine.net)

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/

// Pre-req: edu-python.js and jquery.ba-bbq.min.js should be imported BEFORE this file


function enterEditMode() {
	$.bbq.pushState({mode: 'edit'});
}

function enterVisualizeMode(traceData) {
	curTrace = traceData; // first assign it to the global curTrace, then
	                      // let jQuery BBQ take care of the rest
	$.bbq.pushState({mode: 'visualize'});
	$('#inputDataOnVisualizing').val($('#inputData').val());
}


$(document).ready(function() {
	eduPythonCommonInit(); // must call this first!

	registerInputTextarea('pyInput');

	// be friendly to the browser's forward and back buttons
	// thanks to http://benalman.com/projects/jquery-bbq-plugin/
	$(window).bind('hashchange', function(e) {
		appMode = $.bbq.getState('mode'); // assign this to the GLOBAL appMode

		// default mode is 'edit'
		if(appMode == undefined) {
			appMode = 'edit';
		}

		// if there's no curTrace, then default to edit mode since there's
		// nothing to visualize:
		if(!curTrace) {
			appMode = 'edit';
			$.bbq.pushState({mode: 'edit'});
		}

		if(appMode == 'edit') {
			$('#pyInputPane').show();
			$('#pyOutputPane').hide();

		} else if(appMode == 'visualize') {
			$('#pyInputPane').hide();
			$('#pyOutputPane').show();
			window.scrollTo(0, 0);

			$('#executeBtn').html('Запустить программу');
			$('#executeBtn').attr('disabled', false);

			// do this AFTER making #pyOutputPane visible, or else
			// jsPlumb connectors won't render properly
			processTrace(curTrace, false);

		} else {
			assert(false);
		}
	});

	// From: http://benalman.com/projects/jquery-bbq-plugin/
	//   Since the event is only triggered when the hash changes, we need
	//   to trigger the event now, to handle the hash the page may have
	//   loaded with.
	$(window).trigger('hashchange');


	$('#executeBtn').attr('disabled', false);
	$('#executeBtn').click(function() {
		$('#executeBtn').html('Ваша программа выполняется...');
		$('#executeBtn').attr('disabled', true);
		$('#pyOutputPane').hide();

		var req = $.post('/visualizer/execute/', {
			user_script: $('#pyInput').val(),
			input_data : $('#inputData').val()
		});

		req.done(function(traceData) {
			renderPyCodeOutput($('#pyInput').val());
			enterVisualizeMode(traceData);
		});

		req.fail(function() {
			alert('Ой, на сервере случилась какая-то ошибка :(\nСкорее всего, дело в том, что ваша программа совершает слишком много действий. Проверьте, не заходит ли ваша программа в вечный цикл?');

			$('#executeBtn').html('Запустить программу');
			$('#executeBtn').attr('disabled', false);
		});
	});


	$('#editBtn').click(function() {
		enterEditMode();
	});


	$('#exampleLinks a').click(function(e) {
		var code_file = $(e.target).data('code');
		var input_file = $(e.target).data('input');

		$.get('/static/example-code/' + code_file, function(code) {
			$('#pyInput').val(code);
		});

		if(typeof(input_file) !== 'undefined') {
			$.get('/static/example-code/' + input_file, function(code) {
				$('#inputData').val(code);
			});
		} else {
			$('#inputData').val();
		}

		return false;
	});

	if($('#pyInput').val() == '') {
		$('#exampleLinks .default').click();
	}
});

