from textwrap import dedent
from catswalk.scraping.driverfunc.jquery import import_jquer

def wait_until_images_loaded(driver, timeout=30):
    """Waits for all images & background images to load."""
    driver.set_script_timeout(timeout)
    import_jquer(driver)
    driver.execute_async_script(dedent('''
        function extractCSSURL(text) {
            var url_str = text.replace(/.*url\((.*)\).*/, '$1');
            if (url_str[0] === '"') {
                return JSON.parse(url_str);
            }
            if (url_str[0] === "'") {
                return JSON.parse(
                    url_str
                        .replace(/'/g, '__DOUBLE__QUOTE__HERE__')
                        .replace(/"/g, "'")
                        .replace(/__DOUBLE__QUOTE__HERE__/g, '"')
                );
            }
            return url_str;
        }
        function imageResolved(url) {
            return new $.Deferred(function (d) {
                var img = new Image();
                img.onload = img.onload = function () {
                    d.resolve(url);
                };
                img.src = url;
                if (img.complete) {
                    d.resolve(url);
                }
            }).promise();
        }
        var callback = arguments[arguments.length - 1];
        jQuery.when.apply($, [].concat(
            jQuery('img[src]')
                .map(function (elem) { return $(this).attr('src'); })
                .toArray(),
            jQuery('[style*="url("]')
                .map(function () { return extractCSSURL($(this).attr('style')); })
                .toArray()
                .map(function (url) { return imageResolved(url); })
        )).then(function () { callback(arguments); });
        return undefined;
    '''))