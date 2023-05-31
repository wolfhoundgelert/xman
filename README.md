# xMan

`xMan` (E**x**periment **Man**ager) is a `Python` library for effective managing and organizing experiments in `Jupyter Notebooks` on thе `Google Colab` platform or local machines, or right in the Python `REPL` (Read-Eval-Print Loop) interactive mode.

It offers the following key features:
- ⭐ Keeping track of your experiments, providing a clear overview of your progress.
- ⭐ Saving results in a centralized location, such as a shared Google Drive folder, with the option to use intermediate checkpoints.
- ⭐ Running experiments in parallel across multiple Google Colab accounts, making it a powerful tool for AI, ML, NN, and DL students, learners, enthusiasts, researchers and their teams. 😍



## Installation
<details><summary>Click to expand/collapse</summary>

The `xMan` library can be downloaded from the `GitHub` [repository](https://github.com/wolfhoundgelert/xman):

```commandline
!pip install git+https://github.com/wolfhoundgelert/xman.git
```
❗ Currently, it is not available on `PyPI` - please help me to get the `xman` repository name by leaving a comment with a [polite request to the administration of PyPI](https://github.com/pypi/support/issues/2738)

</details>


## Usage
<details><summary>Click to expand/collapse</summary>

Let's assume that we work in Google Colab and want our experiments to be saved in Google Drive folder, which we can share lately among other Google Colab (and related Google Drive) accounts - it will be useful if we work in a team or/and want to execute experiments in parallel under different Google Colab accounts.

We need to mount our Google Drive:
```python
from google.colab import drive
drive.mount('/content/drive')
```

Import xman library:
```python
from xman import xman
```

We can check our Google Drive directory:
```python
xman.dir_tree('./drive/MyDrive')
```

Create a folder for our experiments specifying the path, name and description:
```python
xman.make_proj('./drive/MyDrive/xman_exps', "My Proj Name", "My proj descr")
```

Or we can load already existed project:
```python
xman.load_proj('./drive/MyDrive/xman_exps')
```

Experiment is something we can "run" in a code (or in our life) with specified parameters. When we change parameters, we make a new experiment. Similar experiments combine into a group, that is defined by some aspect we examine with our experiments with different parameters.

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

You can view the information about your proj, groups and exps:
```python
# Detailed info:
xman.info()  # for the entire project
# or xman.group(1).info()  # for a particular group
# or xman.exp(1, 1).info()  # for a particular exp

Output:
    Proj [EMPTY] My Proj Name - My proj descr    
    Resolution: -= auto status =-    
    
    Group 1 [EMPTY] My Group 1 - My group 1 descr    
        Resolution: -= auto status =-    
        
        Exp 1 [EMPTY] My Exp 1 - My exp 1 descr    
            Resolution: -= auto status =-

# Brief info:
xman.exp(1, 1)
# or xman.group
# or xman.proj

Output:
    Exp 1 [EMPTY] My Exp 1 - My exp 1 descr


Brief info contains: struct_type struct_num [STATUS] Struct_name - Struct_descr
```

As you probably already noticed:
1. `xman` API supports different styles:
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
2. Groups and exps can be reached by their nums and names (so, group names should be unique in the project, and exps names should be unique in a one particular group):
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

TODO


## Performing Experiments

TODO

### Manual Experiments

TODO

### Pipeline Experiments

TODO

### Running in parallel under different Google Colab accounts

TODO


## Conclusion

TODO: It's not a secret, that takes a lot of time and many attempts to find best parameters, so gives competitive advantage


<details><summary>Click to expand/collapse</summary>

   This is the content that will be hidden initially and can be toggled by clicking the summary above.
</details>