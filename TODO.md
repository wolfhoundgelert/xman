### CURRENT:

- BUG: Two competing experiments (Exp 33 - here https://colab.research.google.com/drive/1fLUSxfhYe3iksLkaFRj2CLlEaEwKHK1H#scrollTo=ZQaM79timfej&uniqifier=8 and here https://colab.research.google.com/drive/1DW7nAIs7l4jOryjO4Tax_3hxB7cEOrjV?authuser=2#scrollTo=M1mHCEJnkzYp) One exp shadowed another one, but in google drive there are two folders `exp33` from different users.

  Work from 2 accounts in parallel, sometimes the second one doesn't see the last exp started from the first one and it starts exp with the same number. If delete the first one exp in acc one, it won't be deleted under account two until deleting it manually in the second acc too. INVESTIGATION_RESULT: too long update ping at google drive that exp was deleted. And google drive makes `folder (1)` with space for duplicates: 

  '/content/drive/MyDrive/DL2/test_folder' and '/content/drive/MyDrive/DL2/test_folder (1)'

  Even more, there's no consistency which folder is marked (1). Under different accounts there different namings for the same two folders:

  It can't be solved by locking container dir (group or proj) on some timeout (found manually) as the second account won't see the `.lock` for the same reason.

  1) I can check such situations and ask users for solving. 
  2) I can recommend users to initially create (register) experiments in one place, then execute them under different accounts.
  3) I can provide users with a solution that "flatten" experiments automatically (it will change the order of experiments which follow the problematic "fork").

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

### BUGS:




### TODO:

- [PRIO] Implement 1 and 2 competing folders issue solving points:
  1) I can check such situations and ask users for solving. 
  2) I can recommend users to initially create (register) experiments in one place, then execute them under different accounts.

- [PRIO] [!!!] README.md

- [PRIO] How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 

- [PRIO] Possibility to change name or descr

- [PRIO] ??? Add possibility to make manual `force` update, save, load when we got stuck for somehow? Need to investigate:
  ```
  Proj [ERROR] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946
  
      Group 1 [ERROR] Tokenization - Try several tokenization technics
          Exp 1 [TODO] Punctuation - Remove punctuation
  ```

- [PRIO] [!!!] Each exp takes ~ 2GB of disk size. Need to investigate how to reduce memory consumption. Maybe save separately proj-env, group-env, exp-env. Other related issues: long saving and extremely long initialization on exp.start(). Separate project structure and status data loading from pipeline data loading - too long project loading. Loading exp pipeline data on demand.

- [PRIO] When an error occurs, there's only the final string of the error without a stack. Perhaps, it's better to raise the full error (Is it about an error during a pipeline execution?)

- [PRIO] [!!!] Think about not saving the whole experiment (huge storage memory consumption and low speed of save-load operations), but provide a mechanic for saving checkpoints for long exp-s.

- [PRIO] Reassign group, num, name, descr to exp



### BACKLOG:

- [???] Add printable info about timings on exp execution, savings, loadings
- 
- [???] Set `.lock` file during writing, then remove. If there's an attempt to read during an exp was locked, set a series of timeouts, then raise an error that exp wasn't unlocked for somehow (too long writing time or some error with removing `.lock` file after writing). Error: "pickle data was truncated", then group has an error status and can't update for actual status (active in the other notebook and account)

- [LOW] Add destructors for structures and over classes

- [LOW] Add printable info on start, save, load, etc...

- [LOW] Possibility to add custom `result_str` transformer for different levels: exp, group, proj. Save the transformer as a data field. Then check if exp has a custom one, then group has, then proj, then default str(result). Register result custom viewer on exp, group, and proj levels

- [LOW] __init__.py: __version__ = '0.0.0' - support auto setting from setup.py

- [LOW] Multiprocessing? Multithreading?

- [LOW] Add popular methods (`exp('1.1')` and others) to the xman root: `xman.exp('1.1')` - now it's only `xman.proj.exp('1.1')`

- [LOW] Config for xman and/or xman.mode(STRICT/PROMPT/CAREFREE) Settings in config for exp starting mode: STRICT - all prev should be closed (can't make new group before the previos one was closed?), PROMPT - show prompt for proceeding if something wasn't closed, CAREFREE - no control at all. Other settings for different behavioural features.

- [LOW] xman.guide_me() - analyzes current state and suggest what to do next. E.g. "Try to make a new project...", "Now it's time to create a group...", """You have experiments without finalized statuses...", etc.

- [LOW] Start exp with IN_PROGRESS status and IDLE type (was started but died somehow)

- [LOW] Save data structure version to the separated file `version.pkl`, it will help to recognize unmatched versions of saved file and xman data structure, and maybe it will be possible to make some converters from old to the newest versions.
       
- [LOW] Add runner info (link on notebook and colab account or mail) - from which notebook and who started an exp



### BUGS CAN'T REPRODUCE:

- (24.04.2023) After I manually set statuses for exps in a group, I set a status for the group itself and it was showed as an old EMPTY status. Opened another notebook  - there everything was ok.

- (27.04.2023) Project status should be IN_PROGRESS:
  ```
  Proj [SUCCESS] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946

    Group 1 [IN_PROGRESS] Tokenization - Try several tokenization technics
        Exp 1 [SUCCESS *] Default - Default settings: just split on words, vector_size=200, min_count=5, window=5
        Exp 2 [EMPTY] Punctuation - Remove punctuation
  ```


### Q-A:

- [PRIO] How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 



### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html