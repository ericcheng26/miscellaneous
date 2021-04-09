def addition(x, y):
	return x + y
    
	
dir = dir()
__all__ = [o for o in dir if not '__' in o]

if __name__ == '__main__':
	print(globals())