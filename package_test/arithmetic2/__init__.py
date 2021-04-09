# https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder
# https://unix.stackexchange.com/questions/164025/exclude-one-pattern-from-glob-match
# https://stackoverflow.com/questions/20638040/glob-exclude-pattern
# from . import add
# from importlib import import_module

# If the name is specified in relative terms, 
# then the package argument must be set to the name of the package 
# which is to act as the anchor for resolving the package name
# add = import_module('.add', package = 'arithmetic2')


# 若想 from <package> import * 就包含所有的 modules in the package
# 須在 package 的 __init__ 定義一個 __all__ list，將 modules name 放進 __all__
__all__ = ['add']