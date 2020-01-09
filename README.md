Shimmer
-------

![badge](https://github.com/MartinHowarth/shimmer/workflows/Test/badge.svg)

Hello!

Testing
-------
The following command should be used to run the tests:

    poetry run pytest tests

For tests where a window is displayed, read the test description and
press `Y` or `N` to pass or fail the test. This is intended to allow humans
to validate that components look and behave as expected.

Most components have non-graphical testing as well that covers the event handling, 
but that is no replacement for a real human deciding whether it looks and feels good!

## Running all non-graphical tests.
Set `SKIP_GUI_TESTS=1` in your environment to skip graphical tests.

This skips all tests that require a GUI and user interaction.
