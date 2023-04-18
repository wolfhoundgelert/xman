### CURRENT:




### TODO:



- Possibility to change name or descr

- ??? Add possibility to make manual `force` update, save, load when we got stuck for somehow? Need to investigate:
  ```
  Proj [ERROR] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946
  
      Group 1 [ERROR] Tokenization - Try several tokenization technics
          Exp 1 [TODO] Punctuation - Remove punctuation
  ```

- Add printable info on start, save, load, etc...

- Add printable info about timings on exp execution, savings, loadings

- Add settable verbosity level

- !!! Each exp takes ~ 2GB of disk size. Need to investigate how to reduce memory consumption. Maybe save separately proj-env, group-env, exp-env. Other related issues: long saving and extremely long initialization on exp.start(). Separate project structure and status data loading from pipeline data loading - too long project loading. Loading exp pipeline data on demand.

- When an error occurs, there's only the final string of the error without a stack. Perhaps, it's better to raise the full error.

- Set `.lock` file during writing, then remove. If there's an attempt to read during an exp was locked, set a series of timeouts, then raise an error that exp wasn't unlocked for somehow (too long writing time or some error with removing `.lock` file after writing). Error: "pickle data was truncated", then group has an error status and can't update for actual status (active in the other notebook and account)

- Add popular methods (`exp(1.1)` and others) to the xman root: `xman.exp(1.1)` - now it's only `xman.proj.exp(1.1)`

- Prompt for removing anything - remove_manual_status, remove_manual_result, remove_pipeline, remove_group, remove_exp, etc...

- Config for xman and/or xman.mode(STRICT/PROMPT/CAREFREE) Settings in config for exp starting mode: STRICT - all prev should be closed, PROMPT - show prompt for proceeding if something wasn't closed, CAREFREE - no control at all

- Start exp with IN_PROGRESS status and IDLE type (was started but died somehow)

-  ??? Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure and maybe it will be possible to make some converters from old to the newest versions.
       


### Q-A:



### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html