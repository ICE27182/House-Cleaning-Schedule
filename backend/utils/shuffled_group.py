from hashlib import md5
from collections.abc import Iterable
from operator import itemgetter

def shuffled_group(set_of_people: Iterable[str], 
                   chore_name: str) -> list[str]:
    hashed_chore_name = int.from_bytes(md5(chore_name.encode()).digest())
    hashes_n_names = [(hashed_chore_name 
                        ^ int.from_bytes(md5(name.encode()).digest()), 
                       name)
                      for name in set_of_people]
    return list(map(itemgetter(1), sorted(hashes_n_names)))
