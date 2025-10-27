# coding=utf-8
import time

from HCNetSDK import *
from PlayCtrl import *

from ctypes import Structure, c_uint32, sizeof

class NET_DVR_PTZPOS(Structure):
    _fields_ = [
        ("wPanPos",  c_uint32),   # 水平坐标 0-3600，单位 0.1°
        ("wTiltPos", c_uint32),   # 垂直坐标 0-900， 单位 0.1°
        ("wZoomPos", c_uint32),   # 变焦坐标 0-12800
    ]

class devClass:
    def __init__(self):
        self.hikSDK, self.playM4SDK = self.LoadSDK()  # 加载sdk库
        self.iUserID = -1  # 登录句柄
        self.lRealPlayHandle = -1  # 预览句柄
        self.wincv = None  # windows环境下的参数
        self.win = None  # 预览窗口
        self.FuncDecCB = None  # 解码回调
        self.PlayCtrlPort = C_LONG(-1)  # 播放通道号
        self.basePath = ''  # 基础路径
        self.preview_file = ''  # linux预览取流保存路径
        self.funcRealDataCallBack_V30 = REALDATACALLBACK(self.RealDataCallBack_V30)  # 预览回调函数
        # self.msg_callback_func = MSGCallBack_V31(self.g_fMessageCallBack_Alarm)  # 注册回调函数实现

    def LoadSDK(self):
        hikSDK = None
        playM4SDK = None
        try:
            print("netsdkdllpath: ", netsdkdllpath)
            hikSDK = load_library(netsdkdllpath)
            playM4SDK = load_library(playM4dllpath)
        except OSError as e:
            print('动态库加载失败', e)
        return hikSDK, playM4SDK

    # 设置SDK初始化依赖库路径
    def SetSDKInitCfg(self):
        # 设置HCNetSDKCom组件库和SSL库加载路径
        if sys_platform == 'windows':
            basePath = os.getcwd().encode('gbk')
            strPath = basePath + rb'\lib'
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            print('strPath: ', strPath)
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                print('NET_DVR_SetSDKInitCfg: 2 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + rb'\libcrypto-1_1-x64.dll')):
                print('NET_DVR_SetSDKInitCfg: 3 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + rb'\libssl-1_1-x64.dll')):
                print('NET_DVR_SetSDKInitCfg: 4 Succ')
        else:
            basePath = os.getcwd().encode('utf-8')
            strPath = basePath + rb'\lib'
            sdk_ComPath = NET_DVR_LOCAL_SDK_PATH()
            sdk_ComPath.sPath = strPath
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SDK_PATH.value,
                                                 byref(sdk_ComPath)):
                print('NET_DVR_SetSDKInitCfg: 2 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_LIBEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libcrypto.so.1.1')):
                print('NET_DVR_SetSDKInitCfg: 3 Succ')
            if self.hikSDK.NET_DVR_SetSDKInitCfg(NET_SDK_INIT_CFG_TYPE.NET_SDK_INIT_CFG_SSLEAY_PATH.value,
                                                 create_string_buffer(strPath + b'/libssl.so.1.1')):
                print('NET_DVR_SetSDKInitCfg: 4 Succ')
        self.basePath = basePath
    # ==================== 1. 时间-盲控（连续转 N 秒） ====================
    def ptz_turn_left_5s(self, channel=1, speed=4):
        """水平左转 5 s 后自动停"""
        PAN_LEFT = 23
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_LEFT, 0, speed):
            print('PTZ start fail, err:', self.hikSDK.NET_DVR_GetLastError())
            return
        time.sleep(0.1)
        if not self.hikSDK.NET_DVR_PTZControlWithSpeed_Other(self.iUserID, channel, PAN_LEFT, 1, speed):
            print('PTZ stop fail, err:', self.hikSDK.NET_DVR_GetLastError())
        else:
            print('PTZ turn-left 5s done.')


    # ==================== 2. 步进-角度法（走固定步长） ====================
    def ptz_step_left_2deg(self, channel=1):
        """水平左转 2°（0.1° × 20 步）"""
        PAN_LEFT_STEP1 = 23 | 0x10          # 单步 0.1°
        for i in range(20):
            # ✅ 用带速度接口才能识别步进标志
            if not self.hikSDK.NET_DVR_PTZControl(
                    self.iUserID, channel, PAN_LEFT_STEP1, 0, 0):   # 0=开始（步进自动停）
                print('PTZ step fail, err:', self.hikSDK.NET_DVR_GetLastError())
                return
            # 步进命令执行时间极短，可不给 sleep 或 10 ms 即可
            time.sleep(0.01)
        print('PTZ step-left 2° done.')


    # ==================== 3. 绝对/相对角度法（一次到位） ====================
    def ptz_goto_relative(self, delta_pan_deg, delta_tilt_deg=0.0, channel=1):
        """
        相对当前坐标移动 delta_pan_deg 度（水平）、delta_tilt_deg 度（垂直）
        精度 0.1°，到位自动停
        """
        GET_PTZPOS  = 3282          # HCNetSDK 宏，官方已定义
        SET_PTZPOS  = 3283

        # 1. 取当前坐标
        cur = NET_DVR_PTZPOS()
        ret_len = c_uint(0)
        if not self.hikSDK.NET_DVR_GetDVRConfig(self.iUserID, channel, GET_PTZPOS, byref(cur), sizeof(cur), byref(ret_len)):
            print('Get PTZ pos fail, err:', self.hikSDK.NET_DVR_GetLastError())
            return

        # 2. 计算目标（0.1° 单位，模 360°）
        target_pan = int((cur.wPanPos / 10 + delta_pan_deg)   * 10) % 3600
        target_tilt= int((cur.wTiltPos / 10 + delta_tilt_deg) * 10)
        target_tilt = max(0, min(target_tilt, 900))   # 大多数球机垂直范围 -90~0°

        # 3. 一次转到目标
        targ = NET_DVR_PTZPOS(wPanPos=target_pan, wTiltPos=target_tilt, wZoomPos=cur.wZoomPos)
        if not self.hikSDK.NET_DVR_SetDVRConfig(self.iUserID, channel, SET_PTZPOS, byref(targ), sizeof(targ)):
            print('Set PTZ pos fail, err:', self.hikSDK.NET_DVR_GetLastError())
            return
        print(f'PTZ goto relative  H{delta_pan_deg:+.1f}° V{delta_tilt_deg:+.1f}°  done.')


    # ==================== 4. 预置点法（瞬间跳转） ====================
    def ptz_goto_preset(self, preset_idx=1, channel=1):
        """瞬间转到已保存的预置点"""
        GOTO_PRESET = 39
        if not self.hikSDK.NET_DVR_PTZPreset_Other(self.iUserID, channel, GOTO_PRESET, preset_idx):
            print('PTZ goto preset fail, err:', self.hikSDK.NET_DVR_GetLastError())
            return
        print(f'PTZ goto preset {preset_idx} done.')


    def ptz_save_preset(self, preset_idx=1, channel=1):
        """把当前位置保存为预置点"""
        SET_PRESET = 8
        if not self.hikSDK.NET_DVR_PTZPreset_Other(self.iUserID, channel, SET_PRESET, preset_idx):
            print('PTZ save preset fail, err:', self.hikSDK.NET_DVR_GetLastError())
            return
        print(f'PTZ save preset {preset_idx} done.')

    # 通用设置，日志/回调事件类型等
    def GeneralSetting(self):

        # 日志的等级（默认为0）：0-表示关闭日志，1-表示只输出ERROR错误日志，2-输出ERROR错误信息和DEBUG调试信息，3-输出ERROR错误信息、DEBUG调试信息和INFO普通信息等所有信息
        # self.hikSDK.NET_DVR_SetLogToFile(3, b'./SdkLog_Python/', False)
        self.hikSDK.NET_DVR_SetLogToFile(3, bytes('./SdkLog_Python/', encoding="utf-8"), False)

    # 登录设备
    def LoginDev(self, ip, username, pwd):
        # 登录参数，包括设备地址、登录用户、密码等
        struLoginInfo = NET_DVR_USER_LOGIN_INFO()
        struLoginInfo.bUseAsynLogin = 0  # 同步登录方式
        struLoginInfo.sDeviceAddress = ip  # 设备IP地址
        struLoginInfo.wPort = 9000  # 设备服务端口
        struLoginInfo.sUserName = username  # 设备登录用户名
        struLoginInfo.sPassword = pwd  # 设备登录密码
        struLoginInfo.byLoginMode = 0

        # 设备信息, 输出参数
        struDeviceInfoV40 = NET_DVR_DEVICEINFO_V40()

        self.iUserID = self.hikSDK.NET_DVR_Login_V40(byref(struLoginInfo), byref(struDeviceInfoV40))
        if self.iUserID < 0:
            print("Login failed, error code: %d" % self.hikSDK.NET_DVR_GetLastError())
            self.hikSDK.NET_DVR_Cleanup()
        else:
            print('登录成功，设备序列号：%s' % str(struDeviceInfoV40.struDeviceV30.sSerialNumber, encoding="utf8").rstrip('\x00'))

    # 登出设备
    def LogoutDev(self):
        if self.iUserID > -1:
            # 撤销布防，退出程序时调用
            self.hikSDK.NET_DVR_Logout(self.iUserID)

    def DecCBFun(self, nPort, pBuf, nSize, pFrameInfo, nUser, nReserved2):
        # 解码回调函数
        if pFrameInfo.contents.nType == 3:
            # 解码返回视频YUV数据，将YUV数据转成jpg图片保存到本地
            # 如果有耗时处理，需要将解码数据拷贝到回调函数外面的其他线程里面处理，避免阻塞回调导致解码丢帧
            sFileName = ('./pic/test_stamp[%d].jpg' % pFrameInfo.contents.nStamp)
            nWidth = pFrameInfo.contents.nWidth
            nHeight = pFrameInfo.contents.nHeight
            nType = pFrameInfo.contents.nType
            dwFrameNum = pFrameInfo.contents.dwFrameNum
            nStamp = pFrameInfo.contents.nStamp
            print(nWidth, nHeight, nType, dwFrameNum, nStamp, sFileName)

            lRet = self.playM4SDK.PlayM4_ConvertToJpegFile(pBuf, nSize, nWidth, nHeight, nType,
                                                           c_char_p(sFileName.encode()))
            if lRet == 0:
                print('PlayM4_ConvertToJpegFile fail, error code is:', self.playM4SDK.PlayM4_GetLastError(nPort))
            else:
                print('PlayM4_ConvertToJpegFile success')

    # 将视频流保存到本地
    def writeFile(self, filePath, pBuffer, dwBufSize):
        # 使用memmove函数将指针数据读到数组中
        data_array = (c_byte * dwBufSize)()
        memmove(data_array, pBuffer, dwBufSize)

        # 判断文件路径是否存在
        if not os.path.exists(filePath):
            # 如果不存在，使用 open() 函数创建一个空文件
            open(filePath, "w").close()

        preview_file_output = open(filePath, 'ab')
        preview_file_output.write(data_array)
        preview_file_output.close()

    def RealDataCallBack_V30(self, lPlayHandle, dwDataType, pBuffer, dwBufSize, pUser):
        # 码流回调函数
        if sys_platform == 'linux':
            # 码流回调函数
            if dwDataType == NET_DVR_SYSHEAD:
                from datetime import datetime
                # 获取当前时间的datetime对象
                current_time = datetime.now()
                timestamp_str = current_time.strftime('%Y%m%d_%H%M%S')
                self.preview_file = f'./previewVideo{timestamp_str}.mp4'
            elif dwDataType == NET_DVR_STREAMDATA:
                self.writeFile(self.preview_file, pBuffer, dwBufSize)
            else:
                print(u'其他数据,长度:', dwBufSize)
        elif sys_platform == 'windows':
            if dwDataType == NET_DVR_SYSHEAD:
                # 设置流播放模式
                self.playM4SDK.PlayM4_SetStreamOpenMode(self.PlayCtrlPort, 0)
                # 打开码流，送入40字节系统头数据
                if self.playM4SDK.PlayM4_OpenStream(self.PlayCtrlPort, pBuffer, dwBufSize, 1024 * 1024):
                    # 设置解码回调，可以返回解码后YUV视频数据
                    self.FuncDecCB = DECCBFUNWIN(self.DecCBFun)
                    self.playM4SDK.PlayM4_SetDecCallBackExMend(self.PlayCtrlPort, self.FuncDecCB, None, 0, None)
                    # 开始解码播放
                    if self.playM4SDK.PlayM4_Play(self.PlayCtrlPort, self.wincv.winfo_id()):
                        print(u'播放库播放成功')
                    else:
                        print(u'播放库播放失败')
                else:
                    print(f'播放库打开流失败, 错误码：{self.playM4SDK.PlayM4_GetLastError(self.PlayCtrlPort)}')
            elif dwDataType == NET_DVR_STREAMDATA:
                self.playM4SDK.PlayM4_InputData(self.PlayCtrlPort, pBuffer, dwBufSize)
            else:
                print(u'其他数据,长度:', dwBufSize)

    def startPlay(self, playTime):
        # 获取一个播放句柄
        if not self.playM4SDK.PlayM4_GetPort(byref(self.PlayCtrlPort)):
            print(f'获取播放库句柄失败, 错误码：{self.playM4SDK.PlayM4_GetLastError(self.PlayCtrlPort)}')

        if sys_platform == 'linux':
            # 开始预览
            preview_info = NET_DVR_PREVIEWINFO()
            preview_info.hPlayWnd = 0
            preview_info.lChannel = 1  # 通道号
            preview_info.dwStreamType = 0  # 主码流
            preview_info.dwLinkMode = 0  # TCP
            preview_info.bBlocked = 1  # 阻塞取流

            # 开始预览并且设置回调函数回调获取实时流数据
            self.lRealPlayHandle = self.hikSDK.NET_DVR_RealPlay_V40(self.iUserID, byref(preview_info),
                                                                    self.funcRealDataCallBack_V30,
                                                                    None)
            if self.lRealPlayHandle < 0:
                print('Open preview fail, error code is: %d' % self.hikSDK.NET_DVR_GetLastError())
                # 登出设备
                self.hikSDK.NET_DVR_Logout(self.iUserID)
                # 释放资源
                self.hikSDK.NET_DVR_Cleanup()
                exit()
            time.sleep(playTime)

        elif sys_platform == 'windows':
            import tkinter
            from tkinter import Button

            # 创建窗口
            self.win = tkinter.Tk()
            # 固定窗口大小
            self.win.resizable(0, 0)
            self.win.overrideredirect(True)

            sw = self.win.winfo_screenwidth()
            # 得到屏幕宽度
            sh = self.win.winfo_screenheight()
            # 得到屏幕高度

            # 窗口宽高
            ww = 512
            wh = 384
            x = (sw - ww) / 2
            y = (sh - wh) / 2
            self.win.geometry("%dx%d+%d+%d" % (ww, wh, x, y))

            # 创建退出按键
            b = Button(self.win, text='退出', command=self.win.quit)
            b.pack()
            # 创建一个Canvas，设置其背景色为白色
            self.wincv = tkinter.Canvas(self.win, bg='white', width=ww, height=wh)
            self.wincv.pack()

            # 开始预览
            preview_info = NET_DVR_PREVIEWINFO()
            preview_info.hPlayWnd = 0
            preview_info.lChannel = 1  # 通道号
            preview_info.dwStreamType = 0  # 主码流
            preview_info.dwLinkMode = 0  # TCP
            preview_info.bBlocked = 1  # 阻塞取流

            # 开始预览并且设置回调函数回调获取实时流数据
            self.lRealPlayHandle = self.hikSDK.NET_DVR_RealPlay_V40(self.iUserID, byref(preview_info),
                                                                    self.funcRealDataCallBack_V30,
                                                                    None)
            if self.lRealPlayHandle < 0:
                print('Open preview fail, error code is: %d' % self.hikSDK.NET_DVR_GetLastError())
                # 登出设备
                self.hikSDK.NET_DVR_Logout(self.iUserID)
                # 释放资源
                self.hikSDK.NET_DVR_Cleanup()
                exit()

            # show Windows
            self.win.mainloop()

    def stopPlay(self):
        # 关闭预览
        self.hikSDK.NET_DVR_StopRealPlay(self.lRealPlayHandle)

        # 停止解码，释放播放库资源
        if self.PlayCtrlPort.value > -1:
            self.playM4SDK.PlayM4_Stop(self.PlayCtrlPort)
            self.playM4SDK.PlayM4_CloseStream(self.PlayCtrlPort)
            self.playM4SDK.PlayM4_FreePort(self.PlayCtrlPort)
            self.PlayCtrlPort = C_LONG(-1)


if __name__ == '__main__':
    dev = devClass()
    dev.SetSDKInitCfg()  # 设置SDK初始化依赖库路径
    dev.hikSDK.NET_DVR_Init()  # 初始化sdk
    dev.GeneralSetting()  # 通用设置，日志，回调函数等
    dev.LoginDev(ip=b'192.168.1.64', username=b"admin", pwd=b"okwy1234")  # 登录设备

    dev.ptz_turn_left_5s()          # 1. 老办法，转 5 秒
    # dev.ptz_step_left_2deg()        # 2. 走 2° 步进
    # dev.ptz_goto_relative(-30, 0)  # 3. 相对左转 30°（到位自动停）
    # dev.ptz_save_preset(1)          # 4. 把当前点记为预置点 1
    

    dev.startPlay(playTime=5)  # playTime用于linux环境控制预览时长，windows环境无效
    dev.stopPlay()
    # dev.ptz_goto_preset(1)          #    瞬间回该点
    dev.LogoutDev()
    # 释放资源
    dev.hikSDK.NET_DVR_Cleanup()
