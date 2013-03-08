$(document).ready(function() {

	field = 'order';
	table = $('#result_list');
	tbody = table.children('tbody');
	rows = tbody.children('tr');

	// Find the column by which we should sort.
	column = rows.first().children().has('input[name*=' + field + ']').index();

	// No sortable column.
	if (column == -1) {
		return;
	}

	// Change cursor and hide order column.
	rows.css('cursor', 'move');
	table.find('tr :nth-child(' + (column + 1) + ')').hide();

	// Make the table sortable
	tbody.sortable({
		axis: 'y',
		items: 'tr',
		cursor: 'move',
		update: function(event, ui) {
			rows = $(this).find('tr');

			rows.each(function(index) {
				$(this).find('td:nth-child(' + (column + 1) + ') input:first').attr('value', index);
			});

			// Update row classes.
			rows.removeClass('row1 row2');
			rows.filter(':even').addClass('row1');
			rows.filter(':odd').addClass('row2');
		}
	});
});
