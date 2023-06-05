### CURRENT:

+ "Exp 1 [DONE]" -> "Exp 2.1 [DONE]" (add group number)

+ For `exp.success()` and `exp.fail()` check there's no other success or fail status - need that guard

+ Can't unpickle exp after re-oping in other notebook (DL2, hw_6-1, Group 1, Exp 1 and 2)
  + Try to use `dill` instead of `cloudpickle` - NO NEED, the issue was about `datasets` load its data from disk.
  In such cases it's better to add to the `train` run-func all needed code:
    ```
    !pip install datasets
    import datasets
    dataset = datasets.load_dataset('ag_news')
        
    import nltk
    nltk.download('punkt')
    ```
    
+ Opened under another account project doesn't recognize exp running in the first group as IN_PROGRESS and ACTIVE. Shows it as TO_DO. (exp 3.1 in DL2/hw_6-1)

+ Create exp with saving on storage, run exp and stop it manually in the cell. Start once again:
  ```
  IllegalOperationXManError: Can't recreate pipeline for exp `Exp 2 [IN_PROGRESS: IDLE] Baseline `mean` - {'aggregation_type': 'mean'}` - there's no `.run` data file! Use `save=True` for `make_pipeline()` method if you need to preserve `run_func` and `params` for other session.
  ```
  + Maybe it would be better if I didn't delete `.run` after an error, because I can tune some in imports and run. But need to delete `error` and `error_stack` on rerun, and review `start()`.

- Make 2 exp-s, xman.start(). The second exp started, but the first one was expected.

- `What For and Why` section before `Installation`:
  - Case 1: GPU, checkpoints, spent hours for nothing when GPU was dropped by Google
  - Case 2: Chaotic research without understanding



### BUGS:

- Colab cash doesn't allow to get actual info about experiments "/content/drive/.shortcut-targets-by-id/1G9R8MCoshlzIuEOrmbNzHnDSWEZi-4-b"
  - There also "/content/drive/.Trash-0"
  - There also "/content/drive/.file-revisions-by-id"

- Can't upload `xman` on pypi.org 
  +  Write a letter about `xman` repo to `support@pypi.org`
  - https://github.com/pypi/support/issues/2738
  - https://stackoverflow.com/questions/76304501/cant-register-my-package-on-pypi-org-pip-with-a-name-released-for-me-by-the-p



### TODO:

- Possibility to mark some exp with some marker in `info()`. I want to mark best or interesting exps. And clean that marker if it's needed.

- Documentation for each API method - py docstrings

- Test coverage:
  - Create own test file for each `xman` module
  - Each API method should be covered by tests
  - Each protected method with some logic should be covered by tests
  - Each private method with some logic should be covered by tests

- Add `__str__` and `_repr_pretty_` to xMan, show there the credits, version, quick help and links to documentation.


### BACKLOG:

- [LOW] Add `__str__` and `_repr_pretty_` to xMan, show there the credits, version, quick help and links to documentation.

- [LOW] How to solve the issue of multiple `update`-s in a chain `a.foo().bar().biz()`. I need to register each call in some `UpdateManager`, if it's the first call - set `is_chain` status to `True`, this status activates some other thread (e.g. by minimal timer) for setting `is_chain` back to `False`. Each of methods (foo, bar, biz) check `is_chain` flag, and if it's `True`, they skip `update`. In this case, the flag will be cleared right after the chain and the next chain starts again with `update`. I can add this logic to the root `super().update()` and it will return `False` if the chain were marked:
  ```
  if not super().update():
      return False
  ```
  If it's needed to update during protected calls, use `force` flag for `self._update(force=True)`.
  Check if `self.__updating` is still needed.
  If I implement the points above, then underscored protected methods (which duplicate public methods) will be obsolete?
  Force update for saving data and listeners

- [LOW] Save and load config for `config.py` under `.config` file for different levels: proj, group, exp

- [PRIO] How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 

- [PRIO] [!!!] Each exp takes ~ 2GB of disk size. Need to investigate how to reduce memory consumption. Maybe save separately proj-env, group-env, exp-env.

- [LOW] Save data classes in json format for human reading availability

- [???] XManError.__process_stack: Limit stack len via a config tb.format_stack()[:STACK_LIMIT]

- [???] Add printable info about timings on exp execution, savings, loadings

- [???] Set `.lock` file during writing, then remove. If there's an attempt to read during an exp was locked, set a series of timeouts, then raise an error that exp wasn't unlocked for somehow (too long writing time or some error with removing `.lock` file after writing). Error: "pickle data was truncated", then group has an error status and can't update for actual status (active in the other notebook and account)

- [???] Add printable info on start, save, load, etc...

- [LOW] Possibility to add custom `result_str` transformer for different levels: exp, group, proj. Save the transformer as a data field. Then check if exp has a custom one, then group has, then proj, then default str(result). Register result custom viewer on exp, group, and proj levels

- [LOW] __init__.py: __version__ = '0.0.0' - support auto setting from setup.py

- [LOW] Multiprocessing? Multithreading?

- [LOW] Config for xman and/or xman.mode(STRICT/PROMPT/CAREFREE) Settings in config for exp starting mode: STRICT - all prev should be closed (can't make new group before the previos one was closed?), PROMPT - show prompt for proceeding if something wasn't closed, CAREFREE - no control at all. Other settings for different behavioural features.

- [LOW] xman.guide_me() - analyzes current state and suggest what to do next. E.g. "Try to make a new project...", "Now it's time to create a group...", """You have experiments without finalized statuses...", etc.

- [LOW] Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure, and maybe it will be possible to make some converters from old to the newest versions.
       
- [LOW] Add runner info (link on notebook and colab account or mail) - from which notebook and who started an exp



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