# Debugging outputs
### USE LAMBDA ON NEXT UPDATE debugComment = lambda c: print(f"DEBUG: {c}") if DEBUG else continue

# Function for 'DEBUG:' notated comments
def debug_comment(e):
    """Simple output prefixed with 'DEBUG: '"""
    if DEBUG:
        print("\nDEBUG: {}".format(e))

# Function to print out a dict in a pretty way for 'DEBUG:' notated comments
def unpack_dict(dic):
    """Splits dict up for pretty outputs"""
    for key, value in sorted(dic.items(), key=lambda x: x[0]):
        print("\nDEBUG: {} : {}".format(key, value))
