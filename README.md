
**Warning**: This repository is a completely crazy pet project experiment that is not even expected to become product.
It is published openly just in case something will be useful to somebody as I rely a lot on the open-source tools so
it is logical to keep my integrated stack open.

# Home AI toolkit

A collection of the self-made need-based tools for home AI/ML hub.
The primary case is a knowledge base / LLM chat that covers various information that is used around home / family.

## The basic idea of the stack

This AI hub is expected to be able to scout over the various sources
of information in the house, automatically process new data elements
and integrate it somehow into the home central knowledge base.
The preparation steps may vary by data source, data may be enriched
in the process.

Home knowledge base should be fed with the information extracted
from the data sources, appropriate tokenisation and embedding models
should be used to build appropriate index with the idea of semantic
search.

The human interface to the system would be a home-deployed LLM
that should be able to use home knowledge base and its abilities
to support semantic search to integrate home-hosted data into chats.
Also agents are considered to collect external data / perform
realtime searches as needed.

Home AI hub is expected to integrate in future with the in-house
domotica (Home Assistant is envisioned as a primary citizen).

## First target

The first target is a barch transcribation support over the home
storage (NAS). Whisper (https://github.com/openai/whisper) will be
used as a tool to do the actual job.
