from guest import Guest

with Guest() as g:
    for msg in g.messages():
        print(msg)
