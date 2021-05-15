from math import sin, pi
from random import uniform, choice
import ctypes
from io import BytesIO

import numpy as np
import matplotlib.image

from objc_util import ObjCClass, ObjCBlock, ObjCInstance
import ui

OSStatus = ctypes.c_int32
err_ptr = ctypes.c_void_p()


class AudioBuffer(ctypes.Structure):
  _fields_ = [('mNumberChannels', ctypes.c_uint32),
              ('mDataByteSize', ctypes.c_uint32), ('mData', ctypes.c_void_p)]


class AudioBufferList(ctypes.Structure):
  _fields_ = [('mNumberBuffers', ctypes.c_uint32), ('mBuffers',
                                                    AudioBuffer * 2)]


AVAudioEngine = ObjCClass('AVAudioEngine')
AVAudioFormat = ObjCClass('AVAudioFormat')
AVAudioSourceNode = ObjCClass('AVAudioSourceNode')
AVAudioUnitDelay = ObjCClass('AVAudioUnitDelay')


class Oscillator:
  def __init__(self):
    self.amplitude = 1
    self.frequency = 440
    self.wave_box = [
      self.mixwave, self.sine, self.triangle, self.sawtooth, self.square,
      self.whiteNoise
    ]
    self.fre_slider = ui.Slider()
    self.fre_slider.flex = 'W'
    self.fre_slider.value = 0.5
    self.fre_slider.action = self.move_frequency

  def sine(self, time, *args):
    frequency = args[0] if args else self.frequency
    wave = self.amplitude * sin(2.0 * pi * frequency * time)
    return wave

  def triangle(self, time, *args):
    frequency = args[0] if args else self.frequency
    period = 1.0 / frequency
    currentTime = time % period
    value = currentTime / period
    result = 0.0
    if value < 0.25:
      result = value * 4
    elif value < 0.75:
      result = 2.0 - (value * 4.0)
    else:
      result = value * 4 - 4.0
    wave = self.amplitude * result
    return wave

  def tone_triangle(self, time, *args):
    frequency = args[0] if args else self.frequency
    period = 1.0 / frequency
    currentTime = time % period
    value = currentTime / period
    result = 0.0
    if value < 0.0:
      result = value * 4

    elif value > 0.8:
      #result = 0
      result = value * 4 - 4.0
      #pass
    else:
      result = 0
    wave = self.amplitude * result
    return wave

  def sawtooth(self, time, *args):
    frequency = args[0] if args else self.frequency
    period = 1.0 / frequency
    currentTime = time % period
    wave = self.amplitude * ((currentTime / period) * 2 - 1.0)
    return wave

  def square(self, time, *args):
    frequency = args[0] if args else self.frequency
    period = 1.0 / frequency
    currentTime = time % period
    if (currentTime / period) < 0.5:
      wave = self.amplitude
      return wave
    else:
      wave = -1.0 * self.amplitude
      return wave

  def whiteNoise(self, _):
    return uniform(-1.0, 1.0)

  def mixwave(self, time):
    #wave = self.sine(time) * self.sine(time, .8)
    #wave = self.whiteNoise(time) * self.tone_triangle(time, 2)
    wave01 = self.square(time) * self.tone_triangle(time, 3)
    wave02 = self.whiteNoise(time) * self.tone_triangle(time, 2)
    wave = wave01 + wave02
    return wave

  def move_frequency(self, sender):
    val = sender.value * 880
    self.frequency = val


class Synth:
  def __init__(self, parent):
    self.parent = parent
    self.timex = 0
    self.sampleRate = 0
    self.deltaTime = 0

    self.render_block = ObjCBlock(
      self.SourceNodeRender,
      restype=OSStatus,
      argtypes=[
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(AudioBufferList)
      ])
    self.tap_block = ObjCBlock(
      self.AudioNodeTap,
      restype=None,
      argtypes=[ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p])
    self.set_up()

  def set_up(self):
    audioEngine = AVAudioEngine.new()
    sourceNode = AVAudioSourceNode.alloc()
    mainMixer = audioEngine.mainMixerNode()
    outputNode = audioEngine.outputNode()

    delay = AVAudioUnitDelay.new()
    delay.delayTime = 0.2
    delay.feedback = 25

    _format = outputNode.inputFormatForBus_(0)
    self.sampleRate = _format.sampleRate()
    self.deltaTime = 1 / self.sampleRate
    inputFormat = AVAudioFormat.alloc(
    ).initWithCommonFormat_sampleRate_channels_interleaved_(
      _format.commonFormat(), self.sampleRate, 2, _format.isInterleaved())

    sourceNode.initWithRenderBlock_(self.render_block)
    audioEngine.attachNode_(sourceNode)
    sourceNode.volume = 0.1

    audioEngine.attachNode_(delay)

    audioEngine.connect_to_format_(sourceNode, delay, inputFormat)
    audioEngine.connect_to_format_(delay, mainMixer, inputFormat)
    audioEngine.connect_to_format_(mainMixer, outputNode, inputFormat)  # 44100
    mainMixer.installTapOnBus_bufferSize_format_block_(0, 64 * 64, inputFormat,
                                                       self.tap_block)
    audioEngine.prepare()
    self.audioEngine = audioEngine

  def SourceNodeRender(self, _cmd, isSilence_ptr, timestamp_ptr,
                       frameCount_ptr, outputData_ptr):
    ablPointer = outputData_ptr.contents
    #toneGenerator = choice(self.parent.osc.wave_box)
    for frame in range(frameCount_ptr):
      sampleVal = self.parent.toneGenerator(self.timex)
      #sampleVal = whiteNoise(self.timex)
      self.timex += self.deltaTime

      for bufferr in range(ablPointer.mNumberBuffers):
        buffer = ctypes.cast(ablPointer.mBuffers[bufferr].mData,
                             ctypes.POINTER(
                               ctypes.c_float * frameCount_ptr)).contents
        buffer[frame] = sampleVal
    return 0

  def AudioNodeTap(self, _cmd, buffer, when):
    buf = ObjCInstance(buffer)
    np_buff = np.ctypeslib.as_array(buf.floatChannelData()[0], (256, 16))
    with BytesIO() as bIO:
      #matplotlib.image.imsave(bIO, np_buff + 1, format='png',cmap=(matplotlib.image.cm.get_cmap('gray',256)), vmax=2.0,vmin=0.0)
      matplotlib.image.imsave(bIO, np_buff + 1, format='png')
      img = ui.Image.from_data(bIO.getvalue())
      self.parent.im_view.image = img

  def run(self):
    err = ctypes.byref(err_ptr)
    self.audioEngine.startAndReturnError_(err)

  def stop(self):
    del self.parent.im_view
    self.audioEngine.stop()


class View(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.im_view = ui.ImageView()
    self.im_view.bg_color = 0
    self.im_view.flex = 'WH'
    self.add_subview(self.im_view)
    self.osc = Oscillator()
    self.len_type = len(self.osc.wave_box) - 1

    self.type_osc = ui.Slider()
    self.type_osc.continuous = False
    self.type_osc.value = 0
    self.type_osc.flex = 'W'
    self.type_osc.action = self.change_osc

    self.toneGenerator = self.osc.wave_box[0]

    self.add_subview(self.type_osc)
    self.add_subview(self.osc.fre_slider)

    self.synth = Synth(self)
    self.synth.run()

  def change_osc(self, sender):
    val = int(sender.value * self.len_type)
    self.toneGenerator = self.osc.wave_box[val]
    self.type_osc.value = val / self.len_type

  def layout(self):
    self.osc.fre_slider.y = self.type_osc.height

  def will_close(self):
    self.synth.stop()


if __name__ == '__main__':
  view = View()
  view.present('fullscreen')
  #view.present()

