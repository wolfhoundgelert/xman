### CURRENT:




### TODO:

- BUG: Work from 2 accounts in parallel, sometimes the second one doesn't see the last exp started from the first one and it starts exp with the same number. If delete the first one exp in acc one, it won't be deleted under account two until deleting it manually in the second acc too. INVESTIGATION_RESULT: too long update ping at google drive that exp was deleted. And google drive make `folder(1)` (or `folder (1)` with space?) names for duplicates

- BUG: After I manually set statuses for exps in a group, I set a status for the group itself and it was showed as an old EMPTY status. Opened another notebook  - there everything was ok.

- BUG: after setting unsupported manual status (e.g. FAILED instead of FAIL), exp is corrupted and it is not possibly to set or remove status (only with illegal surgery on exp.data fields). Add checking for the status before assigning or smth like that

- BUG: two competting experiments (Exp 33 - here https://colab.research.google.com/drive/1fLUSxfhYe3iksLkaFRj2CLlEaEwKHK1H#scrollTo=ZQaM79timfej&uniqifier=8 and here https://colab.research.google.com/drive/1DW7nAIs7l4jOryjO4Tax_3hxB7cEOrjV?authuser=2#scrollTo=M1mHCEJnkzYp) One exp shadowed another one, but in google drive there are two folders `exp33` from different users

- BUG: Proj has status `DONE`, but should be `IN_PROGRESS`:
  ```
  # xman.proj.make_group('Tokenization', 'Try several tokenization technics')
  # xman.proj.group(1).make_exp('Default', 'Default settings: just split on words, vector_size=200, min_count=5, window=5')
  # xman.proj.group(1).make_exp('Punctuation', 'Remove punctuation')
  # xman.proj.group(1).make_exp('Stopwords', 'Remove stopwords (and punctuation)')
  # xman.proj.group(1).make_exp('Lemmatization', 'Lemmatize words (after removing stopwords and punctuation)')
  # xman.proj.group(1).make_exp('Lemmatization-2', 'Lemmatize words with nltk after fail with spacy (with removing stopwords and punctuation)')
  xman.proj.group(1).make_exp('Lowercase', 'Lowercase input')
  xman.proj
  ```
  ```
  Proj [DONE] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946

    Group 1 [IN_PROGRESS] Tokenization - Try several tokenization technics
        Exp 1 [SUCCESS *] Default - Default settings: just split on words, vector_size=200, min_count=5, window=5
        Exp 2 [SUCCESS *] Punctuation - Remove punctuation
        Exp 3 [SUCCESS *] Stopwords - Remove stopwords (and punctuation)
        Exp 4 [FAIL *] Lemmatization - Lemmatize words (after removing stopwords and punctuation)
        Exp 5 [FAIL *] Lemmatization-2 - Lemmatize words with nltk after fail with spacy (with removing stopwords and punctuation)
        Exp 6 [EMPTY] Lowercase - Lowercase input
  ```

- Add group info with verbose exp information:
  ```
  Exp 1 [FAIL *] Default - Default params: vector_size=100, min_count=5, window=5
    Resolution: Reduction vector_size from 200 to default 100 gives no significant effect
    Result:
        DCG@   1: 0.647 | Hits@   1: 0.647
        DCG@   5: 0.709 | Hits@   5: 0.761
        DCG@  10: 0.728 | Hits@  10: 0.820
        DCG@ 100: 0.767 | Hits@ 100: 1.000
        DCG@ 500: 0.767 | Hits@ 500: 1.000
        DCG@1000: 0.767 | Hits@1000: 1.000
        
  Exp 2 [FAIL *] 50-5-5 - Word2Vec params: vector_size, min_count, window
      Resolution: Reduction vector_size from 200 to 50 gives no significant effect
      Result:
          DCG@   1: 0.639 | Hits@   1: 0.639
          DCG@   5: 0.707 | Hits@   5: 0.767
          DCG@  10: 0.724 | Hits@  10: 0.817
          DCG@ 100: 0.763 | Hits@ 100: 0.999
          DCG@ 500: 0.763 | Hits@ 500: 1.000
          DCG@1000: 0.763 | Hits@1000: 1.000
  ```

- Add guard to `exp.set_manual_result()` for keeping the previous result. Need to manually remove the previous one with `exp.remove_manual_result()`

- Project status should be IN_PROGRESS:
  ```
  Proj [SUCCESS] hw_3-1 - https://stepik.org/lesson/940785/step/1?unit=946946

    Group 1 [IN_PROGRESS] Tokenization - Try several tokenization technics
        Exp 1 [SUCCESS *] Default - Default settings: just split on words, vector_size=200, min_count=5, window=5
        Exp 2 [EMPTY] Punctuation - Remove punctuation
  ```

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
       
- Add runner info (link on notebook and colab account or mail) - from which notebook and who started an exp

- Think about not saving the whole experiment (huge storage memory consumption and low speed of save-load operations), but provide a mechanic for saving checkpoints for long exp-s.

- Raname attach_pipeline to make_pipeline

- Return exp in methods like set_manual_status: `xman.proj.group(4).exp(1).set_manual_status(...).info()`

- Reassign group, num, name, descr to exp




### Q-A:

- How to parallel a huge grid-search (gs) exp? gs has number of experiments, but they all have the same env, so don't need to save each env separately. Does a group assume having the same env for all its children (exps)? 



### HOW-TO:
    
- Printing in jupyter notebook - _repr_pretty_:

    https://stackoverflow.com/a/41454816/9751954
    
- Dealing with `dill` lib:

    https://stackoverflow.com/a/28095208/9751954,

    https://oegedijk.github.io/blog/pickle/dill/python/2020/11/10/serializing-dill-references.html