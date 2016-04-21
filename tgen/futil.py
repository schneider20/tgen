#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Various utility functions.
"""

from __future__ import unicode_literals
import cPickle as pickle
import codecs
import gzip
from io import IOBase
from codecs import StreamReader, StreamWriter

from alex.components.slu.da import DialogueAct
from tree import TreeData


def file_stream(filename, mode='r', encoding='UTF-8'):
    """\
    Given a file stream or a file name, return the corresponding stream,
    handling GZip. Depending on mode, open an input or output stream.
    (A copy from pytreex.core.util to remove dependency)
    """
    # open file
    if isinstance(filename, (file, IOBase, StreamReader, StreamWriter)):
        fh = filename
    elif filename.endswith('.gz'):
        fh = gzip.open(filename, mode)
    else:
        fh = open(filename, mode)
    # support encodings
    if encoding is not None:
        if mode.startswith('r'):
            fh = codecs.getreader(encoding)(fh)
        else:
            fh = codecs.getwriter(encoding)(fh)
    return fh


def read_das(da_file):
    """Read dialogue acts from a file, one-per-line."""
    das = []
    with file_stream(da_file) as fh:
        for line in fh:
            da = DialogueAct()
            da.parse(line)
            das.append(da)
    return das


def read_ttrees(ttree_file):
    """Read t-trees from a YAML/Pickle file."""
    from pytreex.block.read.yaml import YAML as YAMLReader
    if 'pickle' in ttree_file:
        # if pickled, read just the pickle
        fh = file_stream(ttree_file, mode='rb', encoding=None)
        unpickler = pickle.Unpickler(fh)
        ttrees = unpickler.load()
        fh.close()
    else:
        # if not pickled, read YAML and save a pickle nearby
        yaml_reader = YAMLReader(scenario=None, args={})
        ttrees = yaml_reader.process_document(ttree_file)
        pickle_file = ttree_file.replace('yaml', 'pickle')
        fh = file_stream(pickle_file, mode='wb', encoding=None)
        pickle.Pickler(fh, pickle.HIGHEST_PROTOCOL).dump(ttrees)
        fh.close()
    return ttrees


def write_ttrees(ttree_doc, fname):
    """Write a t-tree Document object to a YAML file."""
    from pytreex.block.write.yaml import YAML as YAMLWriter
    writer = YAMLWriter(scenario=None, args={'to': fname})
    writer.process_document(ttree_doc)


def read_tokens(tok_file):
    """Read sentences (one per line) from a file and return them as a list of tokens
    (forms with undefined POS tags)."""
    # TODO apply Morphodita here
    tokens = []
    with file_stream(tok_file) as fh:
        for line in fh:
            tokens.push([(form, None) for form in line.strip().split(' ')])

def write_tokens(doc, language, selector, tok_file):
    # TODO TODO TODO
    raise NotImplementedError()

def chunk_list(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def ttrees_from_doc(ttree_doc, language, selector):
    """Given a Treex document full of t-trees, return just the array of t-trees."""
    return map(lambda bundle: bundle.get_zone(language, selector).ttree,
               ttree_doc.bundles)


def trees_from_doc(ttree_doc, language, selector):
    """Given a Treex document full of t-trees, return TreeData objects for each of them."""
    return map(lambda bundle: TreeData.from_ttree(bundle.get_zone(language, selector).ttree),
               ttree_doc.bundles)


def sentences_from_doc(ttree_doc, language, selector):
    """Given a Treex document, return a list of sentences in the given language and selector."""
    return map(lambda bundle: bundle.get_zone(language, selector).sentence, ttree_doc.bundles)


def tokens_from_doc(ttree_doc, language, selector):
    """Given a Treex document, return a list of lists of tokens (word forms + tags) in the given
    language and selector."""
    atrees = map(lambda bundle: bundle.get_zone(language, selector).atree, ttree_doc.bundles)
    sents = []
    for atree in atrees:
        anodes = atree.get_descendants(ordered=True)
        sent = []
        for anode in anodes:
            form, tag = anode.form, anode.tag
            if form == 'X':
                tnodes = anode.get_referencing_nodes('a/lex.rf')
                if tnodes:
                    form = tnodes[0].t_lemma
            sent.append((form, tag))
        sents.append(sent)
    return sents


def add_bundle_text(bundle, language, selector, text):
    """Given a document bundle, add sentence text to the given language and selector."""
    zone = bundle.get_or_create_zone(language, selector)
    zone.sentence = (zone.sentence + ' ' if zone.sentence is not None else '') + text
