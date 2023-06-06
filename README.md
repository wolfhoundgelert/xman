# xMan

`xMan` (E**x**periment **Man**ager) is a `Python` library for effective management and organising experiments in `Jupyter Notebooks` on thе `Google Colab` platform or local machines, or right in the Python `REPL` (Read-Eval-Print Loop) interactive mode.

It offers the following key features:
- ⭐ Keeping track of your experiments, providing a clear overview of your progress.
- ⭐ Saving results in a centralised location, such as a shared Google Drive folder, with the option to use intermediate checkpoints.
- ⭐ Rapid deployment and running experiments in parallel across multiple Google Colab accounts, making it a powerful tool for AI, ML, NN, and DL students, learners, enthusiasts, researchers and their teams. 😍

In particular, provided:

- Create, delete, rename, and move directories, and print directory tree with a depth limitation.

- Create a new project, load existing projects specified by their directory paths, update and reload projects.

- Print information about the project, specific groups or experiments, and retrieve various details such as location directory, directory tree, number, name, description, status, manual or automatic flag, etc.

- All the information is saved in storage.

- Retrieve groups and experiments by their numbers or names.

- Manage groups and experiments - create, delete, edit, move, retrieve children and obtain various information about them.

- Filter experiments and groups based on various parameters in different modes, with support for custom filters.

- Retrieve experiments that are ready to start, initiate such experiments without manual checking, and support automatic start of the next experiment.

- Support manual experiments and experiments with running pipelines, and view their results.

- Set manual statuses and manual results for manual experiments.

- Automatically set statuses for pipeline experiments.

- Protection for currently running experiments.

- Set a custom method for stringifying experiment results at the experiment, group, and project levels.

- Set a custom result viewer for viewing experiment results at the experiment, group, and project levels.

- Finalize experiments, groups, and projects after review, marking them with SUCCESS or FAIL statuses.

- Add notes in txt, json, and pickle formats to experiments, groups, and project structures.

- Save errors and error stacks in case of issues during pipeline execution.

- Save checkpoints during pipeline execution and load them later or start the pipeline from a specific saved point.

- Set markers on experiments to highlight specific experiments.

And so on...

## What for and why

You are probably familiar with the following situations:

1. You are looking for the optimal solution, just sorting through a lot of different network parameters and their combinations. After launching a dozen experiments, you find yourself losing track of what you've done and the corresponding results. Most importantly, you feel uncertain about which direction to pursue. It's a nightmare you'd rather forget. However, there's a way to salvage the situation. By structuring your experiments, conducting evaluative reviews, and keeping the results within easy reach, this tool will help you conserve effort and spare your nerves. You'll experience fewer chaotic launches, while significantly increasing the number of experiments. With a conscious approach, you can achieve exceptional model quality and bid farewell to the frustrations of the past. Explore [First glance](#first-glance) and [Performing experiments](#performing-experiments).


2. You are hard at work on a project in Google Colab. Your network training requires substantial time and computational resources, relying on the GPU (a heartfelt thanks and appreciation to Google and the Colab team for making their infrastructure available to anyone ❤️). The training process has been going for the third hour, but, suddenly, disaster strikes – you've exhausted your daily GPU limit. Now, you face the daunting task of migrating your experiment to a new Colab account and redeploying everything from scratch. This process consumes considerable time and frays your nerves. You've not deployed under a second (let alone a third) account, making the prospect of working in parallel and avoiding idle time, because it seems overly complicated and bewildering. And it remains unclear how to piece everything together later in different Jupyter Notebooks. It's a nightmare best forgotten. But fear not! Now you can swiftly deploy under any account, even starting from a completely empty Jupyter Notebook. And don't forget to use checkpoints saving feature during your train execution. Simply refer to the [Pipelines with checkpoints](#pipelines-with-checkpoints) and [Running in parallel under different Google Colab accounts](#running-in-parallel-under-different-google-colab-accounts) section for seamless execution.



## Installation
<details><summary>Click to expand/collapse</summary>

The `xMan` library can be downloaded from the `GitHub` [repository](https://github.com/wolfhoundgelert/xman):

```commandline
!pip install git+https://github.com/wolfhoundgelert/xman.git
```
❗ Currently, it is not available on `PyPI` - please help me to get the `xman` repository name by leaving a comment with a [polite request to the administration of PyPI](https://github.com/pypi/support/issues/2738)

</details>



## First glance
<details><summary>Click to expand/collapse</summary>

Let's assume that we work in Google Colab and want our experiments to be saved in Google Drive folder, which we can share lately among other Google Colab (and related Google Drive) accounts - it will be useful if we work in a team or/and want to execute experiments in parallel under different Google Colab accounts.

We need to mount our Google Drive:
```python
from google.colab import drive
drive.mount('/content/drive')
```

Import `xMan` library:
```python
from xman import xman
```

We can check our Google Drive directory:
```python
xman.dir_tree('./drive/MyDrive')
```

Make a new project for our experiments specifying the path, name and description:
```python
xman.make_proj('./drive/MyDrive/xman_exps', "My Proj Name", "My proj descr")
```

Or we can load already existed project:
```python
xman.load_proj('./drive/MyDrive/xman_exps')
```

Experiment is something we can "run" in a code (or in our life) with specified parameters. When we change parameters, we make a new experiment. Similar experiments combine into a group that is defined by some aspect we examine with our experiments with different parameters.

Thereby, we need to create a new group of experiments:
```python
xman.make_group('My Group 1', 'My group 1 descr')
# or xman.proj.make_group('My Group 1', 'My group 1 descr')
```

When we have a group, we can populate it with specific experiments (exp - single, exps - plural):
```python
xman.make_exp(1, 'My Exp 1', 'My exp 1 descr')
# or xman.make_exp('My Group 1', 'My Exp 1', 'My exp 1 descr')
# or xman.proj.group(1).make_exp('My Group 1', 'My Exp 1', 'My exp 1 descr')
```

You can view the information about your `proj`, `groups` and `exps`:
```python
# Detailed info:
xman.info()  # for the entire project
# or xman.group(1).info()  # for a particular group
# or xman.exp(1, 1).info()  # for a particular exp

# Output:
#     Proj [EMPTY] My Proj Name - My proj descr    
#     Resolution: -= auto status =-    
#     
#     Group 1 [EMPTY] My Group 1 - My group 1 descr    
#         Resolution: -= auto status =-    
#         
#         Exp 1 [EMPTY] My Exp 1 - My exp 1 descr    
#             Resolution: -= auto status =-

# Brief info:
xman.exp(1, 1)
# or xman.group
# or xman.proj

# Output:
#     Exp 1 [EMPTY] My Exp 1 - My exp 1 descr

# Brief info contains: struct_type struct_num [STATUS] Struct_name - Struct_descr
```

As you probably already noticed:
1. `xMan` API supports different styles:
    ```python
    # You can use chains of actions:
    xman.make_group(...).make_exp(...).set_pipeline().start().view_result()
    
    # Or work with objects:
    proj = xman.make_proj(...)  # or xman.load_proj(...) if proj already exist
    group = proj.make_group(...)  # or proj.group(num_or_name) if group already exist
    exp = group.make_exp(...)  # or group.exp(num_or_name) if exp alrady exists
    exp.start()
    exp.view_result()
    ```
2. Groups and exps can be reached by their numbers and names (so, group names should be unique in the project, and exps names should be unique in a one particular group):
    ```python
    xman.group(1)  # or xman.group('My Group 1')
    xman.exp(1, 1)  # or xman.exp('My Group 1', 'My Exp 1') or combine nums and names
    ```
3. Main structures are `proj`, `group` and `exp`. Each of them contains a reach set of various API functionality. The most often usable methods are duplicated in `xman` itself, so you don't need to call `xman.proj.group(1)` or even `xman.proj.group(1).exp(1)` every time you want to get some group or exp, or other often usable API, just call:
   ```python
   xman.group(1)
   xman.exp(1, 1)
   
   # Use direct calls only for some specific methods and properties, e.g.:
   xman.proj.change_group_num(...)  # for changing group number
   xman.proj.move_exp(...)  # for moving exp in other group
   ```
   So, as you can see, you don't need to save links on your groups and experiments. You can get them whenever you want regardless of the `Google Colab` sessions and previously executed cells in your `Jupyter Notebook`, and they are reachable from `xman` itself: `xman.exp(1, 1)`.

</details>



## Sharing across Google Colab accounts
<details><summary>Click to expand/collapse</summary>

In `Google Drive` share your project folder with some other account. Login on `Google Drive` under that account. On the left-side panel choose the `Shared with me` option, find the project shared folder, right click menu, choose `Add shortcut to Drive`. In the opened window choose the `All locations` tab, click `My Drive` option, then click `Add` button below.

Now you can open `My Drive` on the left-side panel and find the project shared folder there. 

Open a new `Jupyter Notebook` or a shared copy of the original one. I recommend always making a copy of your shared notebooks when you (or your teammates) work under other `Google Colab` accounts - it will keep your notebooks from cell output conflicting during execution.

In that notebook load the project:
```python
# Mount `Google Drive`:
from google.colab import drive
drive.mount('/content/drive')

# Install `xMan` library:
!pip install git+https://github.com/wolfhoundgelert/xman.git

# Import `xMan` library:
from xman import xman

# Load project passing its path:
xman.load_proj('./drive/MyDrive/xman_exps')

# Now you can work with your project under that other Google Colab account:
xman.info()
```

</details>



## Performing experiments
<details><summary>Click to expand/collapse</summary>

A life cycle of any experiment, either it is `ML` experiment written in code or it is some live experiment performing on a physics lesson, can be described by statuses from the next workflow:

`EMPTY` -> `TO_DO` -> `IN_PROGRESS` -> `DONE` or `ERROR` -> `SUCCESS` or `FAIL`

And it doesn't matter, we are performing our experiment manually and only writing down its results (and manually changing exp statuses for keeping track of our progress), or we are using some executable pipeline, which changes statuses automatically according to its state.

`EMPTY` - we just created a new exp record in our project and here we have only our exp name and description.

`TO_DO` - we prepared our exp for the execution (gathered all we need together and ready to start the exp).

`IN_PROGRESS` - the exp was started, and now it is in progress.

`DONE` or `ERROR` - our exp was finished smoothly, or we encountered some issues which didn't allow us to get a result.

`SUCCESS` or `FAIL` - we reviewed what we have after the previous step and decided the exp was successful (output was significant good, and we can use that further) or we failed (nothing significantly, or we had even worse results than before).

As was mentioned before, `xMan` provides 2 approaches for managing experiments: manually and with setting executable pipeline.

### Manual Experiments
<details><summary>Click to expand/collapse</summary>

`exp` (also `group` and `proj`) is assumed to be manual if its status was set manually:
```python
xman.exp(1, 1).is_manual  # False
xman.exp(1, 1).set_manual_status('TO_DO', 'Ready for start')
xman.exp(1, 1).is_manual  # True

xman.exp(1, 1).info()
# Output:
#    Exp 1 [TO_DO *] My Exp 1 - My exp 1 descr    
#        Resolution: Ready for start
```
Pay attention on the `*` in the status `[TO_DO *]`, it says that the `exp` has a manual status and is considered as a manual exp.

If some `exp` has a manual status, it can't be fed with an executable pipeline until the manual status is deleted. Use `xman.exp(...).delete_manual_status()` for deleting the manual status and making `exp` not manual again.

You can set a result manually and/or complete the exp:
```python
xman.exp(1, 1).set_manual_result('Answer to the Ultimate Question of Life, the Universe, and Everything is 42')
xman.exp(1, 1).success('The answer is good enough')  # or xman.exp(1, 1).fail('Too bad')
# shortening for xman.exp(1, 1).set_manual_status('SUCCESS', 'The answer is good enough')

xman.exp(1, 1).info()
# Output:
#     Exp 1 [SUCCESS *] My Exp 1 - My exp 1 descr    
#        Resolution: The answer is good enough    
#        Result:
#            Answer to the Ultimate Question of Life, the Universe, and Everything is 42
```

You can use manual exps such way:
```python
# Define the pipeline:
def train_pipeline(params...):
    # init model and environment
    # train model
    # validate and calculate score
    return result

# Define params and execute the pipeline:
params = ...
result = train_pipeline(params)

# Set the result manually:
xman.make_exp(...).set_manual_result(result)

# Review result...
xman.exp(...).info()

# ...and decide it is success or fail:
xman.exp(...).success(...)
```

</details>


### Pipeline Experiments

#### Pipelines without checkpoints
<details><summary>Click to expand/collapse</summary>

```python
# Define a pipeline without checkpoints:
def train_pipeline(param1, param2):
    # init model and environment
    # train model (takes some time)
    # validate and calculate score
    return f"Score 1: {param1 * 2}, Score 2: {param2 ** 2}"

# Make a new group for new group of experiments
xman.make_group('Another Group', 'Group for pipeline exps')

# Define params as a dict:
params = {'param1': 3, 'param2': 2}

# Make a new exp using params in its name:
xman.make_exp(2, f"Exp with {params['param1']} and {params['param2']}", 
              'My exp with pipeline')
# xman.exp(2, 1).status -> `EMPTY`

# Make the pipeline:
xman.exp(2, 1).make_pipeline(train_pipeline, params)
# xman.exp(2, 1).status -> `TO_DO`

# Start the exp with pipeline:
xman.exp(2, 1).start()
# xman.exp(2, 1).status -> `IN_PROGRESS`

# ...the execution took some time...

# xman.exp(2, 1).status -> `DONE`
xman.exp(2, 1).info()
# Output:
#     Exp 1 [DONE] Exp with 3 and 2 - My exp with pipeline    
#         Resolution: -= auto status =-    
#         Result:
#             Score 1: 6, Score 2: 4

# Finalise the exp:
xman.exp(2, 1).success("You're awesome!")
# xman.exp(2, 1).status -> `SUCCESS`
```

</details>

#### Pipelines with checkpoints
<details><summary>Click to expand/collapse</summary>

```python
# Define a pipeline with checkpoints (add `mediator` as the first param):
from xman.pipeline import CheckpointsMediator 

def train_pipeline_with_mediator(mediator: CheckpointsMediator, param1, param2):
    # init model and environment

    # if it's not the first run of this exp, and the exp wasn't completed, and
    # there was some saved checkpoint, you can init your train from the saved
    # in the checkpoint state:
    cp_paths = mediator.get_checkpoint_paths_list()
    if cp_paths is not None:
        cp = mediator.load_checkpoint(cp_paths[-1])
        # init using information from this loaded checkpoint

    # start train model

    # save checkpoint (e.g. after each N epochs), you can save anything 
    # you need for starting from this position:
    cp = '...my checkpoint...'
    mediator.save_checkpoint(cp, replace=True)

    # finish train model
    # validate and calculate score
    return f"Score 1: {param1 * 2}, Score 2: {param2 ** 2}"

# Define params as a dict:
params = {'param1': 4, 'param2': 3}

# Make a new exp using params in its name:
xman.make_exp(2, f"Exp with {params['param1']} and {params['param2']}", 
              'My exp with pipeline')
# xman.exp(2, 2).status -> `EMPTY`

# Make the pipeline:
xman.exp(2, 2).make_pipeline_with_checkpoints(
    train_pipeline_with_mediator, params)
# xman.exp(2, 2).status -> `TO_DO`

# Start the exp with pipeline:
xman.exp(2, 2).start()
# xman.exp(2, 2).status -> `IN_PROGRESS`

# ...the execution took some time...

# xman.exp(2, 2).status -> `DONE`
xman.exp(2, 2).info()
# Output:
#     Exp 2 [DONE] Exp with 4 and 3 - My exp with pipeline    
#         Resolution: -= auto status =-    
#         Result:
#             Score 1: 8, Score 2: 9

# Finalise the exp:
xman.exp(2, 2).success("Smile)")
# xman.exp(2, 2).status -> `SUCCESS`
```

After saving a checkpoint you can reach it with the mediator:
```python
mediator = xman.exp(2, 2).checkpoints_mediator  # get mediator
cp_paths = mediator.get_checkpoint_paths_list()  # get paths
if cp_paths is not None:
    cp = mediator.load_checkpoint(cp_paths[-1])  # get the last checkpoint
    print(cp)
 # Output:
 #     ...my checkpoint...
```

You can delete checkpoints with `xman.exp(2, 2).delete_checkpoints()`.

</details>
</details>



## Running in parallel under different Google Colab accounts
<details><summary>Click to expand/collapse</summary>

First, read the information about `Sharing across Google Colab accounts` in this document above. After you share your project, there are 2 ways of running experiments in parallel under different `Google Colab` accounts:
1. You can load your project under the second account, duplicate your `Jupyter Notebook` into this account, re-init all needed cells (e.g. prepare the data, define methods and variables, init your model), create and `start()` your new experiment (or just `start()` if the exp was already created under the first account).
2. Or you can make a pipeline for your new exp with a `save_on_storage=True` flag under the first account and just initiate the project under the second account (you don't need to duplicate your original notebook - just load the project, see `Sharing across Google Colab accounts` section).
   ```python
   xman.exp(...).make_pipeline(train_pipeline, params, save_on_storage=True)
   # or
   xman.exp(...).make_pipeline_with_checkpoints(
      train_pipeline_with_mediator, params, save_on_storage=True)
   ```   
   Pay attention to making your pipeline with the `save_on_storage=True` flag saves your run-function and parameters with all the dependencies they need (other definitions and variables). So it can be storage space consumable if you work with some big dataset - raw needed data from the current `Google Colab` session will be saved on your `Google Drive` in the according to the exp folder (it's easy to be several GB).

   P.S. You can use not only `xman.exp(...).start()`, but also `xman.group(...).start()`, and even `xman.start()` - these methods search ready to start experiments and start them. You can use `autostart_next=True` parameter if you prepared several experiments in advance.

All your results will be saved into the project shared `Google Drive` folder, so you can use as many accounts as you want. Regardless of which approach you'll choose, you can create any mess with or in your notebooks without worrying about it - all the results will be saved and organised in your project in one place. Sounds amazing, yeah? 😀 Just don't forget to duplicate your notebooks (not only share them) under different accounts to avoid conflicting between cell's output in the notebook's history.

> **Note:** `xMan` uses `cloudpickle` library for saving pipeline information for running exp in other runtimes. Sometimes `cloudpickle` can't resolve dependencies for saving and further extraction, e.g. some information from `datasets` or `nltk` libraries is placed to the storage. You have to perform such imports and initialisations in other runtime, or you can save them just into the `run_func` of your pipeline:
   ```python
   !pip install datasets
   import datasets
   dataset = datasets.load_dataset('ag_news')
   
   import nltk
   nltk.download('punkt')
   ```

</details>



## What's next

- Tests coverage.
- API Documentation coverage.
- CI/CD for the library releases.
- `grid-search` implementation (there are some issues with storage space consumption).
- `xman.guide_me()` will advise you what to do next (load proj, create group, create exp, finalise completed exps and so on). 
- Project management control modes, e.g. you can activate `STRICT` mode, in this case you're not allowed to make a new exp group until you finalise with `success` or `fail` all exps from the previous one - it will help you to keep things from getting messed up.
- UI forms.



## Conclusion

It is not a secret that `AI`, `ML`, `NN`, `DL` experiments take a huge amount of time, because often you have to sort through a huge number of parameters and configurations that cannot be kept in your head, and, for example, the process of training neural networks can take hours. This tool can help you to streamline your experiments and, moreover, run them in parallel under different `Google Colab` accounts. This gives you a competitive edge in the rapidly evolving AI technologies space.

Good luck! ❤️
