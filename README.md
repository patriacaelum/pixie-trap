# pixie-trap
Allows placing hitboxes for a sprite atlas and exports them in a JSON format.

## Workflow

### Load Canvas

When first running the program, the canvas will be blank. You can go to `File -> New` to select an image file to load as the canvas. Alternatively, go to `File -> Open` to open a workfile that was saved from a previous session.

### Select Sprite

When the image on the canvas is loaded, select the `Select` tool from the toolbar on the left. You can adjust the number of sprites on the sprite atlas altering the `Rows` and `Cols` entries in the inspector panel on the right side. By default, the sprite atlas is a single large sprite, but the sprites will divided using cyan coloured rulers across the canvas.

Once the sprites are divided correctly, use the mouse to select the sprite you want to work on. The selection will be shown in red, and when it is selected, that sprite will appear brighter than the sprites surrounding it.

The sprite label can also be changed in the inspector panel on the right side.

### Drawing Hitboxes

Next, select the `Draw` tool from the toolbar and begin drawing the hitboxes for the selected sprite. Click and drag anywhere on the canvas to create a rectangle.

### Adjusting the Hitboxes

Once the hitboxes have been drawn in roughly, select the `Move` tool from the toolbar and press on one of the rectangles. The hitbox properties on the right show the coordinates of the hitbox as well as the transparency, which can be adjusted.

There are also smaller squares around the edges of the selected rectangle, and these can be used to resize the hitbox for fine adjustment. The arrow keys can also be used to move the hitboxes pixel by pixel, and pressing `Delete` will remove the hitbox.

### Rinse and Repeat

The previous three steps should be repeated for any other sprites that are on the sprite atlus. If there are many that are overlapping, you can toggle the `Enable Isolate` on the inspector panel to only show the hitboxes that applicable to the currently selected sprite.

### Save and Export

Once you are happy with your progress, you can save the current workspace as a PXT file. This is really just a tarballed directory with the canvas image and the JSON data required to build the hitboxes again.

The rectangles can also be exported to JSON, which maps each sprite to their hitboxes, where each hitbox is mapped as label to coordinates.
