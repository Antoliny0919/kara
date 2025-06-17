'use strict'
{
    const ChooseBox = {
        cache: {},
        init: function(id) {
            // Remembers the initial state of each selection area.
            const box = document.getElementById(id);
            this.cache[id] = [];
            const cache = this.cache[id];
            const options = box.querySelector(`#${id}_options`).querySelectorAll('li');
            for (const node of options) {
                const input = node.querySelector('input');
                cache.push({node: node, value: input.value});
            }
        },
        redisplay: function(id) {
            // Repopulate select box from cache
            const box = document.getElementById(`${id}_options`);
            const scroll_value_from_top = box.scrollTop;
            box.innerHTML = '';
            for (const options of this.cache[id]) {
                box.appendChild(options["node"]);
            }
            box.scrollTop = scroll_value_from_top;
        },
        get_options: function(id) {
            const box = document.getElementById(id);
            const options = box.querySelector(`#${id}_options`).querySelectorAll('li');
            return options
        },
        add_to_cache: function(id, node, value) {
            this.cache[id].push({node: node, value: value});
        },
        delete_from_cache: function(id, value) {
            let delete_index = null;
            const cache = this.cache[id];
            for (const [i, item] of cache.entries()) {
                if (item.value === value) {
                    delete_index = i;
                    break;
                }
            }
            cache.splice(delete_index, 1);
        },
        cache_contains: function(id, value) {
            // Check if an item is contained in the cache
            for (const item of this.cache[id]) {
                if (item.value === value) {
                    return true;
                }
            }
            return false;
        },
        move: function(from, to) {
            const direction = from.split('_').pop();
            const from_box_options = this.get_options(from);
            for (const option of from_box_options) {
                const input = option.querySelector('input');
                // Move is allowed only if the ID of the selection area ends with "from" or "to".
                // Move occurs only if the transfer direction, checkbox selection 
                // and presence of the selected element in the selection area are all valid.
                if ((direction === 'from' && input.checked || direction === 'to' && !input.checked)) {
                    if (this.cache_contains(from, input.value)) {
                        this.add_to_cache(to, option, input.value);
                        this.delete_from_cache(from, input.value);
                    }
                }
            }
            this.redisplay(from);
            this.redisplay(to);
        }
    }
    window.ChooseBox = ChooseBox;
}
