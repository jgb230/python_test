#!/usr/bin/env python
# coding=utf-8

import ctypes

ctypes.CDLL("/home/jgb/mtsProject/ext/mts_outer/glog/lib/libgflags.so.2", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/mtsProject/ext/mts_outer/glog/lib/libglog.so.0", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/mtsProject/ext/mts_outer/boost_1_64_0/stage/lib/libboost_system.so.1.64.0", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/mtsProject/ext/mts_outer/tinyxml/lib/libtinyxml2.so.4", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/mtsProject/ext/mts_outer/zmq/lib/libzmq.so.5", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/tes/lib/libtes_db.so", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/tes/lib/libemotionAPI.so", mode=ctypes.RTLD_GLOBAL)
ctypes.CDLL("/home/jgb/mtsProject/build/lib/services/libemotionCommon.so", mode=ctypes.RTLD_GLOBAL)

lib = ctypes.CDLL("/home/jgb/tes/lib/services/libemotion.so")

lib.updateEmotionToRedis(0, "1803131024017cc6f33d1d79RI001618", 220)
#lib.addDesire("1803131024017cc6f33d1d79RI001612", "13", "106")
#lib.removeDesire("1803131024017cc6f33d1d79RI001612", "13", "106")
