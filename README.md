**Warning**: This repository is a completely crazy pet project experiment that is not even expected to become a product.
It is published openly just in case something will be useful to somebody as I rely a lot on open-source tools, so
it is logical to keep my integrated stack open.

# Home AI Toolkit

A collection of self-made, need-based tools for a home AI/ML hub.
The primary use case is a knowledge base / LLM chat that covers various information used around the home / family.

## Basic Idea of the Stack

This AI hub is expected to scout over various sources
of information in the house, automatically process new data elements,
and integrate them into the home central knowledge base.
The preparation steps may vary by data source, and data may be enriched in the process.

The home knowledge base should be fed with information extracted
from the data sources. Appropriate tokenization and embedding models
should be used to build an index with the idea of semantic search.

The human interface to the system would be a home-deployed LLM
that should be able to use the home knowledge base and its abilities
to support semantic search to integrate home-hosted data into chats.
Additionally, agents are considered to collect external data and perform
real-time searches as needed.

The Home AI hub is expected to integrate in the future with in-house
domotica (Home Assistant is envisioned as a primary citizen).

## First Target

The first target is batch transcription support over the home
storage (NAS). Whisper (https://github.com/openai/whisper) will be
used as a tool to do the actual job.
