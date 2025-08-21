<template>
  <a-modal
    v-model:visible="visible"
    :title="null"
    :width="700"
    :footer="null"
    :maskClosable="false"
    :closable="false"
    :bodyStyle="{ padding: '0' }"
    class="alert-process-modal"
    destroyOnClose
  >
    <div class="alert-process-header">
      <div class="header-icon pulse-animation">
        <warning-outlined />
      </div>
      <div class="header-title">报警处理</div>
      <div class="header-close" @click="handleCancel">
        <close-outlined />
      </div>
    </div>
    
    <div class="alert-process-container">
      <div class="alert-main-content">
        <!-- 左侧：图像/视频区域和报警信息 -->
        <div class="alert-left-section">
          <!-- 视频/图片区域 -->
          <div class="alert-media-container">
            <!-- 视频播放区域 -->
            <div v-if="alertData.videoUrl" class="video-wrapper">
              <video 
                ref="videoPlayer" 
                controls 
                autoplay
                class="alert-video"
              >
                <source :src="processedVideoUrl" type="video/mp4">
                您的浏览器不支持视频播放
              </video>
              <div class="live-badge">
                <div class="live-dot"></div>
                <span>LIVE</span>
              </div>
            </div>
            <!-- 图片显示区域 -->
            <div v-else-if="alertData.image || alertData.imagePath" class="alert-image">
              <img :src="processedImageUrl" alt="报警图像" />
              <div class="live-badge">
                <div class="live-dot"></div>
                <span>LIVE</span>
              </div>
            </div>
            <!-- 无媒体显示区域 -->
            <div v-else class="alert-no-media">
              <file-image-outlined />
              <p>暂无图像</p>
            </div>
          </div>

          <!-- 报警信息部分 -->
          <div class="alert-info-section">
            <div class="section-title">
              <alert-outlined /> 报警信息
            </div>
            <div class="alert-info-grid">
              <div class="info-item">
                <div class="label">
                  <clock-circle-outlined /> 时间：
                </div>
                <div class="value">{{ alertData.time || '未知时间' }}</div>
              </div>
              <div class="info-item">
                <div class="label">
                  <environment-outlined /> 位置：
                </div>
                <div class="value">{{ alertData.location || '未知位置' }}</div>
              </div>
              <div class="info-item">
                <div class="label">
                  <tag-outlined /> 类型：
                </div>
                <div class="value danger">{{ alertData.type || '未知类型' }}</div>
              </div>
              <div class="info-item" v-if="alertData.description">
                <div class="label">
                  <info-circle-outlined /> 描述：
                </div>
                <div class="value">{{ alertData.description }}</div>
              </div>
              <div class="info-item" v-if="alertData.videoUrl">
                <div class="label">
                  <video-camera-outlined /> 视频：
                </div>
                <div class="value">
                  <a-tag color="blue">已录制报警视频</a-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：处理信息 -->
        <div class="alert-right-section">
          <div class="section-title">
            <form-outlined /> 处理信息
          </div>
          
          <div class="form-item">
            <div class="label">
              <check-circle-outlined /> 处理结果：
            </div>
            <a-select 
              v-model:value="processResult" 
              style="width: 100%"
              :options="[
                { value: '确认报警', label: '确认报警' },
                { value: '误报', label: '误报' },
                { value: '已处理', label: '已处理' },
                { value: '需进一步调查', label: '需进一步调查' }
              ]"
            />
          </div>
          
          <div class="form-item">
            <div class="label">
              <message-outlined /> 处理说明：
            </div>
            <a-textarea 
              v-model:value="processDescription" 
              placeholder="请输入处理说明..." 
              :rows="3"
              :maxLength="200"
              show-count
              class="process-textarea"
            />
          </div>
          
          <!-- 按钮 -->
          <div class="form-actions">
            <a-button @click="handleCancel" class="cancel-btn">取消</a-button>
            <a-button type="primary" @click="handleConfirm" :loading="submitting" class="confirm-btn">确认</a-button>
          </div>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, watch, PropType, computed, onMounted } from 'vue';
import { Modal, Button, Select, Input, Tag } from 'ant-design-vue';
import { 
  FileImageOutlined,
  ClockCircleOutlined,
  EnvironmentOutlined,
  AlertOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  FormOutlined,
  WarningOutlined,
  CloseOutlined,
  TagOutlined,
  MessageOutlined,
  VideoCameraOutlined
} from '@ant-design/icons-vue';

export default defineComponent({
  name: 'AlertProcessModal',
  components: {
    AModal: Modal,
    AButton: Button,
    ASelect: Select,
    ASelectOption: Select.Option,
    ATextarea: Input.TextArea,
    ATag: Tag,
    FileImageOutlined,
    ClockCircleOutlined,
    EnvironmentOutlined,
    AlertOutlined,
    InfoCircleOutlined,
    CheckCircleOutlined,
    FormOutlined,
    WarningOutlined,
    CloseOutlined,
    TagOutlined,
    MessageOutlined,
    VideoCameraOutlined
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    alertData: {
      type: Object as PropType<{
        id?: number;
        time?: string;
        type?: string;
        description?: string;
        location?: string;
        image?: string;
        videoUrl?: string;
        imagePath?: string;
      }>,
      default: () => ({})
    }
  },
  emits: ['cancel', 'confirm', 'update:visible'],
  setup(props, { emit }) {
    const processResult = ref('确认报警');
    const processDescription = ref('');
    const submitting = ref(false);
    const videoPlayer = ref<HTMLVideoElement | null>(null);

    // 处理视频URL，确保能正确访问后端API
    const processedVideoUrl = computed(() => {
      if (!props.alertData.videoUrl) return '';
      
      // 如果是相对路径，添加后端API基础URL
      if (props.alertData.videoUrl.startsWith('/api/')) {
        return `http://localhost:5001${props.alertData.videoUrl}`;
      }
      
      return props.alertData.videoUrl;
    });

    // 处理图片URL
    const processedImageUrl = computed(() => {
      // 如果有imagePath，优先使用
      if (props.alertData.imagePath && props.alertData.imagePath.startsWith('/api/')) {
        return `http://localhost:5001${props.alertData.imagePath}`;
      }
      
      // 否则使用base64图片
      if (props.alertData.image) {
        return `data:image/jpeg;base64,${props.alertData.image}`;
      }
      
      return '';
    });

    // 当弹窗打开时重置表单并初始化视频
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        processResult.value = '确认报警';
        processDescription.value = '';
        
        console.log('视频URL:', props.alertData.videoUrl);
        console.log('处理后的视频URL:', processedVideoUrl.value);
        console.log('图片URL:', processedImageUrl.value);
        
        // 如果有视频，在下一个tick后尝试播放
        if (props.alertData.videoUrl) {
          setTimeout(() => {
            if (videoPlayer.value) {
              videoPlayer.value.load();
              videoPlayer.value.play().catch(err => {
                console.error('视频播放失败:', err);
              });
            }
          }, 300);
        }
      }
    });

    // 弹窗打开后初始化视频
    onMounted(() => {
      if (props.visible && props.alertData.videoUrl && videoPlayer.value) {
        videoPlayer.value.load();
        videoPlayer.value.play().catch(err => {
          console.error('视频播放失败:', err);
        });
      }
    });

    const handleCancel = () => {
      emit('update:visible', false);
      emit('cancel');
    };

    const handleConfirm = () => {
      submitting.value = true;
      
      // 构建处理结果数据
      const result = {
        alertId: props.alertData.id,
        result: processResult.value,
        description: processDescription.value,
        videoUrl: props.alertData.videoUrl,
        imagePath: props.alertData.imagePath
      };
      
      // 模拟提交过程
      setTimeout(() => {
        submitting.value = false;
        emit('confirm', result);
        emit('update:visible', false);
      }, 500);
    };

    return {
      processResult,
      processDescription,
      submitting,
      handleCancel,
      handleConfirm,
      videoPlayer,
      processedVideoUrl,
      processedImageUrl
    };
  }
});
</script>

<style lang="less" scoped>
.alert-process-modal {
  :deep(.ant-modal-content) {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  }
}

.alert-process-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
  color: #fff;
  
  .header-icon {
    font-size: 20px;
    margin-right: 10px;
    
    &.pulse-animation {
      animation: pulse 1.5s infinite;
    }
  }
  
  .header-title {
    flex: 1;
    font-size: 16px;
    font-weight: 600;
  }
  
  .header-close {
    font-size: 16px;
    cursor: pointer;
    opacity: 0.8;
    transition: all 0.3s;
    
    &:hover {
      opacity: 1;
      transform: scale(1.1);
    }
  }
}

.alert-process-container {
  padding: 16px;
  
  .alert-main-content {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    
    @media (max-width: 768px) {
      flex-direction: column;
    }

    .alert-left-section {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .alert-right-section {
      flex: 0.5;
      display: flex;
      flex-direction: column;
      gap: 16px;

      .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        margin-top: auto;
        
        .cancel-btn {
          border-radius: 4px;
        }
        
        .confirm-btn {
          border-radius: 4px;
          background: #1890ff;
          border-color: #1890ff;
          box-shadow: 0 2px 6px rgba(24, 144, 255, 0.3);
          transition: all 0.3s;
          
          &:hover {
            background: #40a9ff;
            border-color: #40a9ff;
            box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
            transform: translateY(-1px);
          }
        }
      }
    }

    .alert-media-container {
      height: 260px;
      background-color: #f5f5f5;
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      border: 1px solid #eee;

      .video-wrapper {
        width: 100%;
        height: 100%;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        
        .alert-video {
          width: 100%;
          height: 100%;
          object-fit: contain;
          max-height: 260px;
        }
      }

      .alert-video,
      .alert-image img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        transition: transform 0.3s;
        
        &:hover {
          transform: scale(1.02);
        }
      }

      .alert-image {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .live-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: rgba(0, 0, 0, 0.5);
        padding: 2px 6px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        
        .live-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background-color: #ff4d4f;
          margin-right: 4px;
          animation: blink 1s infinite;
        }
        
        span {
          font-size: 10px;
          color: #fff;
          font-weight: 600;
          letter-spacing: 0.5px;
        }
      }

      .alert-no-media {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #bbb;
        width: 100%;
        height: 100%;

        .anticon {
          font-size: 36px;
          margin-bottom: 8px;
        }

        p {
          margin: 0;
          font-size: 14px;
        }
      }
    }

    .alert-info-section {
      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
        
        .anticon {
          margin-right: 8px;
          color: #ff4d4f;
        }
      }
      
      .alert-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;

        .info-item {
          display: flex;
          align-items: flex-start;

          .label {
            width: 60px;
            color: #666;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            font-size: 13px;
            
            .anticon {
              margin-right: 4px;
              color: #ff4d4f;
              font-size: 12px;
            }
          }

          .value {
            font-weight: 500;
            color: #333;
            word-break: break-word;
            font-size: 13px;
            
            &.danger {
              color: #ff4d4f;
              font-weight: 600;
            }
          }
        }
      }
    }

    .form-item {
      margin-bottom: 12px;

      .label {
        margin-bottom: 6px;
        font-weight: 500;
        display: flex;
        align-items: center;
        font-size: 13px;
        
        .anticon {
          margin-right: 4px;
          color: #1890ff;
          font-size: 12px;
        }
      }
      
      .process-textarea {
        border-radius: 4px;
        resize: none;
        
        &:focus {
          box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
        }
      }
    }
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes blink {
  0% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.4;
  }
}
</style> 