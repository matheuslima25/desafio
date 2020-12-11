import os
from typing import Any, List, Union


# 12FACTOR ADOPTION


def get_env(name: str, *, default: Any = None, aliases: Union[List[str], str] = None) -> str:
    """
    this little helper is meant to ease the transition to sane
    configurations and introduce new, sane naming for the ENV variables

    aliases work in the way of definition - rightmost wins if more then one are present,
    primal name always wins if present

    :param name: primal name of the variable
    :param default: default returned if variable is not defined
    :param aliases: set of variable aliases which are visited (for b/c during renaming)
    :return: str
    """
    _traversed = []
    if isinstance(aliases, str):
        _traversed.append(aliases)
    elif isinstance(aliases, list):
        _traversed.extend(aliases)
    elif aliases is None:
        pass
    else:
        raise ValueError('aliases should be either string or list of strings')

    # extend aliases with primary name
    _traversed.append(name)
    v = None
    # iterate over aliases, get values, `name` always wins for being the last
    for n in _traversed:
        v = os.getenv(n, v)  # it writes previous if alias is undefined
    if v is None or v == '':
        return default
    return v


__true_values = (True, 1, '1', 'True', 'true')


def get_env_flag(name: str, *, default: bool = False, aliases: Union[List[str], str] = None) -> bool:
    """
    this little helper is meant to ease the transition to sane
    configurations and introduce new, sane naming for the ENV variables

    aliases work in the way of definition - rightmost wins if more then one are present,
    primal name always wins if present

    this variation works best to evaluate the BOOL value out of given environment variables

    :param name: primal name of the variable
    :param default: default returned if variable is not defined
    :param aliases: set of variable aliases which are visited (for b/c during renaming)
    :return: bool
    """
    v = get_env(name, default=default, aliases=aliases)

    if v in __true_values:
        return True
    return False
