
__author__ = 'rykov'
from PySide import QtCore, QtGui
import Transportable
import Stationary
import sys
import RK4_2
from multiprocessing import Process, freeze_support
import PlotGraph
import UDP
import UDP_KSU_TS
import Serial
import AdvantechWithWrapper as Advantech
import SetBit
import LSU
import MultiprocessingParams as MP
import Config as Cfg

freeze_support()


class Main(QtGui.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.stationary = Cfg.params.stationary
        self.stationary_mode = Cfg.params.stationary_mode
        if self.stationary:
            self.ui = Stationary.Ui_MainWindow()
        else:
            self.ui = Transportable.Ui_MainWindow()
        self.ui.setupUi(self)

        if self.stationary and self.stationary_mode == Cfg.mode_enum.mode_1:
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabEnabled(3, False)

        if not self.stationary:
            group = QtGui.QButtonGroup(self)
            group.addButton(self.ui.bool_39, 1)
            group.addButton(self.ui.bool_40, 2)

            group_2 = QtGui.QButtonGroup(self)
            group_2.addButton(self.ui.bool_22, 1)
            group_2.addButton(self.ui.bool_23, 2)
            group_2.addButton(self.ui.bool_24, 3)

        self.commands_array = [False]*48
        self.ksu_array = [False]*8
        self.ksu_array[0] = True
        self.ksu_array[3] = True
        self.lsu_array = [False]*8
        self.lsu_2_array = [False]*8
        self.ks_array = [False]*8
        self.faults_array = [False]*8
        self.fc_state_array = [False]*8
        self.fc_2_state_array = [False]*8
        self.im_mask_array = [True]*16

        # self.ui.frame_lsu_2_role.setVisible(False)
        # self.ui.groupBox_lsu_2.setVisible(False)
        # self.ui.fc_2_state.setVisible(False)
        self.ui.frame_6.setVisible(False)
        if not self.stationary:
            self.ui.frame_14.setVisible(False)
            self.ui.frame_16.setVisible(False)
            self.ui.frame_20.setVisible(False)
        self.ui.reset.setVisible(False)
        self.ui.imitate.setVisible(False)

        self.lsu = LSU.LSU()
        if not Cfg.params.stationary or Cfg.params.stationary_mode == Cfg.mode_enum.mode_3:
            self.lsu.start()

        self.show()

        colors = [QtCore.Qt.black,
                  QtCore.Qt.red,
                  QtCore.Qt.blue,
                  QtCore.Qt.magenta,
                  QtCore.Qt.darkYellow,
                  QtCore.Qt.green,
                  QtCore.Qt.cyan,
                  QtCore.Qt.darkGray]

        names = [u"КР1",
                 u"КР2",
                 u"КТ1",
                 u"КТ2",
                 u"РТВ",
                 u"ЧВ ТГ",
                 u"ДП",
                 u"ЧВ ЭЦН"]

        y_names = [u'Положение клапанов, мм',
                   u'Положение РТВ, мм',
                   u'Частота вращения ТГ, об/мин',
                   u'Давление пара перед АТГУ, МПа',
                   u'Частота вращения ЭЦН, об/мин']

        y_scales_min = [0,
                        0,
                        0,
                        0,
                        0]

        y_scales_max = [30,
                        62,
                        10000,
                        3,
                        1000]

        formats = ['{:.3f}',
                   '{:.3f}',
                   '{:.3f}',
                   '{:.3f}',
                   '{:.3f}']

        axes = [0, 0, 0, 0, 1, 2, 3, 4]
        trends = []
        trends_lsu2 = []
        for color, name, axis in zip(colors, names, axes):
            trends.append({'color': color, 'name': name, 'axis': axis})
            trends_lsu2.append({'color': color, 'name': name, 'axis': axis})

        axes = []
        axes_lsu2 = []
        for name, y_scale_max, y_scale_min, y_format in zip(y_names, y_scales_max, y_scales_min, formats):
            axes.append({'scale': (y_scale_min, y_scale_max), 'name': name, 'format': y_format})
            axes_lsu2.append({'scale': (y_scale_min, y_scale_max), 'name': name, 'format': y_format})

        self.ui.graph.config(trends, axes, x_axis={'name': u'Время', 'format': '{:.2f}'}, trend_limit=2000)
        if self.stationary:
            self.ui.graph_lsu2.config(trends_lsu2, axes_lsu2, x_axis={'name': u'Время', 'format': '{:.2f}'}, trend_limit=2000)
            self.ui.pushButton_2.clicked.connect(self.stop_graph_2)

        self.ui.pushButton.clicked.connect(self.stop_graph)

        if self.stationary:
            for child in self.ui.valves_3.children() + self.ui.valves_4.children() + self.ui.valves_11.children() + self.ui.valves_12.children() + \
                    self.ui.valves_15.children() + self.ui.valves_16.children() + self.ui.valves_13.children() + self.ui.valves_14.children():
                if isinstance(child, QtGui.QCheckBox):
                    child.clicked.connect(self.imitate_params)
                elif isinstance(child, QtGui.QDoubleSpinBox):
                    child.valueChanged.connect(self.imitate_params)
            # self.ui.f1_im.clicked.connect(self.imitate_params)

        if not self.stationary:
            for b in self.ui.commands.children():
                if isinstance(b, QtGui.QPushButton):
                    if b.isCheckable():
                        b.clicked.connect(self.make_commands)
                    else:
                        b.pressed.connect(self.make_commands_true)
                        b.released.connect(self.make_commands_false)

        if not self.stationary:
            for b in self.ui.discrete_ksu.children():
                b.clicked.connect(self.make_ksu)

        for b in self.ui.discrete_lsu.children():
            b.clicked.connect(self.make_lsu)

        if self.stationary:
            for b in self.ui.discrete_lsu_2.children():
                b.clicked.connect(self.make_lsu_2)

        if not self.stationary:
            for b in self.ui.discrete_ks.children():
                b.clicked.connect(self.make_ks)

        for b in self.ui.discrete_faults.children():
            b.clicked.connect(self.make_faults)

        for b in self.ui.fc_state.children():
            b.clicked.connect(self.make_fc_state)

        if self.stationary:
            for b in self.ui.fc_2_state.children():
                b.clicked.connect(self.make_fc_2_state)

        if not self.stationary:
            for b in self.ui.im_mask.children():
                b.clicked.connect(self.make_im_mask)

        MP.mp()
        self.pu_struct = MP.pu_struct
        self.atgu_1 = MP.atgu_1
        self.atgu_2 = MP.atgu_2
        self.controls = MP.controls
        self.im_params = MP.im_params
        self.lsu_params = MP.lsu_params
        self.im_queue = MP.im_queue
        self.flag = MP.flag
        self.queue_plot = MP.queue_plot
        self.queue_adv = MP.queue_adv
        # self.adv_data = MP.

        self.ui.qr_in.valueChanged.connect(self.set_qr_in)
        self.ui.we_in.valueChanged.connect(self.set_we_in)
        self.ui.t_cool_in.valueChanged.connect(self.set_t_in)
        self.ui.t_hot_in.valueChanged.connect(self.set_t_in)

        if self.stationary:
            self.ui.qr_in_2.valueChanged.connect(self.set_qr_in)
            self.ui.we_in_2.valueChanged.connect(self.set_we_in)
            self.ui.t_cool_in_2.valueChanged.connect(self.set_t_in)
            self.ui.t_hot_in_2.valueChanged.connect(self.set_t_in)

        self.ui.freq_in.valueChanged.connect(self.set_freq_in)
        self.ui.mode.valueChanged.connect(self.set_mode)
        self.ui.dp_final.currentIndexChanged.connect(self.set_dp_final)
        self.ui.period.valueChanged.connect(self.set_period)
        self.ui.reset.clicked.connect(self.reset)
        self.ui.imitate.clicked.connect(lambda: self.imitate(self.ui.imitate.isChecked()))

        self.ui.qr_in.setValue(Cfg.params.power)
        self.ui.we_in.setValue(Cfg.params.electric_power)
        self.ui.t_cool_in.setValue(Cfg.params.cool_water_temperature)
        self.ui.t_hot_in.setValue(Cfg.params.hot_water_temperature)
        self.ui.p2_in.setValue(Cfg.params.atgu_pressure)
        self.ui.p8_in.setValue(Cfg.params.condenser_pressure)

        if not self.stationary:
            self.ui.kr1_2_set.valueChanged.connect(self.set_pp_2)
            self.ui.kr2_2_set.valueChanged.connect(self.set_pp_2)
            self.ui.kt1_2_set.valueChanged.connect(self.set_pp_2)
            self.ui.kt2_2_set.valueChanged.connect(self.set_pp_2)
            self.ui.rtv_2_set.valueChanged.connect(self.set_pp_2)

        self.model_process = Process(target=RK4_2.run,
                                     args=(self.queue_plot, self.flag, self.controls, self.im_params, self.atgu_1, self.atgu_2))
        self.model_process.start()

        self.plot_thread = QtCore.QThread()
        if self.stationary:
            self.plot = PlotGraph.Plot(self.ui.graph, self.ui.graph_lsu2)
        else:
            self.plot = PlotGraph.Plot(self.ui.graph)
        self.plot.moveToThread(self.plot_thread)
        self.plot_thread.started.connect(self.plot.run)
        self.plot.signal.connect(self.plot_add_points)
        self.plot_thread.start()

        if self.stationary:
            self.serial_process = Process(target=Serial.run,
                                          args=(self.atgu_1, self.atgu_2, self.lsu_params, self.flag))
            self.serial_process.start()
            self.adv_process = Process(target=Advantech.run,
                                       args=(self.flag, self.atgu_1, self.atgu_2, self.queue_adv, self.im_params))
            self.adv_process.start()
            self.udp_ksu_ts_process = Process(target=UDP_KSU_TS.run,
                                              args=[self.im_params, self.flag])
            self.udp_ksu_ts_process.start()
        else:
            self.udp_process = Process(target=UDP.run,
                                       args=(self.atgu_1, self.im_params, self.pu_struct, self.lsu_params, self.im_queue, self.flag))
            self.udp_process.start()

        self.t_ind = QtCore.QTimer()
        self.t_ind.timeout.connect(self.update_inds)
        self.t_ind.start(100)

        self.lsu_update = QtCore.QTimer()
        self.lsu_update.timeout.connect(self.update_lsu)
        self.lsu_update.start(10)

    @QtCore.Slot(list)
    def plot_add_points(self, data):
        if not self.ui.pushButton.isChecked():
            self.ui.graph.add_points(*data[:9])
        if Cfg.params.stationary:
            if not self.ui.pushButton_2.isChecked():
                self.ui.graph_lsu2.add_points(data[0], *data[9:])

    def set_adv_queue(self):
        self.queue_adv.put((0, self.ui.qr_in.value()))

    def update_lsu(self):
        self.lsu.version_set = self.lsu_params['version_set']
        self.lsu.metrics_set = self.lsu_params['metrics_set']
        self.lsu.state_word_set = self.lsu_params['state_word_set']
        self.lsu.dp_final_set = self.lsu_params['dp_final_set']
        self.lsu.dp_set = self.lsu_params['dp_set']
        self.lsu.faults = self.im_params['faults']
        self.lsu.mode = self.im_params['mode']
        self.lsu.dp_gui = self.im_params['dp_final']
        self.lsu_params['version'] = self.lsu.version
        self.lsu_params['metrics'] = self.lsu.metrics
        self.lsu_params['state_word'] = self.lsu.state_word
        self.lsu_params['dp_final'] = self.lsu.dp_final
        self.lsu_params['dp'] = self.lsu.dp
        self.im_params['role'] = self.lsu.role

    def reset(self):
        self.controls['reset_flag'] = 1

    def imitate(self, state):
        self.im_params['imitation'] = int(state)
        self.im_queue.put(state)

    def set_qr_in(self):
        sender = self.sender()
        value = sender.value()
        if sender.objectName() == 'qr_in':
            self.ui.qr_in_2.setValue(value)
        else:
            self.ui.qr_in.setValue(value)
        self.controls['qr_in'] = value / 100.0 * 250.0

    def set_we_in(self):
        sender = self.sender()
        self.controls[sender.objectName()] = sender.value() / 100.0 * 25.0

    def set_t_in(self):
        sender = self.sender()
        self.controls[sender.objectName()] = sender.value()

    def set_freq_in(self):
        self.im_params['freq_in'] = self.ui.freq_in.value()

    def set_pp_2(self):
        sender = self.sender()
        self.pu_struct[sender.objectName()] = sender.value()

    def set_mode(self):
        self.im_params['mode'] = self.ui.mode.value()
        # self.lsu.mode = self.im_params['mode']

    def set_dp_final(self):
        self.im_params['dp_final'] = float(self.ui.dp_final.currentText())
        # self.lsu.dp_gui = self.im_params['dp_final']

    def set_period(self):
        self.im_params['period'] = self.ui.period.value()

    def imitate_params(self):
        sender = self.sender()
        if isinstance(sender, QtGui.QCheckBox):
            l = sender.objectName().split('_')
            if len(l) == 2:
                name, sub_name = l
                self.atgu_1[name][sub_name] = sender.isChecked()
            elif len(l) == 3:
                if self.stationary_mode == Cfg.mode_enum.mode_1:
                    name, chanel, sub_name = l
                    self.atgu_2[name][sub_name] = sender.isChecked()
        elif isinstance(sender, QtGui.QDoubleSpinBox):
            l = sender.objectName().split('_')
            if len(l) == 3:
                name, sub_name_1, sub_name_2 = l
                self.atgu_1[name][sub_name_1+'_'+sub_name_2] = sender.value()
            elif len(l) == 4:
                if self.stationary_mode == Cfg.mode_enum.mode_1:
                    name, chanel, sub_name_1, sub_name_2 = l
                    self.atgu_2[name][sub_name_1+'_'+sub_name_2] = sender.value()

    def make_commands(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('bool_')[1])
            self.commands_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.commands_array)
            self.im_params['commands'] = c
            # print c
        except Exception, e:
            print e

    def make_commands_true(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('bool_')[1])
            self.commands_array[index] = True
            c = SetBit.bits_to_bytes_array(self.commands_array)
            self.im_params['commands'] = c
            # print c
        except Exception, e:
            print e

    def make_commands_false(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('bool_')[1])
            self.commands_array[index] = False
            c = SetBit.bits_to_bytes_array(self.commands_array)
            self.im_params['commands'] = c
            # print c
        except Exception, e:
            print e

    def make_ksu(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('ksu_')[1])
            self.ksu_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.ksu_array)
            self.im_params['ksu'] = c[0]
        except Exception, e:
            print e

    def make_lsu(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('lsu_')[1])
            self.lsu_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.lsu_array)
            self.im_params['lsu'] = c[0]
        except Exception, e:
            print e

    def make_lsu_2(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('lsu_2_')[1])
            self.lsu_2_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.lsu_2_array)
            self.im_params['lsu_2'] = c[0]
        except Exception, e:
            print e

    def make_ks(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('ks_')[1])
            self.ks_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.ks_array)
            self.im_params['ks'] = c[0]
        except Exception, e:
            print e

    def make_faults(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('fault_')[1])
            self.faults_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.faults_array)
            self.im_params['faults'] = c[0]
            # self.lsu.faults = self.im_params['faults']
        except Exception, e:
            print e

    def make_fc_state(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('fc_state_')[1])
            self.fc_state_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.fc_state_array)
            state = self.atgu_1['fc_state'].value
            state_right = state & 16
            self.atgu_1['fc_state'].value = c[0] + state_right
        except Exception, e:
            print e

    def make_fc_2_state(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('fc_2_state_')[1])
            self.fc_2_state_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.fc_2_state_array)
            state = self.atgu_2['fc_state'].value
            state_right = state & 16
            self.atgu_2['fc_state'].value = c[0] + state_right
        except Exception, e:
            print e

    def make_im_mask(self):
        sender = self.sender()
        try:
            index = int(sender.objectName().split('mask_')[1])
            self.im_mask_array[index] = sender.isChecked()
            c = SetBit.bits_to_bytes_array(self.im_mask_array)
            self.im_params['im_mask'] = c
        except Exception, e:
            print e

    def update_inds(self):
        self.ui.kr1.setValue(self.atgu_1['kr1']['value'])
        self.ui.kr2.setValue(self.atgu_1['kr2']['value'])
        self.ui.kt1.setValue(self.atgu_1['kt1']['value'])
        self.ui.kt2.setValue(self.atgu_1['kt2']['value'])
        self.ui.rtv.setValue(self.atgu_1['rtv']['value'])
        self.ui.f1.setValue(self.atgu_1['f1']['value'])
        self.ui.fc.setValue(self.atgu_1['fc']['value'])
        self.ui.dp1.setValue(self.atgu_1['dp1']['value'])
        self.ui.p8.setValue(self.atgu_1['p8']['value'])
        self.ui.we.setValue(self.atgu_1['we']['value'])
        self.ui.T8.setValue(self.atgu_1['T8']['value'])
        if self.stationary:
            self.ui.dp2.setValue(self.atgu_1['dp2']['value'])
            self.ui.f2.setValue(self.atgu_1['f2']['value'])
            self.ui.f1_ch2.setValue(self.atgu_1['f1']['value'])
            self.ui.f2_ch2.setValue(self.atgu_1['f2']['value'])
            self.ui.dp1_ch2.setValue(self.atgu_1['dp1']['value'])
            self.ui.dp2_ch2.setValue(self.atgu_1['dp2']['value'])
            self.ui.p8_ch2.setValue(self.atgu_1['p8']['value'])
            self.ui.T8_ch2.setValue(self.atgu_1['T8']['value'])
            if self.stationary_mode != Cfg.mode_enum.mode_1:
                # two ATGU
                self.ui.kr1_lsu2.setValue(self.atgu_2['kr1']['value'])
                self.ui.kr2_lsu2.setValue(self.atgu_2['kr2']['value'])
                self.ui.kt1_lsu2.setValue(self.atgu_2['kt1']['value'])
                self.ui.kt2_lsu2.setValue(self.atgu_2['kt2']['value'])
                self.ui.rtv_lsu2.setValue(self.atgu_2['rtv']['value'])
                self.ui.f1_lsu2.setValue(self.atgu_2['f1']['value'])
                self.ui.f2_lsu2.setValue(self.atgu_2['f2']['value'])
                self.ui.fc_lsu2.setValue(self.atgu_2['fc']['value'])
                self.ui.dp1_lsu2.setValue(self.atgu_2['dp1']['value'])
                self.ui.dp2_lsu2.setValue(self.atgu_2['dp2']['value'])
                self.ui.p8_lsu2.setValue(self.atgu_2['p8']['value'])
                self.ui.we_lsu2.setValue(self.atgu_2['we']['value'])
                self.ui.T8_lsu2.setValue(self.atgu_2['T8']['value'])
        else:
            self.ui.kr1_set.setValue(self.atgu_1['kr1_set'].value)
            self.ui.kr2_set.setValue(self.atgu_1['kr2_set'].value)
            self.ui.kt1_set.setValue(self.atgu_1['kt1_set'].value)
            self.ui.kt2_set.setValue(self.atgu_1['kt2_set'].value)
            self.ui.rtv_set.setValue(self.atgu_1['rtv_set'].value)
            self.ui.fc_set.setValue(self.atgu_1['fc_set'].value)

            self.ui.role.setText(Cfg.role[self.im_params['role']])

            self.ui.freq_mode.setText(Cfg.f_mode[self.pu_struct['rot_freq_mode']])
            self.ui.freq_target.setValue(self.pu_struct['rot_freq_set'])
            self.ui.freq_setpoint.setValue(self.pu_struct['rot_freq_setpoint'])
            self.ui.We.setValue(self.pu_struct['rot_freq_We'])
            self.ui.freq_sign_0.setChecked(bool(self.pu_struct['rot_freq_signs'] & 1))
            self.ui.freq_sign_1.setChecked(bool(self.pu_struct['rot_freq_signs'] & 2))
            self.ui.freq_sign_2.setChecked(bool(self.pu_struct['rot_freq_signs'] & 4))

            self.ui.dp_mode.setText(Cfg.mode[self.pu_struct['dp_mode']])
            self.ui.p2_setpoint.setValue(self.pu_struct['dp_p_set'])
            self.ui.p2_setpoint_final.setValue(self.pu_struct['dp_set_final'])

            self.ui.dpk_mode.setText(Cfg.mode[self.pu_struct['dpk_mode']])
            self.ui.p8_setpoint.setValue(self.pu_struct['dpk_p_set'])
            self.ui.p8_setpoint_final.setValue(self.pu_struct['dpk_p_set_final'])

            self.ui.rtv_mode.setText(Cfg.mode[self.pu_struct['rtv_mode']])
            self.ui.t_setpoint.setValue(self.pu_struct['rtv_t_set'])

            s = self.lsu_params['state_word_set']
            self.ui.role_set.setText(Cfg.role[(s & 128) >> 7])
            self.ui.mode_set.setText(Cfg.mode[(s & 64) >> 6])
            self.ui.dp_final_set.setValue(self.lsu_params['dp_final_set'])
            self.ui.dp_set.setValue(self.lsu_params['dp_set'])

    def stop_graph(self):
        self.plot.flag = not self.ui.pushButton.isChecked()

    def stop_graph_2(self):
        self.plot.flag_2 = not self.ui.pushButton_2.isChecked()

    def closeEvent(self, *args, **kwargs):
        self.flag.value = 0
        self.t_ind.stop()
        self.lsu_update.stop()
        self.ui.graph.stop()
        if self.stationary:
            self.ui.graph_lsu2.stop()
            # self.queue_adv.put(None)
            # self.queue_adv.close()
            self.serial_process.join()
            self.adv_process.join()
            self.udp_ksu_ts_process.join()
        else:
            self.udp_process.join()
        self.plot_thread.exit(0)
        self.plot_thread.wait()
        self.model_process.join()
        self.lsu.flag = False
        MP.shutdown()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = Main()
    myapp.show()
    sys.exit(app.exec_())
