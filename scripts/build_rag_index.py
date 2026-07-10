from __future__ import annotations

import argparse
from pathlib import Path

import faiss
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/rag/codesearchnet_python")
    parser.add_argument("--samples", type=int, default=100000)
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    dataset = load_dataset("code-search-net/code_search_net", "python", split="train", streaming=True)
    documents = []
    for row in tqdm(dataset, total=args.samples, desc="CodeSearchNet"):
        code = str(row.get("whole_func_string") or row.get("func_code_string") or "").strip()
        if code:
            documents.append(code[:8000])
        if len(documents) >= args.samples:
            break
    encoder = SentenceTransformer(args.embedding_model)
    vectors = encoder.encode(
        documents,
        batch_size=args.batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output / "index.faiss"))
    np.save(output / "documents.npy", np.array(documents, dtype=object), allow_pickle=True)
    (output / "embedding_model.txt").write_text(args.embedding_model, encoding="utf-8")
    print(f"documents={len(documents)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
