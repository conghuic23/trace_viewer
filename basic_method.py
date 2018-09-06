import cairo

TEXT_SIZE = 120
TimeLineSolidColor = [0.75, 0.75, 0.75]
TimeLineDottedColor = [0.88, 0.88, 0.88]
ZoneColor = [0.8, 0.90, 1]
ZoneColorBLUE = [0, 0.4, 0.8]
ZoneColorBLUE2 = [0.32, 0.27, 0.79]
TexTColor = [0, 0, 0]   # all block
ZoneLineColor = [0.376, 0.376, 0.376]

class Paint():
    def __init__(self, ctx):
        self.ctx = ctx
        self.u2p = 0
        self.wi = 0
        self.hi = 0

    def init(self, wi, hi, u2p):
        self.wi = wi
        self.hi = hi
        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.rectangle(0, 0, wi, hi)
        self.ctx.fill()
        self.u2p= u2p

    def paint_matrix(self, x, y, dx, dy):
        self.ctx.set_source_rgb(*ZoneColor)
        self.ctx.rectangle(x, y, dx, dy)
        self.ctx.fill()
        self.ctx.set_source_rgb(*ZoneLineColor)
        self.ctx.set_line_width(10.0)
        self.ctx.rectangle(x, y, dx, dy)
        self.ctx.stroke()

    def paint_dotted_line(self, sx, sy, ex, ey):
        self.ctx.set_source_rgb(*TimeLineDottedColor)
        self.ctx.set_line_width(10.0)
        self.ctx.move_to(sx, sy)
        self.ctx.line_to(ex, ey)
        self.ctx.stroke()

    def paint_line(self, sx, sy, ex, ey):
        self.ctx.set_source_rgb(*TimeLineSolidColor)
        self.ctx.set_line_width(10.0)
        self.ctx.move_to(sx, sy)
        self.ctx.line_to(ex, ey)
        self.ctx.stroke()

    def paint_matrix_with_colume(self,x,y,dx,dy):
        self.ctx.set_source_rgb(*TimeLineSolidColor)
        self.ctx.set_line_width(15.0)
        self.ctx.rectangle(x, y, dx, dy)
        self.ctx.stroke()
        for i in range(1, int(dx/self.u2p)+1):
            x_l = i*self.u2p + x
            y_l = y
            xe_l = x_l
            ye_l= y + dy
            if i%5 == 0:
                self.paint_line(x_l,y_l,xe_l,ye_l)
            else:
                self.paint_dotted_line(x_l,y_l,xe_l,ye_l)

    def paint_text(self, x, y, text):
        self.paint_text_size(x, y, text, TEXT_SIZE)

    def paint_text_size(self, x, y, text, size):
        self.ctx.set_font_size(size)
        self.ctx.select_font_face('')
        self.ctx.set_source_rgb(*TexTColor)
        self.ctx.move_to(x, y)
        self.ctx.show_text(text)

    def paint_title(self, x, y, text, size):
        self.ctx.set_font_size(size)
        self.ctx.select_font_face('',
                                  cairo.FontSlant.NORMAL,
                                  cairo.FontWeight.BOLD)
        self.ctx.set_source_rgb(*TexTColor)
        self.ctx.move_to(x, y)
        self.ctx.show_text(text)
