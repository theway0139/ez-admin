import { ref } from 'vue';

// 报警项接口
export interface AlertItem {
  id: number;
  type: string;
  description: string;
  location: string;
  time: string;
  level: string;
  status: string;
  image?: string;
  videoUrl?: string;
  imagePath?: string;
  isNew?: boolean;
  hasImage?: boolean;
  processResult?: string;
  processDescription?: string;
}

// 创建报警项的参数
interface CreateAlertParams {
  type: string;
  description: string;
  location: string;
  level: string;
  status?: string;
  image?: string;
  videoUrl?: string;
  imagePath?: string;
}

// 报警日志服务
class AlertLogService {
  private static instance: AlertLogService;
  private _alerts = ref<AlertItem[]>([]);
  private _nextId = 1;
  
  // 单例模式
  public static getInstance(): AlertLogService {
    if (!AlertLogService.instance) {
      AlertLogService.instance = new AlertLogService();
    }
    return AlertLogService.instance;
  }
  
  // 添加报警
  public addAlert(params: CreateAlertParams): AlertItem {
    const now = new Date();
    const alert: AlertItem = {
      id: this._nextId++,
      type: params.type,
      description: params.description,
      location: params.location,
      time: now.toLocaleString(),
      level: params.level,
      status: params.status || '未处理',
      image: params.image,
      videoUrl: params.videoUrl,
      imagePath: params.imagePath,
      isNew: true,
      hasImage: !!params.image || !!params.videoUrl || !!params.imagePath
    };
    
    this._alerts.value.unshift(alert);
    
    // 5秒后移除新报警标记
    setTimeout(() => {
      const index = this._alerts.value.findIndex(item => item.id === alert.id);
      if (index !== -1) {
        this._alerts.value[index].isNew = false;
      }
    }, 5000);
    
    return alert;
  }
  
  // 处理报警
  public processAlert(id: number, status: string): boolean {
    const index = this._alerts.value.findIndex(item => item.id === id);
    if (index !== -1) {
      this._alerts.value[index].status = status;
      return true;
    }
    return false;
  }
  
  // 获取报警列表
  public get alerts() {
    return this._alerts;
  }
  
  // 获取今日报警数量
  public get todayCount() {
    return ref(this._alerts.value.length);
  }
  
  // 获取待处理报警数量
  public get pendingCount() {
    return ref(this._alerts.value.filter(item => item.status === '未处理').length);
  }
  
  // 获取已处理报警数量
  public get processedCount() {
    return ref(this._alerts.value.filter(item => item.status === '已处理').length);
  }
}

// 导出单例
export const alertLogService = AlertLogService.getInstance(); 