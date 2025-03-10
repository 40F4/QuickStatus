from quickstatus.utils.imports import *
from quickstatus.utils.generic import closeEvent, restoreWindow, colours, widget_refresh
from quickstatus.utils.network_tables import NetworkTables, datatable
from math import degrees

class IntakeWidget(QWidget):
    def __init__(self, wid, conf):
        super(IntakeWidget, self).__init__()
        self.wid = wid
        self.settings = QSettings('QuickStatus', str(self.wid))
        self.config = conf

        restoreWindow(self)

        self.setWindowTitle('QuickStatus (Intake)')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(widget_refresh)
        self.rott = 0
        self.arrow_rot = 0

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing) # VERY IMPORTANT AND MAKES EVERYTHING BEAUTIFUL ✨
        palette = self.palette()
        background_colour = QPalette().color(QPalette().ColorRole.Window)
        foreground_colour = palette.color(palette.ColorRole.Text)
        foreground_colour.setAlpha(255)
        dark = palette.color(palette.ColorRole.Base).lighter(160)
        if sys.platform == 'darwin': palette.setColor(QPalette.ColorRole.Window, dark)
        background_colour = self.palette().color(self.palette().ColorRole.Window)
        self.setPalette(palette)
        colour_chart = [foreground_colour, colours.accent_colour, colours.caution_colour, colours.warning_colour, colours.death_colour]
        size = self.size()
        w = size.width()
        h = size.height()
        cw = w/2 # canvas width
        ch = h/2 # canvas height
        table = datatable['intake']
        if NetworkTables.inst.isConnected() and 'present' in table:
            scale = cw/500
            qp.scale(scale, scale)
            qp.translate(cw/scale,ch/scale)

            # Draw Intake
            pen = QPen(foreground_colour, 8, cap=Qt.PenCapStyle.FlatCap, join=Qt.PenJoinStyle.RoundJoin)
            qp.setPen(pen)
            qp.setBrush(Qt.BrushStyle.NoBrush)

            self.rott = table['encoder_position']*-360
            arc_pos = (-300,-225)
            arc_size = 400
            arc_dist = 50
            arc_angle = 90*16
            arc_cen = (arc_pos[0]+arc_size/2,arc_pos[1]+arc_size/2)
            arc_rot = self.rott
            self.arrow_rot += 0.2
            self.arrow_rot %= 90

            qp.translate(arc_cen[0], arc_cen[1]+125)

            bumper_size = arc_size/4
            qp.drawPolyline([QPointF(-bumper_size,arc_dist), QPointF(-bumper_size,-bumper_size),QPointF(arc_dist,-bumper_size)])
            qp.translate(0, -arc_dist/2-arc_size/2)
            qp.rotate(arc_rot)

            qp.drawArc(QRectF(-arc_size/2, arc_dist/2, arc_size, arc_size), arc_angle, arc_angle)
            qp.drawArc(QRectF(-arc_size/2-arc_dist, 0-arc_dist/2, arc_size+arc_dist*2, arc_size+arc_dist*2), arc_angle, arc_angle)

            qp.drawArc(QRectF(-arc_size/2-arc_dist, arc_size/2-1, arc_dist, arc_dist), arc_angle*2, arc_angle*2)
            qp.drawArc(QRectF(-arc_size/2+arc_size/2-arc_dist/2-1, -arc_dist/2, arc_dist, arc_dist), -arc_angle, arc_angle*2)

            wheel_num = 4
            wheel_size = 1.3
            qp.translate(0, -(-arc_dist/2-arc_size/2))
            
            qp.setBrush(background_colour)
            for i in range(wheel_num):
                rot = -90/wheel_num*(i+1)
                rot = rot+90/wheel_num/2
                qp.rotate(rot)
                qp.drawEllipse(QPointF(0,-arc_size/2-arc_dist/2), arc_dist/2*wheel_size, arc_dist/2*wheel_size)
                qp.rotate(-rot)
            
            arrow_angle = int(self.arrow_rot*6)
            arrow_angle %= 90
            arrow_current = table['voltage_out']
            if arrow_current != 0:
                if arrow_current > 0: arrow_up = True
                else: arrow_up = False
                qp.save()
                qp.setBrush(foreground_colour)
                qp.setPen(Qt.PenStyle.NoPen)
                tri_size = 35
                if arrow_up: qp.rotate(-90+arrow_angle)
                else: qp.rotate(-arrow_angle)
                qp.translate(0,-arc_size/2-arc_dist*2)
                if arrow_up: qp.drawPolygon([QPointF(-1,-tri_size/2),QPointF(-1,tri_size/2),QPointF(tri_size-1,0)])
                else: qp.drawPolygon([QPointF(-1,-tri_size/2),QPointF(-1,tri_size/2),QPointF(-tri_size-1,0)])
                
                qp.restore()
            qp.translate(0, -(arc_size/2+arc_dist/2))
            if arrow_current != 0:
                if arrow_up: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), -arc_angle*2, -arrow_angle*16)
                else: qp.drawArc(QRectF(-arc_size/2-arc_dist*2, -arc_dist*1.5, arc_size+arc_dist*4, arc_size+arc_dist*4), arc_angle*2-1440, arrow_angle*16)
            
            qp.rotate(-arc_rot)
            qp.translate(-arc_cen[0], -(arc_pos[1]-arc_dist/2))

            #Draw State/Action
            font = QFont()
            font.setPointSize(60)
            qp.setFont(font)
            qp.save()
            qp.translate(0,-200)
            font.setPointSize(80)
            qp.setFont(font)

            qp.setBrush(Qt.BrushStyle.NoBrush)

            qp.drawRect(QRectF(-415,285,530,130))

            action_text = "Algae Pickup"
            state_text = "Coral VA"

            qp.drawText(-380,377, action_text)
            font.setPointSizeF(70)
            qp.setFont(font)
            qp.drawText(-380,500, state_text)


            # Draw Bay
            qp.restore()
            qp.translate(125,-125)
            qp.drawPolyline([QPointF(-100,0), QPointF(-50,125), QPointF(50,125), QPointF(100,0)])
            qp.setPen(QPen(colour_chart[4], 8, Qt.PenStyle.DotLine))
            qp.drawLine(QLineF(-75,100,75,100))
            
            qp.setPen(QPen(foreground_colour, 25))
            if table['present']: qp.drawEllipse(QPointF(0,25),50,50)

            bay_num = round(table['distance'])

            qp.drawText(125,75, str(bay_num)+"mm")
        
        else:
            qp.setPen(foreground_colour)
            font = QFont()
            font.setPointSizeF(16)
            qp.setFont(font)
            text = "NetworkTable not connected"
            font_metrics = QFontMetrics(font)
            text_width = font_metrics.horizontalAdvance(text)/2
            text_height = font_metrics.height()
            qp.drawText(QPointF(cw-text_width, ch+text_height/4), text)
            self.setMinimumHeight(text_height)

    def closeEvent(self, e):
        closeEvent(self, e)