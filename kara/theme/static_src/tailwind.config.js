/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    important: true,
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',
        /* Django-components */
        '../../**/components/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    theme: {
        extend: {
            fontFamily: {
                'title': ['iceHimchan-Rg', 'sans-serif'],
                'sub-title': ['ChosunGu', 'sans-serif'],
                'question-title': ['Gowun Dodum', 'monospace'],
                'question-answer': ['iceHimchan-Rg', 'sans-serif'],
                'sub-text': ['ChosunGu', 'sans-serif'],
                'common': ['Pretendard-Regular', 'sans-serif'],
                'number': ['Orbitron', 'monospace'],
            },
            colors: {
                kara: {
                    'light': '#F3AFC2',
                    'base': '#E46A88',
                    'strong': '#C44B6B',
                    'title': '#212121',
                    'sub-title': '#343232',
                },
                'wedding-gifts': {
                    'registry': '#d4a237',
                    'cash-gift': '#3c8535',
                    'in-kind-gift': '#f5b2b2',
                },
                registry: {
                    'select-color': '#591f30',
                    'select-title-color': '#6f3143',
                }
            },
            keyframes: {
                'slide-down': {
                    '0%': { opacity: '0', transform: 'translateY(-30px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'slide-up-fade': {
                    '0%': { opacity: '1', transform: 'translateY(0)' },
                    '100%': { opacity: '0', transform: 'translateY(-30px)' },
                },
              },
              animation: {
                'slide-down': 'slide-down 0.5s ease-out',
                'slide-up-fade': 'slide-up-fade 0.5s ease-in forwards',
            },
        },
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
