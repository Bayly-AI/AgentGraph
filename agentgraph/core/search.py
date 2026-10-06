"""Okapi BM25 Lexical search engine for fast AgentGraph retrieval."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional

from agentgraph.core.models import AgentGraphNode, SearchResult


class BM25SearchEngine:
    """Okapi BM25 ranking algorithm implementation for AgentGraph nodes."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._doc_lengths: Dict[str, int] = {}
        self._term_freqs: Dict[str, Counter[str]] = {}
        self._doc_freqs: Counter[str] = Counter()
        self._avg_doc_len: float = 0.0
        self._nodes: Dict[str, AgentGraphNode] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize string into lowercase alphanumeric words."""
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text)]

    def index_node(self, node: AgentGraphNode) -> None:
        """Add or update node in BM25 index."""
        self._nodes[node.id] = node
        text_corpus = f"{node.label} {node.plane} {node.type} {node.content} " + " ".join(
            str(v) for v in node.properties.values()
        )
        tokens = self._tokenize(text_corpus)
        self._doc_lengths[node.id] = len(tokens)
        tf = Counter(tokens)
        self._term_freqs[node.id] = tf

        for term in tf:
            self._doc_freqs[term] += 1

        total_tokens = sum(self._doc_lengths.values())
        self._avg_doc_len = total_tokens / len(self._doc_lengths) if self._doc_lengths else 0.0

    def clear(self) -> None:
        """Clear search index."""
        self._doc_lengths.clear()
        self._term_freqs.clear()
        self._doc_freqs.clear()
        self._avg_doc_len = 0.0
        self._nodes.clear()

    def query(
        self,
        query_str: str,
        target_plane: Optional[str] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Query index and return ranked SearchResult items."""
        tokens = self._tokenize(query_str)
        if not tokens or not self._doc_lengths:
            return []

        scores: Dict[str, float] = defaultdict(float)
        N = len(self._doc_lengths)

        for term in tokens:
            df = self._doc_freqs.get(term, 0)
            if df == 0:
                continue

            # IDF calculation with smoothing
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)

            for doc_id, tf_map in self._term_freqs.items():
                node = self._nodes.get(doc_id)
                if not node or (target_plane and node.plane != target_plane):
                    continue

                freq = tf_map.get(term, 0)
                if freq == 0:
                    continue

                doc_len = self._doc_lengths[doc_id]
                denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / self._avg_doc_len))
                num = freq * (self.k1 + 1.0)
                scores[doc_id] += idf * (num / denom)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        results = []
        for did, score in ranked:
            node = self._nodes[did]
            results.append(SearchResult(
                node=node,
                score=round(score, 4),
                matched_plane=node.plane
            ))
        return results
