ckan.module('creator_fields', function ($, _) {
    return {
        initialize: function () {
            const maxCreators = 5;

            // Count how many creators already have data
            let visible = 1;  // first is always visible
            for (let i = 2; i <= maxCreators; i++) {
                const firstName = $(`#field_creator_first_name_${i}`).val();
                const lastName = $(`#field_creator_last_name_${i}`).val();
                if (firstName || lastName) {
                    visible = i;  // show this index
                }
            }

            function toggleField(index, show) {
                $(`.creator-field[data-index="${index}"]`).each(function () {
                    $(this).css('display', show ? '' : 'none');
                });

                // Show/hide the separator below this pair
                const separator = $(`.creator-separator[data-index="${index}"]`);
                if (separator.length) separator.css('display', show && index < maxCreators ? '' : 'none');
            }

            // Hide all fields beyond the visible ones
            for (let i = 2; i <= maxCreators; i++) toggleField(i, i <= visible);

            // Add Creator button click
            $('#add-creator').on('click', function () {
                if (visible < maxCreators) {
                    visible++;
                    toggleField(visible, true);
                }
            });
        }
    };
});
