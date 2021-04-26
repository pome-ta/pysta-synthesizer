from ctypes import Structure, c_void_p, c_int32, c_uint32

OSStatus = c_int32
err_ptr = c_void_p()

# memo: [Core Audio その１ AudioBufferとAudioBufferList](https://objective-audio.jp/2008/03/22/core-audio-audiobufferaudiobuf/)
class AudioBuffer(Structure):
  _fields_ = [('mNumberChannels', c_uint32),
              ('mDataByteSize', c_uint32),
              ('mData', c_void_p)]

class AudioBufferList(Structure):
  # xxx: AudioBuffer * 2 ?
  _fields_ = [('mNumberBuffers', c_uint32),
              ('mBuffers', AudioBuffer * 2)]

