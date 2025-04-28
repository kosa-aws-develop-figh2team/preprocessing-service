
from utils.converter import convert_to_text, handle_txt
from utils.chunker import split_into_chunks
from utils.embed import save_chunk_vectordb

local_tmp_path = ".test/tmp/sample.pdf"
txt_text = convert_to_text(local_tmp_path)
clean_txt = handle_txt(txt_text)
chunk_list = split_into_chunks(clean_txt)
save_chunk_vectordb(chunk_list, "TEST03")
print('!')