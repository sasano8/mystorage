# mystoreにまだ未移行なコードあるかも！？？


# import os

# from myhdf5.directory import InfinityTempNames


# def test_infinity_temp_names():
#     with InfinityTempNames() as tmpnames:
#         assert isinstance(tmpnames.dirname, str)
#         assert isinstance(tmpnames.next(), str)
#         assert isinstance(tmpnames.next(), str)

#         for i, filname in enumerate(tmpnames):
#             assert isinstance(filname, str)
#             if i > 10:
#                 break

#         for filename in tmpnames.names:
#             assert isinstance(filename, str)


# def test_infinity_tempfiles_if_file_not_close():
#     with InfinityTempNames() as tmpnames:
#         dirname = tmpnames.dirname
#         f1 = tmpnames.next()
#         f = open(f1, "w")
#         f.write("aaa")
#         f.flush()

#     assert not os.path.exists(dirname)
