import gzip
import pandas as pd
import shutil

# content = b"Lots of content here"
# with gzip.open('file.txt.gz', 'wb') as f:
#     f.write(content)

with gzip.open('test.csv.gz', 'r') as f:
    file_content = f.read()
    print(type(file_content))
with open('file_out.txt', 'wb') as f_out:
    f_out.write(file_content)


# file_content = pd.read_csv('file.txt.gz', delimiter=';', compression='gzip')
# print(file_content)

#
# with open('file.txt', 'wb') as f_in:
#     with gzip.open('file.txt.gz', 'rb') as f_out:
#         shutil.copyfileobj(f_in, f_out)


# s_in = b"Lots of content here"
# s_out = gzip.compress(s_in)
# print(s_out)