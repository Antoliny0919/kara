'use strict';
{
    window.SelectFilter = {
        init: function(field_id) {
            const chooseBlockContainer = document.getElementById(`${field_id}-choose-block-container`);

            chooseBlockContainer.addEventListener('click', function(e) {
                if (e.target.tagName === 'INPUT') {
                    if (e.target.closest(`.choose-block`).id === field_id + '_to') {
                        // Add to the selectable area.
                        ChooseBox.move(field_id + '_to', field_id + '_from');
                    } else {
                        // Add to the selected area.
                        ChooseBox.move(field_id + '_from', field_id + '_to');
                    }
                }
            });
            ChooseBox.init(field_id + '_from');
            ChooseBox.init(field_id + '_to');
        },
    };

    window.addEventListener('load', function(e) {
        document.querySelectorAll('div.checkbox-select-multiple').forEach(function(el) {
            const id = el.id;
            SelectFilter.init(id);
        });
    });
}
