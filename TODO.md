### CURRENT:

- [PRIO] How to solve the issue of multiple `update`-s in a chain `a.foo().bar().biz()`. I need to register each call in some `UpdateManager`, if it's the first call - set `is_chain` status to `True`, this status activates some other thread (e.g. by minimal timer) for setting `is_chain` back to `False`. Each of methods (foo, bar, biz) check `is_chain` flag, and if it's `True`, they skip `update`. In this case, the flag will be cleared right after the chain and the next chain starts again with `update`. I can add this logic to the root `super().update()` and it will return `False` if the chain were marked:
  ```
  if not super().update():
      return False
  ```
  If it's needed to update during protected calls, use `force` flag for `self._update(force=True)`.
  Check if `self.__updating` is still needed.
  If I implement the points above, then underscored protected methods (which duplicate public methods) will be obsolete? 

- [PRIO] Start exp with IN_PROGRESS status and IDLE type (was started but died somehow), use intermediate checkpoints.

- [PRIO] Add destructors for structures and over classes (check all files)



### BUGS:




### TODO:

- [PRIO] [!!!] README.md




### BACKLOG:

- [LOW] Save and load config for `config.py` under `.config` file for different levels: proj, group, exp

- [PRIO] How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 

- [PRIO] [!!!] Each exp takes ~ 2GB of disk size. Need to investigate how to reduce memory consumption. Maybe save separately proj-env, group-env, exp-env.

- [LOW] Implement filter: `xman.filter(...what to filter...)` - see `filter.py`

- [LOW] Save data classes in json format for human reading availability

- [???] XManError.__process_stack: Limit stack len via a config tb.format_stack()[:STACK_LIMIT]

- [LOW] change exp or group num

- [LOW] Move exp into another group

- [???] Add possibility to make manual `force` update, save, load when we got stuck for somehow? Need to investigate:
  ```
  Proj [ERROR] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946
  
      Group 1 [ERROR] Tokenization - Try several tokenization technics
          Exp 1 [TODO] Punctuation - Remove punctuation
  ```

- [???] Add printable info about timings on exp execution, savings, loadings
- 
- [???] Set `.lock` file during writing, then remove. If there's an attempt to read during an exp was locked, set a series of timeouts, then raise an error that exp wasn't unlocked for somehow (too long writing time or some error with removing `.lock` file after writing). Error: "pickle data was truncated", then group has an error status and can't update for actual status (active in the other notebook and account)

- [LOW] Add printable info on start, save, load, etc...

- [LOW] Possibility to add custom `result_str` transformer for different levels: exp, group, proj. Save the transformer as a data field. Then check if exp has a custom one, then group has, then proj, then default str(result). Register result custom viewer on exp, group, and proj levels

- [LOW] __init__.py: __version__ = '0.0.0' - support auto setting from setup.py

- [LOW] Multiprocessing? Multithreading?

- [LOW] Config for xman and/or xman.mode(STRICT/PROMPT/CAREFREE) Settings in config for exp starting mode: STRICT - all prev should be closed (can't make new group before the previos one was closed?), PROMPT - show prompt for proceeding if something wasn't closed, CAREFREE - no control at all. Other settings for different behavioural features.

- [LOW] xman.guide_me() - analyzes current state and suggest what to do next. E.g. "Try to make a new project...", "Now it's time to create a group...", """You have experiments without finalized statuses...", etc.

- [LOW] Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure, and maybe it will be possible to make some converters from old to the newest versions.
       
- [LOW] Add runner info (link on notebook and colab account or mail) - from which notebook and who started an exp

- [???] Do I need to pull factual event dispatching out from the current execution thread (by making small timeout)? Async dispatching.



### ON HOLD:

- BUG: Two competing experiments (Exp 33 - here https://colab.research.google.com/drive/1fLUSxfhYe3iksLkaFRj2CLlEaEwKHK1H#scrollTo=ZQaM79timfej&uniqifier=8 and here https://colab.research.google.com/drive/1DW7nAIs7l4jOryjO4Tax_3hxB7cEOrjV?authuser=2#scrollTo=M1mHCEJnkzYp) One exp shadowed another one, but in google drive there are two folders `exp33` from different users.

  Work from 2 accounts in parallel, sometimes the second one doesn't see the last exp started from the first one and it starts exp with the same number. If delete the first one exp in acc one, it won't be deleted under account two until deleting it manually in the second acc too. INVESTIGATION_RESULT: too long update ping at google drive that exp was deleted. And google drive makes `folder (1)` with space for duplicates: 

  '/content/drive/MyDrive/DL2/test_folder' and '/content/drive/MyDrive/DL2/test_folder (1)'

  Even more, there's no consistency which folder is marked (1). Under different accounts there different namings for the same two folders:

  It can't be solved by locking container dir (group or proj) on some timeout (found manually) as the second account won't see the `.lock` for the same reason.

  + 1) I can check such situations and ask users for solving. 
  + 2) I can recommend users to initially create (register) experiments in one place, then execute them under different accounts.
  - 3) I can provide users with a solution that "flatten" experiments automatically (it will change the order of experiments which follow the problematic "fork").

  ```
  print(os.listdir('/content/drive/MyDrive/DL2/test_folder'))
  print(os.listdir('/content/drive/MyDrive/DL2/test_folder (1)'))
  >>>
  ['.ipynb_checkpoints', 'second.txt']
  ['.ipynb_checkpoints', 'first.txt']
  ```
  And
  ```
  print(os.listdir('/content/drive/MyDrive/DL2/test_folder'))
  print(os.listdir('/content/drive/MyDrive/DL2/test_folder (1)'))
  >>>
  ['first.txt', '.ipynb_checkpoints']
  ['second.txt', '.ipynb_checkpoints']
  ```
  
  https://stackoverflow.com/questions/76106194/folders-created-with-python-code-from-2-colab-accounts-in-one-google-drive-share

  I've sent an email to a guy from the Colab team.



### BUGS CAN'T REPRODUCE:



### Q-A:

- [PRIO] How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 



### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html