from cx_Freeze import setup, Executable

# import re
# import os
# import sys
#
# prog_name = os.path.basename(sys.argv[0])
#
# print(prog_name)

base = None

executables = [Executable('main.py', base=base)]

packages = ["idna"]
options = {
    'build_exe': {

        'packages': packages,
    },

}

setup(
    name="<any name>",
    options=options,
    version="<any number>",
    description='<any description>',
    executables=executables
)
