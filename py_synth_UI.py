import ui




class MainView(ui.View):
  def __init__(self, *args, **kwargs):
    ui.View.__init__(self, *args, **kwargs)
    self.bg_color = 1
    self.tone_triangle = ui.SegmentedControl()
    self.tone_triangle.segments = ['sine', 'aaa', 'bbb', 'ppp']
    self.tone_triangle.flex = 'W'
    self.tone_triangle.selected_index = 0
    self.add_subview(self.tone_triangle)
    
  def layout(self):
    pass
    


if __name__ == '__main__':
  view = MainView()
  view.present('fullscreen')
  #view.present()

