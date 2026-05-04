import pandas as pd
import random
from collections import defaultdict

class MinHashLSH:
    def __init__(self, num_hashes=100, num_bands=20, rows_per_band=5):
        self.num_hashes = num_hashes
        self.num_bands = num_bands
        self.rows_per_band = rows_per_band
        random.seed(42)
        self.salts = [str(random.random()) for _ in range(num_hashes)]

    def get_shingles(self, text, k=3):
        words = str(text).split()
        if len(words) <= k: return {text}
        return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}

    def get_signature(self, shingle_set):
        signature = []
        for salt in self.salts:
            min_hash = float('inf')
            for shingle in shingle_set:
                min_hash = min(min_hash, hash(shingle + salt))
            signature.append(min_hash)
        return signature

    def find_similar_pairs(self, df):
        print("1. Generating Signatures...")
        signatures = {}
        for index, row in df.iterrows():
            shingles = self.get_shingles(row['plain_english_summary'])
            signatures[row['cve_id']] = self.get_signature(shingles)

        print("2. Running LSH Bucketing...")
        candidate_pairs = set()
        for band_idx in range(self.num_bands):
            buckets = defaultdict(list)
            start = band_idx * self.rows_per_band
            end = start + self.rows_per_band
            
            for cve_id, sig in signatures.items():
                bucket_id = tuple(sig[start:end])
                buckets[bucket_id].append(cve_id)
                
            for docs in buckets.values():
                if len(docs) > 1:
                    for i in range(len(docs)):
                        for j in range(i + 1, len(docs)):
                            candidate_pairs.add(tuple(sorted([docs[i], docs[j]])))
                            
        print(f"✅ Found {len(candidate_pairs)} highly similar CVE pairs!")
        return candidate_pairs

# How to use it:
# df = pd.read_csv("my_ckan_data.csv")
# lsh = MinHashLSH()
# suspicious_duplicates = lsh.find_similar_pairs(df)