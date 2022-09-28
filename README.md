
# what is this?

I like the idea of using
[seaborn-command](https://github.com/kojix2/seaborn-command) but dislike the
input choices.

So then I thought, why can't I push my yaml or json or whatever though a pandas
commandline that can reformat things in a way seaborn-command wants to see them?

But then I also started to wonder if it made sense to allow the pandas-cli to
output various matplotlib and seaborn formats directly... maybe...

# focus

look, this project is essentially a brainstorm, so I'm not really sure what it
should do or not do...

# stdin parsing thoughts

I'd really like to be able to `cat *.json | pd -f csv` and have useful output
come out. I don't think that's super realistic though. without some kind of file
separator, you end up having to do an O(n²) thing -- or perhaps much worse where
you do something like this

```
for line in sys.stdin:
    buffer += line
    for type_parser in types_we_know:
        try:
            dat = type_parser(buffer)
            results.append(dat)
            buffer = ""
            break
        except:
            pass # keep trying I guess
```
. For each line and for each type we just keep trying to parse? This is probably
fine for small files, but certainly not for large ones.

Otoh, some json-esque parsers seem to be able to handle inputs like this

```
{ "field": false }

{ "field": true }

{
    "field": "supz",
    "field2": "heh"
}
```

just fine -- in such parsers you'd just get three records or events. They have
the advantage, of course, of only having to deal with one file type. How would
such a thing work form yaml (look for the `---`? what if it's not there?).

This is really only a problem with stdin parsing. You'd expect properly
formatting things to be in proper filenames given as paths on the commandline.
