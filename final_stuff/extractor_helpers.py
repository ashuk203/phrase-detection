import spacy
spacy.require_gpu()
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.tokenizer import Tokenizer
import re

from whoosh.qparser import QueryParser
import whoosh.index as index
from whoosh.index import open_dir
from whoosh.query import Every

from collections import defaultdict

import itertools
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

nlp = spacy.load('en_core_web_sm')

# print(type(tuple([r"'s\b", r"(?<!\d)\.(?!\d)"])))
# print(type(nlp.Defaults.prefixes))

# print(nlp.Defaults.prefixes)
infixes = [r"'s\b", r"(?<!\d)\.(?!\d)"] +  nlp.Defaults.prefixes
infix_re = spacy.util.compile_infix_regex(infixes)

def custom_tokenizer(nlp):
    return Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

nlp.tokenizer = custom_tokenizer(nlp)

def extractor(document, *pattern):
    '''
    @param str file: text file for tuple extraction
    @param list pattern: extraction pattern
    A phrase extractor based on spacy
    '''
    phrases = []
    matcher = Matcher(nlp.vocab)
    matcher.add("pattern extraction", pattern)
    doc = nlp(document)
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        phrases.append(span.text)
    return phrases

def partition(file, size = 1000000):
    '''
    partition the input file into block with maximum size of 1000000, since SpaCy v2.x parser may have issues allocating memory with size larger than 1000000
    '''
    while True:
        data = file.read(size)
        if not data:
            break
        yield data


def getPhrases(file, context_pattern):
    new_phrases = set()
    with open(file, 'r') as f:
        matcher = Matcher(nlp.vocab)
        file_chunk = partition(f)
        for t in file_chunk:
            doc = nlp(t)
            for cp in context_pattern:
                pos_indices = [i for i in range(len(cp)) if 'POS' in cp[i]]
                if len(pos_indices) == 0:
                    continue
                    
                start_offset = min(pos_indices)
                end_offset = max(pos_indices) + 1
                matcher.add("extraction", [cp])
                matches = matcher(doc)
                for match_id, start, end in matches:
                    span = doc[start+start_offset:start+end_offset].text
                    if span not in new_phrases:
                        new_phrases.add(span)
                matcher.remove("extraction")
    return new_phrases
