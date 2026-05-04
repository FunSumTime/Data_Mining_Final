def  make_shingles(text,k):
    list_words = text.split(" ")
   
    my_set = set()
    n  = len(list_words)
    if k >= n:
        print("k is  too large to make multiple")
        my_set.add(text)
        return my_set
    
    start_index =  0
    window_index =  k
    
    # do slidingn  window  to  get  the shingles
    while window_index <= n:
        # join gllues slce of  a list  to gether with spaces gettingn rid  of  having  to do a loop
        string_to_add =  " ".join(list_words[start_index:window_index])

        my_set.add(string_to_add)

    # move window  forward  one
        start_index += 1
        window_index += 1
    return  my_set

    
print(make_shingles("Security teams need to prioritize", 3))

# now i have  my shingles now need  to hash them  and get  there  simularity

import  random

# how many times  we  will runn it  to  get  simulatrity the more  = better estimate
num_hashes = 100

# use  seeded ranndom to get test  for debug
random.seed(42)

hash_salts =  [str(random.random()) for _ in  range(num_hashes)]

def  get_minhash_signature(shingle_set):
    # compress  a giant set of  text shingles  into tiny arrya of  100 numbers
    signature = []

    # run through 100 hash  functions
    for salt in hash_salts:
        min_hash =  float('inf') # start with innfity to get  min

        # hahs every shingle in  the document  using  salt
        for  shingle in shingle_set:
            # combine with salt  to  get random
            shingle_hash =  hash(shingle +  salt)

            if shingle_hash  < min_hash:
                min_hash = shingle_hash
        
        # add  the minn hash to  signnature  array
        signature.append(min_hash)
    # now have  100 or  how many runs we do of shingles  that are the min hash for our simularity
    return signature

# getting  the shingles to  pass  in
doc_A_Shingles = make_shingles()
doc_B_Shingles = make_shingles()

# compare them  
sig_A =  get_minhash_signature(doc_A_Shingles)
sig_B = get_minhash_signature(doc_B_Shingles)

matches  = 0
# get  the probality
for i in range(num_hashes):
    if sig_A[i]  ==  sig_B[i]:
        matches  += 1

estimated_similarity = matches/ num_hashes

print(f"Total matches: {matches}")
print(f"Estimated Jaccard Similarity: {estimated_similarity * 100 }%")


from collections import defaultdict

def perform_lsh(signatures_dict, num_bands=20, rows_per_band=5):
    """
    signatures_dict: A dictionary where the key is the cve_id and the value is the 100-number array.
    """
    # This will hold our final pairs of documents that need to be compared
    candidate_pairs = set()
    
    # We loop through one band at a time (e.g., Band 0, Band 1, Band 2...)
    for band_idx in range(num_bands):
        # Create fresh buckets for this specific band
        buckets = defaultdict(list)
        
        # Calculate where this band starts and stops in the 100-number array
        start_row = band_idx * rows_per_band
        end_row = start_row + rows_per_band
        
        # Put every document into a bucket for this band
        for cve_id, signature in signatures_dict.items():
            # Slice out just the 5 numbers for this band
            band_slice = signature[start_row:end_row]
            
            # Convert the list of numbers into a tuple (so it can be a dictionary key)
            bucket_id = tuple(band_slice)
            
            # Drop the document ID into the bucket!
            buckets[bucket_id].append(cve_id)
            
        # After sorting all documents for this band, check the buckets
        for bucket_id, docs_in_bucket in buckets.items():
            # If there's more than one document in this bucket, they are a candidate pair!
            if len(docs_in_bucket) > 1:
                # Add them to our final list (using a loop handles buckets with 3+ docs)
                for i in range(len(docs_in_bucket)):
                    for j in range(i + 1, len(docs_in_bucket)):
                        # Sort them so (A, B) is the same as (B, A)
                        pair = tuple(sorted([docs_in_bucket[i], docs_in_bucket[j]]))
                        candidate_pairs.add(pair)
                        
    return candidate_pairs

