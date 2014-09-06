function visualize(link) {
	var code_block = $(link).parent();

	var form = $('<form method="POST" target="_blank">');
	form.attr('action', '/visualizer/?lesson=' + lesson_name);

	var input = $('<textarea name="code">');
	input.text(code_block.find('pre')[0].textContent);
	form.append(input);

	var input = $('<input type="text" name="input">');
	input.val(code_block.data('input'));
	form.append(input);

	form.hide();
	$(document.body).append(form);
	form.submit();
}
