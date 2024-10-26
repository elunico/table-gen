# Special Processors for CSV Files

## `@color:` Directive

### Format
CSV cells that begin with `@color:` can then specify any valid CSS color in any format. This includes hex codes, rga(), names, etc.

### Render
The `@color:` directive is rendered as a small, square div with the background color set to the color specified inline in the table cell

### Examples

`@color:#ff0`

`@color:lightblue`

`@color:rgba(100, 100, 0, 0.5)`

## `@img:` Directive

### Format
CSV cells that begin with `@img:` can then specify a valid image url and, optionally, a width, a height or both for the image.
The formats that are allowed are:
    `@img:URL` to display an image with the src of URL at its default dimensions
    `@img:URL$$W` to display an image with the src of URL at the given width W and an automatic height. The value for W should be in pixels
    `@img:URL$$WxH` to display an image with the src of URL at the given width W and height H. The value for W and H should be in pixels

### Render
The `@img:` directive is rendered as an img element with the given src url and optionally width and height set in CSS

### Examples

`@img:https://example.com/image.jpg`

`@img:https://example.com/large-image.jpg$$100`

`@img:https://example.com/should-be-square.jpg$$100x100`

## `@rand` Directive

### Format
CSV cells that contain `@rand` generate a random uniform decimal in the range [0, 1).
There are no allowed arguments to this directive

### Render
The `@rand` directive is rendered as the text of the resulting random number

### Examples

`@rand`

## `@html:` Directive

### Format
CSV cells that begin with `@html:` can will have the content of their cell following the `@html:` directive inserted directly into the webpage table without sanitization.
Ordinarily, text is HTML-escaped before being put in the table, but this directive prevents that escaping from happening.

The content following the colon is the HTML inserted directly into the webpage. No other arugments are allowed

### Render
The `@html:` directive puts the raw content of the cell directly into the webpage

### Examples

`@html:<iframe width='560' height='315' src='https://www.youtube.com/embed/ya3hZQgwHds?si=tBIcbO35698BUvRo' title='YouTube video player' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' referrerpolicy='strict-origin-when-cross-origin' id='youtube-6' allowfullscreen></iframe><style>#youtube-6 { width: auto; height: auto; }</style>`


## `@pydate` Directive

### Format
CSV cells that contain with `@pydate` will render as the text of the current date in 'ddd, MMMMMMM DD, YYYY' format in the locale timezone.

No arugments are allowed

### Render
The `@pydate` directive puts the text of the current date in 'ddd, MMMMMMM DD, YYYY' format in the current locale timezone into the page

### Examples

`@pydate`