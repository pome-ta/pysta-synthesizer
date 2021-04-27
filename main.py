from ctypes import c_int32, c_uint32, c_void_p, Structure
from objc_util import ObjCClass
import ui

import pdbg

AVAudioEngine = ObjCClass('AVAudioEngine')
AVAudioSourceNode = ObjCClass('AVAudioSourceNode')


# memo: [Core Audio その１ AudioBufferとAudioBufferList](https://objective-audio.jp/2008/03/22/core-audio-audiobufferaudiobuf/)
class AudioBuffer(Structure):
  _fields_ = [('mNumberChannels', c_uint32), ('mDataByteSize', c_uint32),
              ('mData', c_void_p)]

class AudioBufferList(Structure):
  # xxx: AudioBuffer * 2 ?
  _fields_ = [('mNumberBuffers', c_uint32), ('mBuffers', AudioBuffer * 2)]


class Synth:
  def __init__(self):
    self.audioEngine = AVAudioEngine.new()
    
  def setup(self):
    self.mainMixer = self.audioEngine.mainMixerNode()
    self.outputNode = self.audioEngine.outputNode()
    
    format = self.outputNode.inputFormatForBus_(0)
    pdbg.all(self.mainMixer)


synth = Synth()
synth.setup()
