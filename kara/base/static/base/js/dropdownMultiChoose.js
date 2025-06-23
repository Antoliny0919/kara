'use strict';
{
    window.SelectFilter = {
        init: function(field_id) {
            const dropdownPanel = document.getElementById(`${field_id}-dropdown-panel`);

            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                        const display = window.getComputedStyle(dropdownPanel).display;
                        if (display === 'none') {
                            // Run dropdownPanel is hidden state.
                            SelectFilter.display_selected(field_id);
                        }
                    }
                });
            });

            observer.observe(dropdownPanel, { attributes: true });

            dropdownPanel.addEventListener('click', function(e) {
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
        /* 
        ``display_selected`` and ``get_inner_color`` involve logic specific to components using ``dropdownMultiChoose``,
        where the resulting elements can encapsulate various types of data,
        and the exact structure of the resulting elements cannot be predicted from that data alone.
        This kind of logic pertains to the detailed behavior of a specific component
        and therefore needs to be separated through inheritance.
        */
        display_selected: function(id) {
            const box = document.getElementById(`${id}_selected`)
            box.innerHTML = '';
            const selectedOptions = ChooseBox.cache[`${id}_to`]
            for (const option of selectedOptions) {
                const node = option['node'];
                const nodeData = node.dataset;
                const hexColorCode = nodeData['hexColor'];
                const label = nodeData['label'];
                const li = document.createElement('li');
                li.className = 'tag';
                li.style.backgroundColor = hexColorCode;
                li.style.color = this.get_inner_color(hexColorCode);
                li.innerHTML = label;
                box.appendChild(li);
            }
        },
        get_inner_color: function(hexCode) {
            const hex = hexCode.replace('#', '');
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);

            const brightness = (r * 299 + g * 587 + b * 114) / 1000;

            return brightness > 128 ? '#000000' : '#ffffff';
        }
    };

    window.addEventListener('load', function(e) {
        document.querySelectorAll('div.dropdown-multi-choose').forEach(function(el) {
            const id = el.id;
            SelectFilter.init(id);
        });
    });
}
