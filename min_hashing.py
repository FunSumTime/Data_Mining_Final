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