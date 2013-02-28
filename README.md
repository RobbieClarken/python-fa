Installation
------------
Compile [FA archiver](http://controls.diamond.ac.uk/downloads/other/fa-archiver/) and ensure `fa-capture` is on your path.

Example
-------

```python
import fa
from matplotlib import pyplot

fa_data = fa.capture(range(1,99), samples=1000, server='10.17.100.25')
pyplot.plot(fa_data['data'][0,18,:])
pyplot.show()
```
