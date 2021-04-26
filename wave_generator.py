import ui
from objc_class import *
import pdbg

class WaveGenerator:
  def __init__(self):
    self.audioEngine = AVAudioEngine.new()
    self.sourceNode = AVAudioSourceNode.alloc()
    



class View(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.wave_generator = WaveGenerator()


if __name__ == '__main__':
  view = View()
  view.present('fullscreen')
