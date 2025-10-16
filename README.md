Run the program from a terminal, providing a file to display. For example:

./matrix_file_rain -m mixed -s 50 myfile.bin

This will open myfile.bin and stream its contents in mixed mode at the default speed (50 ms frame delay). You can omit -m mixed -s 50 since those are the defaults – they are just shown here for clarity. If you want purely ASCII output, use -m ascii, or for hex-only output use -m hex. You can also specify a different initial speed via -s. Once running, watch the file’s bytes rain down the screen in real time! Press “q” to quit the program. You can also speed up or slow down the animation while it runs: press f (or the up-arrow key) to increase the rate, or s (or down-arrow) to decrease it.
Example: Suppose myfile.bin begins with bytes 0x48 0x65 0x6C 0x6C 0x6F (which spell "Hello"). In ASCII mode, you would eventually see those letters H e l l o falling in the columns. In hex mode, you’d see 48 65 6C 6C 6F appear in the rain. In mixed mode, some columns might show He ll o as characters while others show 48 65 6C ... in hex, with the representation switching as the columns reset. The effect is a scrolling matrix of characters where both the hex values and ASCII symbols of the file’s bytes flow down the screen.

Or... if you're having trouble, try the GUI I made using Python. Simply run it with python3 matrix_rain_gui.py, click Open File…, pick your file, and enjoy the rain!
