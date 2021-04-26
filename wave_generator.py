from objc_util import ObjCClass
import ui

import pdbg



AVAudioEngine = ObjCClass('AVAudioEngine')
AVAudioSourceNode = ObjCClass('AVAudioSourceNode')

#AVAudioMixerNode = ObjCClass('AVAudioMixerNode')




class Synthesizer:
  def __init__(self):
    self.time: float = 0.0
    self.frequencyRamp: float = 0.0
    self.currentFrequency: float = 20.0
    
  def setup(self):
    
    



class View(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.synthesizer = Synthesizer()


if __name__ == '__main__':
  view = View()
  view.present('fullscreen')
