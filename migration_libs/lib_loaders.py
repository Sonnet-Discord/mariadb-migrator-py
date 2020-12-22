# cache generation tools
# Ultabear 2020

import random, os

def generate_infractionid():
    try:
        num_words = os.path.getsize("wordlist.cache.db")-1
        with open("wordlist.cache.db","rb") as words:
            chunksize = int.from_bytes(words.read(1), "big")
            num_words /= chunksize
            values  = sorted([random.randint(0,(num_words-1)) for i in range(3)])
            output = ""
            for i in values:
                words.seek(i*chunksize+1)
                preout = (words.read(int.from_bytes(words.read(1), "big"))).decode("utf8")
                output += preout[0].upper()+preout[1:]
        return output

    except FileNotFoundError:
        with open("wordlist.txt", "r") as words:
            maxval = 0
            structured_data = []
            for i in words.read().encode("utf8").split(b"\n"):
                structured_data.append(bytes([len(i)])+i)
                if len(i)+1 > maxval:
                    maxval = len(i)+1
        with open("wordlist.cache.db","wb") as structured_data_file:
            structured_data_file.write(bytes([maxval]))
            for i in structured_data:
                structured_data_file.write(i+bytes(maxval-len(i)))

        return generate_infractionid()
