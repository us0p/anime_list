from os.path import getsize

class DisplayService():
    def read_image_from_url(self):
        file_path = "/home/us0p/Pictures/Wallpappers/lost_kin.png"
        file_size = getsize(file_path)
        with open(file_path, mode="rb") as i:
            # a PNG file has:
            # an 8 byte length signature.
            # a series of chunks with information about the file.
            # the first 4 bytes of the chunk represent the length of its
            # data.
            # the next 4 bytes are the chunk type/name.
            # next is the chunk data which have the same number of bytes
            # as defined in length.
            # finaly we have the 4 bytes cyclic redundancy code/checksum 
            # CRC, it's the network-byte-order computed over the data and
            # type/name chunks.

            # chunk type/name are given four-letter case sensitive ASCI
            # type/name; the case of the first litter indicates whether
            # the chunk is critical or not. If the first letter is
            # uppercase the chunk is critical else it is ancillary.

            # ancillary chunks can be ignored.

            # the critical chunks are:
            # the header chunk.
            # the pallete chunk deppending over the color type present in
            # the header.
            # the image data chunk.
            # the end of image chunk, its data data field is always empty.

            # the header chunk has always 13 bytes length and contain in
            # this order:
            # 1. width (4 bytes)
            # 2. height (4 bytes)
            # 3. bit depth (1 byte, values 1, 2, 4, 8, or 16)
            # 4. color type (1 byte, values 0, 2, 3, 4, or 6)
            # 5. compression method (1 byte, value 0)
            # 6. filter method (1 byte, value 0)
            # 7. interlace method (1 byte, values 0 "no interlace" or 1 
            #    "Adam7 interlace")

            image_signature = i.read(8)
            print("image signature:", image_signature)
            print("-" * 75)
            chunk_data_length = int.from_bytes(i.read(4), "big")
            chunk_name = str(i.read(4), encoding="utf-8")
            image_width = int.from_bytes(i.read(4), "big")
            image_height = int.from_bytes(i.read(4), "big")
            image_bit_depth = int.from_bytes(i.read(1), "big")
            image_color_type = int.from_bytes(i.read(1), "big")
            image_compression_method = int.from_bytes(i.read(1), "big")
            image_filter_method = int.from_bytes(i.read(1), "big")
            image_interlace_method = int.from_bytes(i.read(1), "big")
            image_header_crc = i.read(4)
            print("chunk name:", chunk_name)
            print(f"{chunk_name} data length:", chunk_data_length, "bytes")
            print("width:", image_width)
            print("height:", image_height)
            print("bit depth:", image_bit_depth)
            print("color type:", image_color_type)
            print("compression method:", image_compression_method)
            print("filter method:", image_filter_method)
            print("interlace method:", image_interlace_method)
            print("crc:", image_header_crc)
            print("-" * 75)
            while i.tell() < file_size:
                repetitive_chunk_length = int.from_bytes(i.read(4), "big")
                repetitive_chunk_name_ = str(i.read(4), encoding="utf-8")
                print("chunk name:", repetitive_chunk_name_)
                print(
                    f"{repetitive_chunk_name_} data length:",
                    repetitive_chunk_length,
                    "bytes"
                )
                repetitive_chunk_data = i.read(repetitive_chunk_length)
                repetitive_chunk_crc = i.read(4)
                print("-" * 75)
        print("file_size:", file_size)
