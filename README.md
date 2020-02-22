Shimmer
-------

<a href="https://github.com/MartinHowarth/shimmer/actions"><img alt="Actions Status" src="https://github.com/MartinHowarth/shimmer/workflows/Test/badge.svg"></a>
<a href="https://github.com/MartinHowarth/shimmer/blob/master/LICENSE"><img alt="License: MIT" src="https://img.shields.io/github/license/MartinHowarth/shimmer"></a>
<a href="https://pypi.org/project/shimmer/"><img alt="PyPI" src="https://img.shields.io/pypi/v/shimmer"></a>
<a href="https://pepy.tech/project/shimmer"><img alt="Downloads" src="https://pepy.tech/badge/shimmer"></a>
<a href="https://github.com/MartinHowarth/shimmer"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

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
