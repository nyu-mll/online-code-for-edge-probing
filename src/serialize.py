#!/bin/bash

# Serialization and deserialization helpers.
# Write arbitrary pickle-able Python objects to a record file, with one object 
# per line as a base64-encoded pickle.

import _pickle as pkl
import base64

def _serialize(examples, fd, flush_every):
    for i, example in enumerate(examples):
        blob = pkl.dumps(example)
        encoded = base64.b64encode(blob)
        fd.write(encoded)
        fd.write(b"\n")
        if (i + 1) % flush_every == 0 and hasattr(fd, 'flush'):
            fd.flush()

def write_records(examples, filename, flush_every=10000):
	"""Streaming read records from file.

	Args:
      examples: iterable(object), iterable of examples to write
      filename: path to file to write
      flush_every: (int), flush to disk after this many examples consumed
    """
    with open(filename, 'wb') as fd:
        _serialize(examples, fd, flush_every)

def _deserialize(fd):
    for line in fd:
        blob = base64.b64decode(line)
        example = pkl.loads(blob)
        yield example

class RepeatableIterator(object):
    """Repeatable iterator class."""
    
    def __init__(self, iter_fn):
        """Create a repeatable iterator.
        
        Args:
          iter_fn: callable with no arguments, creates an iterator
        """
        self._iter_fn = iter_fn
        self._counter = 0
        
    def get_counter(self):
        return self._counter
        
    def __iter__(self):
        self._counter += 1
        return self._iter_fn().__iter__()


def read_records(filename, repeatable=False):
	"""Streaming read records from file.

	Args:
      filename: path to file of b64-encoded pickles, one per line
      repeatable: if true, returns a RepeatableIterator that can read the file 
        multiple times.

	Returns:
      iterable, possible repeatable, yielding deserialized Python objects
    """
	with open(filename, 'rb') as fd:
        iter_fn = lambda: _deserialize(fd)
        return RepeatableIterator(iter_fn) if repeatable else iter_fn()

