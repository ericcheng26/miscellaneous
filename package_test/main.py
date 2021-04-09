# https://stackoverflow.com/questions/4858100/how-to-list-imported-modules
# https://stackoverflow.com/questions/5527415/how-to-get-all-objects-in-a-module-in-python
import arithmetic

while True:
  utility = input('Please enter a keyword or "done" to leave.\n')

  # dir(<object>) == <object>.__dir__()
  # vars(<object>) == <object>.__dict__
  if (not '__' in utility) and utility in dir(arithmetic):
    utility = vars(arithmetic)[utility]
    break
  
  elif utility == 'done':
    break
  
  else:
    print('No such keyword!')
    continue