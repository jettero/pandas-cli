# where is the setup.py?

Yeah, that hasn't been a thing since like 2021. Pfft. (I rarely remember what
you're supposed to do instead though.)

To install, you just
```
pip install .
```

And to build a binary or whatever, you'd do something like this
```
pip install build
python -m build
```

The whole point of using setup.cfg and pyproject.toml instead of setup.py is so
to allow different tools to evolve in place of setuptools (which never wanted to
be in the scripting business in the first place apparently).

There's actually a [whole matrix](https://wiki.python.org/moin/ConfigurationAndBuildTools) of build tools.
There's a similar
[matrix](https://wiki.python.org/moin/PythonTestingToolsTaxonomy) of testing
tools as well.


