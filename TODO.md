### CURRENT:

- There's no proj and group status updates after adding a new exp (or a group). Need to reprocess statuses. Why is there silent crash in the jupyter notebook if I try to run the code below for groups and projects?
```
def _update(self):
    if not super()._update():
        helper._process_status(self)
        return False
```

### TODO:

- `ExpStructContainer` base class
- Create only new instances on update - reuse ones created before
- Implement saving source code of `run_func` of `pipeline` and it's `params`.
I tried `dill` lib for it, but something went wrong - can't print saved `train` function.
- Group 1 [IN_PROGRESS] Test Group - Test group descr or
Group 1 [IN_PROGRESS *] Test Group - Test group descr (* in the status means `manual`)
-  ??? Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure and maybe it will be possible to make some converters from old to the newest versions.
       



### Q-A:





### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html