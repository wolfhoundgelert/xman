### CURRENT:

- 


### TODO:

- Config for xman and/or xman.mode(STRICT/PROMPT/CAREFREE) Settings in config for exp starting mode: STRICT - all prev should be closed, PROMPT - show prompt for proceeding if something wasn't closed, CAREFREE - no control at all
- IN_PROGRESS types ACTIVE, IDLE, UNKNOWN - need to implement pulse.__tick() method which saves timestamps for predicting current state of IN_PROGRESS (ACTIVE, IDLE, UNKNOWN)
- Start exp with IN_PROGRESS status and IDLE type (was started but died somehow)
-  ??? Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure and maybe it will be possible to make some converters from old to the newest versions.
       


### Q-A:



### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html