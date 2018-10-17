This is a simple Python script that generates a Cython .pxd file for the OpenGL API. This allows one to directly use OpenGL from Cython without going through one of the existing (slow) Python libraries. It generates the .pxd using gl.xml pulled from the [OpenGL API registry](https://github.com/KhronosGroup/OpenGL-Registry).

You can either run the script yourself to get the latest version, or download opengl.pxd directly. If you choose the latter option, you will have to edit the file manually to change the included OpenGL header.

You shouldn't change `cdef extern from ...` to `cdef extern from *`, since it is typical for loaders to define OpenGL functions as macros instead of symbols (and because opengl.pxd doesn't include enum values).

To run the script (only guaranteed to work with Python 3.7):
```
python gen_opengl_pxd.py -i '<gl.h>' -o opengl.pxd
```

Be sure to clone with `git clone --recursive`.
