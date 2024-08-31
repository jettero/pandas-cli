
# I've had the idea to make this more than once

I started making this like two years ago, but lost interest. Then I started
making it again (see contrib/pd-thing). I didn't finish it, but I remembered I
had the same idea before. Maybe by copying my new version into contrib/ I'll
suddenly start working on this again? we'll see.

My fresher energy ideas (although I still like the below) is that I really need
a way to combine various input csvs column-wise or row-wise (or maybe horizontal
vs vertical)... anyway, my point is that there needs to be an expressive
input/output macro-language so I can get what I want in the end.

pd-thing can do the following (poorly):

- concatenate several csv files, some with headers, some without
- combine the rows from two or more csv files, joined on a key field
- output the rows of a single csv that don't match entries from the following
  files

It doesn't do these things particularly well, but my first goals on resurrection
will be to transpo those abilities into this fledgling project ... and then come
up with some kind of macro language to facilitate the above and anything else
the user might imagine.

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
