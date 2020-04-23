mylist = ['abc123', 'def456', 'ghi789']
sub = 'abc'
next((print(s) for s in mylist if sub in s), None) # returns 'abc123'